"""
Admin Blueprint - Handles admin dashboard, article approvals, and administrative tasks.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta

from extensions import db
from models import Article, Visit, Message, Comment
from security import admin_required
from logger import get_logger

logger = get_logger(__name__)
admin_bp = Blueprint('admin', __name__)

# ============================================================================
# ADMIN DASHBOARD
# ============================================================================

@admin_bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Display admin dashboard with statistics and article moderation"""
    total_articles = Article.query.count()
    total_visits = Visit.query.count()
    now = datetime.utcnow()

    daily_visits = Visit.query.filter(Visit.timestamp >= now - timedelta(days=1)).count()
    weekly_visits = Visit.query.filter(Visit.timestamp >= now - timedelta(weeks=1)).count()
    monthly_visits = Visit.query.filter(Visit.timestamp >= now - timedelta(days=30)).count()
    yearly_visits = Visit.query.filter(Visit.timestamp >= now - timedelta(days=365)).count()

    readers_per_article = db.session.query(
        Article.title, db.func.count(Visit.id)
    ).join(Visit, Article.id == Visit.article_id).group_by(Article.id).all()

    pending_page = request.args.get('pending_page', 1, type=int)
    approved_page = request.args.get('approved_page', 1, type=int)
    per_page = 3

    pending = Article.query.filter_by(status='pending') \
        .order_by(Article.date_posted.desc()) \
        .paginate(page=pending_page, per_page=per_page)

    approved = Article.query.filter_by(status='approved') \
        .order_by(Article.date_posted.desc()) \
        .paginate(page=approved_page, per_page=per_page)

    return render_template(
        'admin_dashboard.html',
        articles=pending,
        approved_articles=approved,
        total_articles=total_articles,
        total_visits=total_visits,
        daily_visits=daily_visits,
        weekly_visits=weekly_visits,
        monthly_visits=monthly_visits,
        yearly_visits=yearly_visits,
        readers_per_article=readers_per_article
    )


# ============================================================================
# ARTICLE APPROVALS
# ============================================================================

@admin_bp.route('/admin/view/<int:article_id>')
@login_required
@admin_required
def admin_view_article(article_id):
    """View a full article for review (pending or approved)"""
    try:
        article = Article.query.get_or_404(article_id)
        if article.is_deleted():
            flash("This article has been deleted.", "warning")
            return redirect(url_for('admin.admin_dashboard')), 404
        
        # Get paginated comments
        page = request.args.get('page', 1, type=int)
        paginated_comments = Comment.query.filter(
            Comment.article_id == article_id,
            Comment.parent_id.is_(None),  # Only root comments
            Comment.deleted_at.is_(None)  # Exclude soft-deleted comments
        ).order_by(Comment.date_posted.desc()).paginate(
            page=page,
            per_page=5,
            error_out=False
        )
        
        logger.info(f"Admin {current_user.username} viewed article {article_id}")
        return render_template(
            'admin_view_article.html',
            article=article,
            paginated_comments=paginated_comments
        )
    except Exception as e:
        logger.error(f"Error viewing article {article_id}: {str(e)}")
        flash('Error loading article.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/admin/approve/<int:article_id>', methods=['POST'])
@login_required
@admin_required
def approve_article(article_id):
    """Approve a pending article for publication"""
    try:
        article = Article.query.get_or_404(article_id)
        article.status = 'approved'
        db.session.commit()
        logger.info(f"Article {article_id} approved by {current_user.username}")
        flash('Article approved successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Approve article error for article {article_id}: {str(e)}")
        flash('Error approving article.', 'danger')
    
    return redirect(url_for('admin.admin_view_article', article_id=article_id))


@admin_bp.route('/admin/disapprove/<int:article_id>', methods=['POST'])
@login_required
@admin_required
def disapprove_article(article_id):
    """Disapprove a pending article"""
    try:
        article = Article.query.get_or_404(article_id)
        article.status = 'disapproved'
        db.session.commit()
        logger.info(f"Article {article_id} disapproved by {current_user.username}")
        flash('Article disapproved.', 'warning')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Disapprove article error for article {article_id}: {str(e)}")
        flash('Error disapproving article.', 'danger')
    
    return redirect(url_for('admin.admin_dashboard'))


# ============================================================================
# MESSAGE VIEWING
# ============================================================================

@admin_bp.route('/messages')
@login_required
@admin_required
def view_messages():
    """View all contact form messages"""
    messages = Message.query.order_by(Message.date_sent.desc()).all()
    return render_template('messages.html', messages=messages)
