from flask import Flask, render_template
import os
from datetime import datetime
from dotenv import load_dotenv
from config import get_config
from extensions import db, login_manager, migrate, mail, limiter
from logger import setup_logging
from cache_config import configure_caching, cache_busting_url
import warnings

# Suppress Flask-Limiter in-memory storage warning (acceptable for development)
warnings.filterwarnings('ignore', message='.*Using the in-memory storage.*')

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Load configuration based on environment
    env = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(get_config(env))
    
    # Setup upload folder
    basedir = os.path.abspath(os.path.dirname(__file__))
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder
    
    # Setup logging
    setup_logging(app)
    
    # Configure caching and cache headers
    configure_caching(app)
    
    # Make cache_busting_url available in templates
    app.jinja_env.globals.update(cache_busting_url=cache_busting_url)
    
    # Context processor to make datetime.now() available in templates
    @app.context_processor
    def inject_now():
        return {'now': datetime}
    
    # ------------------ INIT EXTENSIONS ------------------
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    limiter.init_app(app)

    # Import models HERE (after db.init_app) - fixes circular import
    from models import User, Article, Comment, Message, Visit
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        return User.query.get(int(user_id))
    
    # Note: db.create_all() is no longer used - migrations handle schema creation
    # For development setup, run: flask db upgrade
    
    # Security headers middleware
    @app.after_request
    def set_security_headers(response):
        """Add security headers to all responses"""
        response.headers['X-Content-Type-Options'] = 'nosniff'  # Prevent MIME type sniffing
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'  # Prevent clickjacking
        response.headers['X-XSS-Protection'] = '1; mode=block'  # Enable browser XSS protection
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'  # HTTPS only
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; img-src 'self' data: https:"
        return response
    
    # ------------------ REGISTER BLUEPRINTS ------------------
    from blueprints import auth_bp, articles_bp, admin_bp, comments_bp, contact_bp, public_bp
    from blueprints.services import bp as services_bp
    from blueprints.bookings import bp as bookings_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(articles_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(bookings_bp)
    
    # ------------------ ERROR HANDLERS ------------------
    @app.errorhandler(404)
    def page_not_found(error):
        """Handle 404 - Page Not Found errors"""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 - Internal Server errors"""
        db.session.rollback()  # Rollback any failed transactions
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 - Forbidden errors"""
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 - Method Not Allowed errors"""
        return render_template('errors/405.html'), 405
    
    @app.shell_context_processor
    def make_shell_context():
        """Add database and models to Flask shell context"""
        return {'db': db, 'User': User, 'Article': Article, 'Comment': Comment}
    
    return app
    
# 👇 Needed for `flask run`
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)