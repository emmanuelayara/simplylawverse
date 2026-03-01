"""
Flask Caching Configuration
Implements caching headers and performance optimization
"""

from datetime import datetime, timedelta
from flask import Flask, request
from functools import wraps

# Cache duration constants (in seconds)
CACHE_TIMEOUT_STATIC = 86400 * 30  # 30 days for static assets
CACHE_TIMEOUT_IMAGES = 86400 * 7   # 7 days for images
CACHE_TIMEOUT_HTML = 3600           # 1 hour for HTML pages
CACHE_TIMEOUT_API = 300             # 5 minutes for API responses

# Cache control headers
CACHE_HEADERS_STATIC = {
    'Cache-Control': 'public, max-age=2592000, immutable',  # 30 days
    'Expires': (datetime.utcnow() + timedelta(days=30)).strftime('%a, %d %b %Y %H:%M:%S GMT'),
    'Pragma': 'cache'
}

CACHE_HEADERS_IMAGES = {
    'Cache-Control': 'public, max-age=604800, immutable',  # 7 days
    'Expires': (datetime.utcnow() + timedelta(days=7)).strftime('%a, %d %b %Y %H:%M:%S GMT'),
    'Pragma': 'cache'
}

CACHE_HEADERS_HTML = {
    'Cache-Control': 'public, max-age=3600, must-revalidate',  # 1 hour
    'Pragma': 'cache'
}

CACHE_HEADERS_NO_CACHE = {
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0'
}

CACHE_HEADERS_API = {
    'Cache-Control': 'public, max-age=300',  # 5 minutes
    'Pragma': 'cache'
}


def configure_caching(app: Flask):
    """
    Configure Flask app with caching headers for different content types
    """

    @app.after_request
    def add_cache_headers(response):
        """Add appropriate cache headers based on response type"""

        # Determine content type and route
        path = request.environ.get('PATH_INFO', '')
        content_type = response.content_type or ''

        # Static files (CSS, JS, fonts)
        if path.startswith('/static/') and (
            path.endswith('.css') or
            path.endswith('.js') or
            path.endswith('.woff') or
            path.endswith('.woff2') or
            path.endswith('.ttf') or
            path.endswith('.eot')
        ):
            for header, value in CACHE_HEADERS_STATIC.items():
                response.headers[header] = value
            # Add ETag for cache validation
            if 'ETag' not in response.headers:
                response.headers['ETag'] = f'"{hash(response.data)}"'

        # Image files
        elif path.startswith('/static/uploads/') or path.startswith('/static/images/'):
            for header, value in CACHE_HEADERS_IMAGES.items():
                response.headers[header] = value
            # Add ETag
            if 'ETag' not in response.headers:
                response.headers['ETag'] = f'"{hash(response.data)}"'

        # HTML pages (except admin)
        elif content_type.startswith('text/html') and not path.startswith('/admin'):
            for header, value in CACHE_HEADERS_HTML.items():
                response.headers[header] = value

        # Admin pages - no cache
        elif path.startswith('/admin'):
            for header, value in CACHE_HEADERS_NO_CACHE.items():
                response.headers[header] = value

        # API responses
        elif content_type.startswith('application/json'):
            for header, value in CACHE_HEADERS_API.items():
                response.headers[header] = value

        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Compression - only for regular responses, not file passthrough
        try:
            if not getattr(response, 'direct_passthrough', False) and len(response.data) > 1024:
                response.headers['Vary'] = 'Accept-Encoding'
        except RuntimeError:
            # Skip compression for file responses in passthrough mode
            pass

        return response


def cache_busting_url(app: Flask, filename: str) -> str:
    """
    Generate a cache-busting URL for static files using file hash
    Usage in templates: {{ cache_busting_url('css/style.css') }}
    """
    try:
        from werkzeug.security import safe_str_cmp
        import hashlib

        filepath = app.static_folder + '/' + filename
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()[:8]
            return f'/static/{filename}?v={file_hash}'
    except Exception as e:
        print(f"Error generating cache-busting URL: {e}")

    return f'/static/{filename}'


def set_response_cache_headers(timeout=300, public=True):
    """
    Decorator for setting cache headers on specific routes
    Usage:
        @app.route('/articles')
        @set_response_cache_headers(timeout=3600)
        def articles():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)

            # Set cache control header
            cache_control = f"public, max-age={timeout}" if public else f"private, max-age={timeout}"
            if hasattr(response, 'headers'):
                response.headers['Cache-Control'] = cache_control

            return response

        return decorated_function

    return decorator


class CacheHelper:
    """Helper class for cache-related utilities"""

    @staticmethod
    def get_cache_key(endpoint, **params):
        """Generate a cache key from endpoint and parameters"""
        param_str = '_'.join(f"{k}_{v}" for k, v in sorted(params.items()))
        return f"{endpoint}_{param_str}" if param_str else endpoint

    @staticmethod
    def should_cache(response, cache_rules=None):
        """Determine if response should be cached"""
        if cache_rules is None:
            cache_rules = {
                'text/html': True,
                'application/json': True,
                'text/plain': False,
            }

        content_type = response.content_type or ''
        for cached_type, should_cache in cache_rules.items():
            if cached_type in content_type:
                return should_cache

        return False

    @staticmethod
    def get_fresh_time(seconds):
        """Get time when cache becomes stale"""
        return datetime.utcnow() + timedelta(seconds=seconds)

    @staticmethod
    def is_cache_fresh(cache_time, timeout):
        """Check if cache is still fresh"""
        return datetime.utcnow() < cache_time + timedelta(seconds=timeout)


# Import statements needed
import os
