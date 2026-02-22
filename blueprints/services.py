"""
Services blueprint for displaying legal services
"""
from flask import Blueprint, render_template, abort, current_app
from models import Service, Article
from sqlalchemy import func

bp = Blueprint('services', __name__, url_prefix='/services')


@bp.route('/')
def index():
    """
    Display all services
    """
    services = Service.query.filter_by(is_active=True).order_by(Service.order).all()
    
    return render_template('services/index.html', 
        services=services,
        page_title='Corporate Legal Services',
        page_description='Professional legal services for Nigerian businesses'
    )


@bp.route('/<slug>')
def service_detail(slug):
    """
    Display individual service page
    """
    service = Service.query.filter_by(slug=slug, is_active=True).first_or_404()
    
    # Get related blog articles for this service
    related_articles = Article.query.filter_by(
        status='approved'
    ).filter(
        Article.category.ilike(f'%{service.name}%')
    ).order_by(Article.date_posted.desc()).limit(3).all()
    
    return render_template('services/detail.html',
        service=service,
        related_articles=related_articles,
        page_title=service.seo_title or service.name,
        page_description=service.seo_description or service.description
    )


@bp.errorhandler(404)
def service_not_found(error):
    """Handle service not found"""
    return render_template('errors/404.html'), 404
