"""
Logging configuration for the application.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    """Configure application logging"""
    if not app.debug:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler('logs/simplylawverse.log', maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Simplylawverse startup')

def get_logger(name):
    """Get a logger instance"""
    return logging.getLogger(name)
