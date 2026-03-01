"""
Authentication Blueprint - Handles user authentication, registration, password reset.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app

from extensions import db, limiter
from forms import (
    LoginForm, AdminRegisterForm, ForgotPasswordForm, ResetPasswordForm,
    EditProfileForm, ChangePasswordForm
)
from models import User, Article, Comment
from security import sanitize_string, validate_email
from email_utils import send_password_reset_email
from logger import get_logger

logger = get_logger(__name__)
auth_bp = Blueprint('auth', __name__)

# ============================================================================
# ADMIN REGISTRATION & LOGIN
# ============================================================================

@auth_bp.route('/admin/register', methods=['GET', 'POST'])
@limiter.limit("5 per day")  # Limit registration attempts
def register_admin():
    """Register a new admin user"""
    form = AdminRegisterForm()
    if form.validate_on_submit():
        # Sanitize inputs
        username = sanitize_string(form.username.data, max_length=150)
        email = sanitize_string(form.email.data, max_length=100)
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            logger.warning(f"Registration attempt with existing username: {username}")
            return redirect(url_for('auth.register_admin'))
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            logger.warning(f"Registration attempt with existing email: {email}")
            return redirect(url_for('auth.register_admin'))

        try:
            hashed_password = generate_password_hash(form.password.data)
            new_admin = User(
                username=username,
                email=email,
                password=hashed_password,
                is_admin=True
            )
            db.session.add(new_admin)
            db.session.commit()
            flash("Admin registered successfully!", "success")
            logger.info(f"New admin registered: {username}")
            return redirect(url_for('auth.admin_login'))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "danger")
            logger.error(f"Registration error for {username}: {str(e)}")
    
    return render_template('admin_register.html', form=form)


@auth_bp.route('/admin/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # Rate limit login attempts
def admin_login():
    """Authenticate and log in admin user"""
    form = LoginForm()
    if form.validate_on_submit():
        # Check if input is email or username
        login_input = form.username.data
        user = User.query.filter(
            (User.username == login_input) | (User.email == login_input)
        ).first()
        if user and check_password_hash(user.password, form.password.data) and user.is_admin:
            login_user(user)
            logger.info(f"Admin login successful: {user.username}")
            return redirect(url_for('admin.admin_dashboard'))
        # Generic message to prevent user enumeration
        logger.warning(f"Failed login attempt for: {login_input}")
        flash('Invalid credentials or not an admin.', 'danger')
    
    return render_template('admin_login.html', form=form)


@auth_bp.route('/admin/logout')
@login_required
def admin_logout():
    """Log out the current user"""
    logger.info(f"User logout: {current_user.username}")
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.admin_login'))


# ============================================================================
# PASSWORD RESET
# ============================================================================

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("5 per hour")  # Rate limit password reset requests
def forgot_password():
    """Handle forgot password request"""
    if current_user.is_authenticated:
        return redirect(url_for('public.home'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            reset_url = url_for('auth.reset_password', token=user.get_reset_token(), _external=True)
            if send_password_reset_email(user, reset_url):
                logger.info(f"Password reset email sent to: {user.email}")
                flash('An email has been sent with instructions to reset your password.', 'info')
            else:
                logger.error(f"Failed to send reset email to: {user.email}")
                flash('Email service is currently unavailable. Please try again later.', 'danger')
        else:
            # Don't reveal if email exists (security best practice)
            logger.info(f"Password reset requested for non-existent email: {form.email.data}")
            flash('An email has been sent with instructions to reset your password.', 'info')
        
        return redirect(url_for('auth.admin_login'))
    
    return render_template('forgot_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token"""
    if current_user.is_authenticated:
        return redirect(url_for('public.home'))
    
    user = User.verify_reset_token(token)
    if not user:
        logger.warning(f"Invalid/expired password reset token attempted")
        flash('That is an invalid or expired token.', 'danger')
        return redirect(url_for('auth.admin_login'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            hashed_password = generate_password_hash(form.password.data)
            user.password = hashed_password
            db.session.commit()
            logger.info(f"Password reset successful for user: {user.username}")
            flash('Your password has been reset! You can now log in with your new password.', 'success')
            return redirect(url_for('auth.admin_login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Password reset error for {user.username}: {str(e)}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('reset_password.html', form=form)


# ============================================================================
# USER PROFILE
# ============================================================================

@auth_bp.route('/profile')
@login_required
def profile():
    """Display user profile"""
    user_articles_count = Article.query.filter_by(author=current_user.username).count()
    user_comments_count = Comment.query.filter_by(name=current_user.username).count()
    pending_articles_count = 0
    
    if current_user.is_admin:
        pending_articles_count = Article.query.filter_by(status='pending').count()
    
    return render_template(
        'profile.html',
        user_articles_count=user_articles_count,
        user_comments_count=user_comments_count,
        pending_articles_count=pending_articles_count
    )


@auth_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile information"""
    form = EditProfileForm()
    
    if form.validate_on_submit():
        try:
            current_user.username = sanitize_string(form.username.data, max_length=150)
            current_user.email = sanitize_string(form.email.data, max_length=100)
            db.session.commit()
            logger.info(f"Profile updated for user: {current_user.username}")
            flash('Your profile has been updated successfully!', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Profile update error for {current_user.username}: {str(e)}")
            flash('An error occurred while updating your profile. Please try again.', 'danger')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    return render_template('edit_profile.html', form=form)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        try:
            hashed_password = generate_password_hash(form.new_password.data)
            current_user.password = hashed_password
            db.session.commit()
            logger.info(f"Password changed for user: {current_user.username}")
            flash('Your password has been changed successfully!', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Password change error for {current_user.username}: {str(e)}")
            flash('An error occurred while changing your password. Please try again.', 'danger')
    
    return render_template('change_password.html', form=form)
