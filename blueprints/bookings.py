"""
Bookings blueprint for consultation bookings and payments
Handles the complete booking flow:
1. Client intake form
2. Select consultation type and date
3. Review and confirm booking
4. Process payment via Paystack
5. Confirmation email
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_mail import Message
from models import (
    Service, ConsultationType, Booking, ClientIntake, 
    AdminAvailability, db
)
from forms import ClientIntakeForm, BookingConfirmationForm
from paystack_client import PaystackClient, format_amount_for_paystack
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
from functools import wraps

bp = Blueprint('bookings', __name__, url_prefix='/book')

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/', methods=['GET', 'POST'])
def index():
    """
    Initial booking page - client intake form
    Collects basic client information and legal issue description
    """
    form = ClientIntakeForm()
    
    if form.validate_on_submit():
        try:
            # Handle file upload
            document_path = None
            if form.document_upload.data:
                file = form.document_upload.data
                if file and allowed_file(file.filename):
                    if file.content_length > MAX_FILE_SIZE:
                        flash('File size exceeds 5MB limit.', 'error')
                        return render_template('bookings/index.html', form=form)
                    
                    filename = secure_filename(f"{datetime.utcnow().timestamp()}_{file.filename}")
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    os.makedirs(upload_folder, exist_ok=True)
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    document_path = f"uploads/{filename}"
            
            # Create/save client intake
            intake = ClientIntake(
                full_name=form.full_name.data,
                email=form.email.data,
                phone=form.phone.data,
                company_name=form.company_name.data,
                cac_status=form.cac_status.data,
                issue_description=form.issue_description.data,
                document_filename=form.document_upload.data.filename if form.document_upload.data else None,
                document_path=document_path,
                document_upload_date=datetime.utcnow() if document_path else None,
                status='pending'
            )
            
            db.session.add(intake)
            db.session.commit()
            
            # Redirect to consultation type selection
            return redirect(url_for('bookings.select_consultation', intake_id=intake.id))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Intake form error: {str(e)}")
            flash('An error occurred while submitting your intake form. Please try again.', 'error')
    
    return render_template('bookings/index.html', form=form)


@bp.route('/select-consultation/<int:intake_id>')
def select_consultation(intake_id):
    """
    Step 2: Select consultation type and date
    """
    intake = ClientIntake.query.get_or_404(intake_id)
    
    # Get active consultation types
    consultation_types = ConsultationType.query.filter_by(is_active=True).order_by(
        ConsultationType.order
    ).all()
    
    # Get available time slots (next 30 days)
    available_dates = get_available_dates()
    
    return render_template('bookings/select_consultation.html',
        intake=intake,
        consultation_types=consultation_types,
        available_dates=available_dates
    )


@bp.route('/confirm/<int:intake_id>/<int:consultation_type_id>/<slot_datetime>')
def confirm_booking(intake_id, consultation_type_id, slot_datetime):
    """
    Step 3: Review and confirm booking details
    """
    intake = ClientIntake.query.get_or_404(intake_id)
    consultation_type = ConsultationType.query.get_or_404(consultation_type_id)
    
    try:
        scheduled_date = datetime.fromisoformat(slot_datetime)
    except ValueError:
        flash('Invalid date/time selected.', 'error')
        return redirect(url_for('bookings.select_consultation', intake_id=intake_id))
    
    # Generate confirmation token
    confirmation_token = Booking.generate_confirmation_token()
    
    # Store in session for confirmation
    form = BookingConfirmationForm(
        client_name=intake.full_name,
        client_email=intake.email,
        client_phone=intake.phone,
        company_name=intake.company_name,
        cac_status=intake.cac_status,
        issue_description=intake.issue_description
    )
    
    return render_template('bookings/confirm.html',
        form=form,
        intake=intake,
        consultation_type=consultation_type,
        scheduled_date=scheduled_date,
        confirmation_token=confirmation_token
    )


@bp.route('/process-payment', methods=['POST'])
def process_payment():
    """
    Step 4: Initialize Paystack payment
    """
    try:
        intake_id = request.form.get('intake_id', type=int)
        consultation_type_id = request.form.get('consultation_type_id', type=int)
        scheduled_date_str = request.form.get('scheduled_date')
        
        intake = ClientIntake.query.get_or_404(intake_id)
        consultation_type = ConsultationType.query.get_or_404(consultation_type_id)
        
        scheduled_date = datetime.fromisoformat(scheduled_date_str)
        
        # Create booking record
        reference = f"BOOK-{datetime.utcnow().timestamp()}"
        
        booking = Booking(
            client_name=intake.full_name,
            client_email=intake.email,
            client_phone=intake.phone,
            company_name=intake.company_name,
            cac_status=intake.cac_status,
            issue_description=intake.issue_description,
            service_id=1,  # Default service - should be selected in UI
            consultation_type_id=consultation_type.id,
            scheduled_date=scheduled_date,
            amount_naira=consultation_type.price_naira,
            payment_reference=reference,
            confirmation_token=Booking.generate_confirmation_token()
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Initialize Paystack payment
        paystack = PaystackClient()
        
        metadata = {
            'booking_id': booking.id,
            'consultation_type': consultation_type.name,
            'company_name': intake.company_name,
        }
        
        payment_result = paystack.initialize_transaction(
            email=intake.email,
            amount_naira=consultation_type.price_naira,
            reference=reference,
            metadata=metadata
        )
        
        if payment_result['success']:
            return jsonify({
                'success': True,
                'authorization_url': payment_result['authorization_url'],
                'booking_id': booking.id,
            })
        else:
            return jsonify({
                'success': False,
                'error': payment_result['error']
            }), 400
    
    except Exception as e:
        current_app.logger.error(f"Payment processing error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Payment processing failed. Please try again.'
        }), 500


@bp.route('/verify-payment/<payment_reference>')
def verify_payment(payment_reference):
    """
    Verify payment with Paystack and confirm booking
    """
    try:
        paystack = PaystackClient()
        verification_result = paystack.verify_transaction(payment_reference)
        
        if verification_result['success'] and verification_result['status'] == 'success':
            # Payment successful - update booking
            booking = Booking.query.filter_by(payment_reference=payment_reference).first_or_404()
            
            booking.payment_status = 'completed'
            booking.booking_status = 'confirmed'
            booking.payment_completed_at = datetime.utcnow()
            booking.email_sent = False
            
            # Update intake status
            intake = ClientIntake.query.filter_by(email=booking.client_email).first()
            if intake:
                intake.status = 'scheduled'
                intake.reviewed_at = datetime.utcnow()
            
            db.session.commit()
            
            # Send confirmation email
            send_booking_confirmation_email(booking)
            
            return render_template('bookings/success.html', booking=booking)
        else:
            flash('Payment verification failed. Please contact support.', 'error')
            return redirect(url_for('bookings.index'))
    
    except Exception as e:
        current_app.logger.error(f"Payment verification error: {str(e)}")
        flash('An error occurred during payment verification.', 'error')
        return redirect(url_for('bookings.index'))


@bp.route('/cancel')
def cancel_booking():
    """Handle cancelled/failed payment"""
    flash('Booking was cancelled. Please try again or contact support.', 'warning')
    return redirect(url_for('bookings.index'))


def get_available_dates():
    """
    Get available consultation dates from admin availability
    Returns: List of available date/time combinations
    """
    now = datetime.utcnow()
    availability_slots = []
    
    # Get availability for next 60 days
    for days_ahead in range(1, 61):
        check_date = (now + timedelta(days=days_ahead)).date()
        
        availabilities = AdminAvailability.query.filter_by(
            date=check_date,
            is_available=True
        ).all()
        
        for avail in availabilities:
            slots = avail.get_available_slots()
            availability_slots.extend(slots)
    
    return availability_slots


def send_booking_confirmation_email(booking):
    """
    Send booking confirmation email to client
    """
    try:
        from extensions import mail
        
        msg = Message(
            subject=f'Consultation Booking Confirmed - {booking.consultation_type.name}',
            recipients=[booking.client_email],
            html=render_template('emails/booking_confirmation.html', booking=booking)
        )
        
        mail.send(msg)
        
        booking.email_sent = True
        booking.email_sent_at = datetime.utcnow()
        db.session.commit()
    
    except Exception as e:
        current_app.logger.error(f"Email sending error: {str(e)}")
