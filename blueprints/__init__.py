"""
Blueprint modules for organizing routes by functionality.
"""
from .auth import auth_bp
from .articles import articles_bp
from .admin import admin_bp
from .comments import comments_bp
from .contact import contact_bp
from .public import public_bp

__all__ = ['auth_bp', 'articles_bp', 'admin_bp', 'comments_bp', 'contact_bp', 'public_bp']
