"""
Contact Blueprint - Handles contact form submissions.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request

from extensions import db, limiter
from forms import ContactForm
from models import Message
from security import sanitize_html, sanitize_string, validate_email
from email_utils import send_contact_confirmation_email
from logger import get_logger

logger = get_logger(__name__)
contact_bp = Blueprint('contact', __name__)

# ============================================================================
# CONTACT FORM
# ============================================================================

@contact_bp.route('/contact', methods=['GET', 'POST'])
@limiter.limit("5 per hour")  # Rate limit contact form submissions
def contact():
    """Handle contact form submission"""
    form = ContactForm()
    if form.validate_on_submit():
        try:
            # Sanitize all inputs before storing
            sanitized_name = sanitize_string(form.name.data, max_length=100)
            sanitized_email = sanitize_string(form.email.data, max_length=120)
            sanitized_subject = sanitize_string(form.subject.data, max_length=200) if hasattr(form, 'subject') else 'Contact Form'
            sanitized_message = sanitize_html(form.message.data)
            
            # Validate email
            if not validate_email(sanitized_email):
                flash("Invalid email address.", "danger")
                logger.warning(f"Invalid email attempted in contact form: {sanitized_email}")
                return render_template('contact.html', form=form)
            
            # Save message to database
            new_message = Message(
                name=sanitized_name,
                email=sanitized_email,
                message=sanitized_message
            )
            db.session.add(new_message)
            db.session.commit()
            logger.info(f"Contact form submission from {sanitized_name} ({sanitized_email})")
            
            # Send confirmation email to user
            if send_contact_confirmation_email(sanitized_email, sanitized_subject):
                flash("Your message has been sent successfully! Check your email for confirmation.", "success")
            else:
                flash("Your message has been saved. Confirmation email could not be sent.", "warning")
            
            return redirect(url_for('contact.contact'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Contact form submission error: {str(e)}")
            flash("An error occurred while sending your message. Please try again.", "danger")
    
    return render_template('contact.html', form=form)
