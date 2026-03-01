"""
Email utility functions for sending emails.
"""
from flask import current_app
from flask_mail import Message
from logger import get_logger

logger = get_logger(__name__)

def send_email(subject, recipients, text_body=None, html_body=None):
    """
    Send an email with the given parameters.
    
    Args:
        subject (str): Email subject line
        recipients (list): List of recipient email addresses
        text_body (str, optional): Plain text body
        html_body (str, optional): HTML body
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        msg = Message(subject=subject, recipients=recipients)
        if text_body:
            msg.body = text_body
        if html_body:
            msg.html = html_body
        
        current_app.extensions['mail'].send(msg)
        logger.info(f"Email sent successfully to {recipients}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipients}: {str(e)}")
        return False

def send_password_reset_email(user, reset_url):
    """
    Send password reset email to user.
    
    Args:
        user: User object with email attribute
        reset_url (str): URL for password reset
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    text_body = f'''To reset your password, visit the following link:
{reset_url}

This link will expire in 30 minutes.

If you did not make this request, please ignore this email.
'''
    
    return send_email(
        subject='Password Reset Request',
        recipients=[user.email],
        text_body=text_body
    )

def send_contact_confirmation_email(user_email, subject_line):
    """
    Send confirmation email for contact form submission.
    
    Args:
        user_email (str): User's email address
        subject_line (str): Original subject from contact form
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    text_body = f'''Thank you for contacting Simply Law!

Your message with subject "{subject_line}" has been received.
We will get back to you as soon as possible.

Best regards,
The Simply Law Team
'''
    
    return send_email(
        subject='We received your message - Simply Law',
        recipients=[user_email],
        text_body=text_body
    )
