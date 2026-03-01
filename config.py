"""
Configuration management for Simply Law
Handles development, testing, and production environments
"""
import os
from datetime import timedelta


class Config:
    """Base configuration with defaults"""
    
    # Flask
    FLASK_APP = os.environ.get('FLASK_APP', 'app.py')
    
    # Secret key (MUST be set in production)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-this')
    if SECRET_KEY == 'dev-secret-key-change-this' and os.environ.get('FLASK_ENV') == 'production':
        raise ValueError('SECRET_KEY must be set in production environment!')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', 'false').lower() == 'true'
    
    # Database connection pooling (important for production)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('SQLALCHEMY_POOL_SIZE', 10)),
        'pool_recycle': int(os.environ.get('SQLALCHEMY_POOL_RECYCLE', 3600)),
        'pool_pre_ping': os.environ.get('SQLALCHEMY_POOL_PRE_PING', 'true').lower() == 'true',
    }
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@simplylawverse.com')
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.environ.get('PERMANENT_SESSION_LIFETIME', 3600))
    )
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'true').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    
    # Upload Configuration
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'static/uploads')
    ALLOWED_EXTENSIONS = set(
        os.environ.get('ALLOWED_EXTENSIONS', 'jpg,jpeg,png,gif,pdf,doc,docx').split(',')
    )
    
    # URL Scheme
    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME', 'http')
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.environ.get('LOG_FORMAT', 'json')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/simplylawverse.log')
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 10 * 1024 * 1024))
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 10))
    
    # Application Settings
    APP_NAME = os.environ.get('APP_NAME', 'Simply Law')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@simplylawverse.com')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # Development uses SQLite by default
    if not os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    
    # Less strict cookie settings for local development
    SESSION_COOKIE_SECURE = False
    
    # Enable SQL echo in development
    SQLALCHEMY_ECHO = True
    
    # Disable HTTPS requirement in development
    PREFERRED_URL_SCHEME = 'http'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Production must use PostgreSQL or MySQL (validation only if actually deploying)
    # This check will run when explicitly importing ProductionConfig in production
    
    # Enforce HTTPS in production
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'
    
    # Disable SQL echo in production
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    
    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Use simple password hashing for tests (faster)
    BCRYPT_LOG_ROUNDS = 4


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration object based on environment"""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])


def validate_production_config():
    """Validate production configuration - call this before deploying to production"""
    if os.environ.get('FLASK_ENV') == 'production':
        db_url = os.environ.get('DATABASE_URL', '')
        if 'sqlite' in db_url.lower() or not db_url:
            raise ValueError(
                'SQLite is not suitable for production! '
                'Set DATABASE_URL to PostgreSQL or MySQL in production.\n'
                'Example: postgresql://user:pass@localhost:5432/simplylawverse_db'
            )
        
        secret_key = os.environ.get('SECRET_KEY', '')
        if not secret_key or secret_key == 'dev-secret-key-change-this':
            raise ValueError(
                'SECRET_KEY must be set to a strong random value in production!\n'
                'Generate with: python -c "import secrets; print(secrets.token_hex(32))"'
            )
