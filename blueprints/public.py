"""
Public Blueprint - Handles public-facing pages (home, about, etc.)
"""
from flask import Blueprint, render_template, redirect, url_for, request

from models import Article, User
from logger import get_logger
from trending_articles import TrendingQuery
from extensions import db

logger = get_logger(__name__)
public_bp = Blueprint('public', __name__)


# ============================================================================
# HOME PAGE
# ============================================================================

@public_bp.route('/')
def home():
    """Display professional law firm homepage"""
    # Get featured articles for the homepage
    featured_articles = Article.query.filter(
        Article.status == 'approved',
        Article.deleted_at.is_(None),
        Article.is_draft == False
    ).order_by(Article.date_posted.desc()).limit(3).all()
    
    logger.info("Home page accessed")
    
    return render_template(
        'pages/home.html',
        featured_articles=featured_articles,
        page_title='Simply Lawverse - Corporate Legal Services',
        page_description='Professional corporate legal services for Nigerian businesses'
    )


# ============================================================================
# ARTICLE PREVIEW
# ============================================================================

@public_bp.route('/article/<int:article_id>')
def view_article(article_id):
    """Display article in preview/modal view with view count tracking"""
    article = Article.query.get_or_404(article_id)
    
    # Increment view count
    TrendingQuery.increment_view_count(article_id)
    
    return render_template('view_article.html', article=article)


# ============================================================================
# CORPORATE LAW FIRM PAGES
# ============================================================================

@public_bp.route('/about')
def about():
    """Lawyer profile and firm information"""
    return render_template('pages/about.html',
        page_title='About Our Firm',
        page_description='Learn about our experienced corporate lawyer and practice'
    )


@public_bp.route('/blog')
def blog():
    """Blog archive/listing page"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '', type=str)
    per_page = 12
    
    query = Article.query.filter(
        Article.status == 'approved',
        Article.deleted_at.is_(None),
        Article.is_draft == False
    ).order_by(Article.date_posted.desc())
    
    if category:
        query = query.filter(Article.category == category)
    
    articles = query.paginate(page=page, per_page=per_page)
    
    # Get categories for sidebar
    categories = db.session.query(Article.category).filter(
        Article.status == 'approved',
        Article.deleted_at.is_(None)
    ).distinct().all()
    
    return render_template('pages/blog.html',
        articles=articles,
        category=category,
        categories=categories,
        page_title='Legal Articles & Insights',
        page_description='Corporate law articles, tips, and legal insights for Nigerian businesses'
    )


@public_bp.route('/legal/<page_type>')
def legal_page(page_type):
    """Legal/compliance pages - privacy, terms, disclaimer"""
    valid_pages = ['privacy-policy', 'terms', 'disclaimer']
    
    if page_type not in valid_pages:
        return redirect(url_for('public.home'))
    
    return render_template(f'legal/{page_type}.html')
