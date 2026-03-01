"""
Security utilities for the application
"""
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
from bleach import clean
import re
import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

# HTML sanitization configuration
ALLOWED_TAGS = {
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote', 'a', 'code', 'pre'
}

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'code': ['class'],
    'pre': ['class']
}

# File upload configuration
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILENAME_LENGTH = 255

def sanitize_html(text, allowed_tags=ALLOWED_TAGS, allowed_attributes=ALLOWED_ATTRIBUTES):
    """
    Sanitize HTML content to prevent XSS attacks
    
    Args:
        text: The HTML text to sanitize
        allowed_tags: Set of allowed HTML tags
        allowed_attributes: Dictionary of allowed attributes for tags
    
    Returns:
        Sanitized HTML string
    """
    if not text:
        return ''
    
    return clean(text, tags=allowed_tags, attributes=allowed_attributes, strip=True)


def sanitize_string(text, max_length=None, allow_html=False):
    """
    Sanitize plain text input
    
    Args:
        text: The text to sanitize
        max_length: Maximum length of text
        allow_html: If True, sanitize as HTML; if False, escape all tags
    
    Returns:
        Sanitized string
    """
    if not text:
        return ''
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # If HTML not allowed, escape any HTML characters
    if not allow_html:
        text = text.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')
    
    # Limit length if specified
    if max_length:
        text = text[:max_length]
    
    return text.strip()


def validate_email(email):
    """
    Validate email address format
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) and len(email) <= 120


def validate_file_upload(file, allowed_extensions, max_size):
    """
    Validate file upload for security
    
    Args:
        file: The file object from request.files
        allowed_extensions: Set of allowed file extensions (without dots)
        max_size: Maximum file size in bytes
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if file exists
    if not file or file.filename == '':
        return (False, 'No file provided.')
    
    # Check filename length
    if len(file.filename) > MAX_FILENAME_LENGTH:
        return (False, f'Filename is too long (max {MAX_FILENAME_LENGTH} characters).')
    
    # Get file extension
    if '.' not in file.filename:
        return (False, 'File must have an extension.')
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    
    # Check file extension
    if ext not in allowed_extensions:
        ext_list = ', '.join(sorted(allowed_extensions))
        return (False, f'Invalid file type. Allowed types: {ext_list}')
    
    # Read file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset pointer
    
    # Check file size
    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        return (False, f'File is too large. Maximum size is {max_mb:.1f}MB.')
    
    # Check if file is empty
    if file_size == 0:
        return (False, 'File is empty.')
    
    return (True, None)


def validate_image_file(file):
    """
    Validate image file for upload
    
    Args:
        file: The file object from request.files
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    return validate_file_upload(file, ALLOWED_IMAGE_EXTENSIONS, MAX_IMAGE_SIZE)


def validate_document_file(file):
    """
    Validate document file for upload
    
    Args:
        file: The file object from request.files
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    return validate_file_upload(file, ALLOWED_DOCUMENT_EXTENSIONS, MAX_DOCUMENT_SIZE)


def get_safe_filename(filename):
    """
    Generate a safe filename from user input
    
    Args:
        filename: Original filename
    
    Returns:
        Safe filename with timestamp prefix
    """
    safe_name = secure_filename(filename)
    
    # If secure_filename resulted in empty string, use a default
    if not safe_name:
        safe_name = 'file'
    
    # Add timestamp to ensure uniqueness
    import time
    return f"{int(time.time())}_{safe_name}"


def admin_required(f):
    """
    Decorator to require admin privileges
    Use this on routes that require admin access
    
    Example:
        @app.route('/admin/delete')
        @login_required
        @admin_required
        def delete_something():
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You must be logged in.', 'danger')
            return redirect(url_for('auth.admin_login'))
        
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('public.home'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def prevent_xss(f):
    """
    Decorator to automatically sanitize form inputs
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    
    return decorated_function
