"""
Comments Blueprint - Handles article comments, threading, soft deletes, and replies.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from extensions import db, limiter
from models import Comment
from security import sanitize_html, sanitize_string, validate_email, admin_required
from logger import get_logger

logger = get_logger(__name__)
comments_bp = Blueprint('comments', __name__)

# ============================================================================
# COMMENT POSTING
# ============================================================================

@comments_bp.route('/article/<int:article_id>/comment', methods=['POST'])
@limiter.limit("10 per hour")  # Rate limit comment submissions
def post_comment(article_id):
    """Post a new top-level comment on an article"""
    try:
        # Get form data with validation and sanitization
        name = sanitize_string(request.form.get('name', '').strip(), max_length=100)
        email = sanitize_string(request.form.get('email', '').strip(), max_length=120)
        content = sanitize_html(request.form.get('comment', '').strip())
        
        # Validate required fields
        if not name or not content:
            flash("Name and comment are required.", "danger")
            return redirect(url_for('articles.read_more', article_id=article_id))
        
        # Validate name length
        if len(name) < 2:
            flash("Name must be at least 2 characters.", "danger")
            return redirect(url_for('articles.read_more', article_id=article_id))
        
        # Validate comment length
        if len(content) < 2 or len(content) > 5000:
            flash("Comment must be between 2 and 5000 characters.", "danger")
            return redirect(url_for('articles.read_more', article_id=article_id))
        
        # Validate email if provided
        if email and not validate_email(email):
            flash("Invalid email address format.", "danger")
            return redirect(url_for('articles.read_more', article_id=article_id))
        
        # Create and save comment
        comment = Comment(
            name=name,
            email=email if email else 'anonymous',
            content=content,
            article_id=article_id
        )
        db.session.add(comment)
        db.session.commit()
        logger.info(f"Comment posted on article {article_id} by {name}")
        flash("Comment posted successfully!", "success")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Comment posting error for article {article_id}: {str(e)}")
        flash(f"Error posting comment: {str(e)}", "danger")
    
    return redirect(url_for('articles.read_more', article_id=article_id))


# ============================================================================
# THREADED REPLIES
# ============================================================================

@comments_bp.route('/comment/<int:parent_id>/reply', methods=['POST'])
@limiter.limit("10 per hour")
def reply_to_comment(parent_id):
    """Reply to a specific comment (threading)"""
    try:
        parent_comment = Comment.query.get_or_404(parent_id)
        article_id = parent_comment.article_id
        
        # Get form data with sanitization
        name = sanitize_string(request.form.get('name', '').strip(), max_length=100)
        email = sanitize_string(request.form.get('email', '').strip(), max_length=120)
        content = sanitize_html(request.form.get('reply', '').strip())
        
        # Validate required fields
        if not name or not content:
            flash("Name and reply are required.", "danger")
            return redirect(url_for('articles.read_more', article_id=article_id))
        
        if len(content) < 2 or len(content) > 5000:
            flash("Reply must be between 2 and 5000 characters.", "danger")
            return redirect(url_for('articles.read_more', article_id=article_id))
        
        if email and not validate_email(email):
            flash("Invalid email address format.", "danger")
            return redirect(url_for('articles.read_more', article_id=article_id))
        
        # Create reply comment with parent_id set
        reply = Comment(
            name=name,
            email=email if email else 'anonymous',
            content=content,
            article_id=article_id,
            parent_id=parent_id  # Link to parent comment
        )
        db.session.add(reply)
        db.session.commit()
        logger.info(f"Reply posted to comment {parent_id} on article {article_id}")
        flash("Reply posted successfully!", "success")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Reply posting error for comment {parent_id}: {str(e)}")
        flash(f"Error posting reply: {str(e)}", "danger")
    
    return redirect(url_for('articles.read_more', article_id=article_id, _anchor=f'comment-{parent_id}'))


# ============================================================================
# SOFT DELETE & RESTORE
# ============================================================================

@comments_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def soft_delete_comment(comment_id):
    """Soft delete a comment (author or admin only)"""
    try:
        comment = Comment.query.get_or_404(comment_id)
        article_id = comment.article_id
        
        # Check permissions (author or admin)
        is_author = comment.name == current_user.username if current_user.is_authenticated else False
        is_admin = current_user.is_admin if current_user.is_authenticated else False
        
        if not (is_author or is_admin):
            logger.warning(f"Unauthorized delete attempt on comment {comment_id} by {current_user.username}")
            flash("You don't have permission to delete this comment.", "danger")
            return redirect(url_for('articles.read_more', article_id=article_id))
        
        comment.soft_delete()
        db.session.commit()
        logger.info(f"Comment {comment_id} soft-deleted")
        flash("Comment deleted successfully.", "success")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Soft delete comment error for comment {comment_id}: {str(e)}")
        flash("Error deleting comment.", "danger")
    
    return redirect(url_for('articles.read_more', article_id=article_id))


@comments_bp.route('/comment/<int:comment_id>/restore', methods=['POST'])
@login_required
def restore_comment(comment_id):
    """Restore a soft-deleted comment (author or admin only)"""
    try:
        comment = Comment.query.get_or_404(comment_id)
        article_id = comment.article_id
        
        # Check permissions (author or admin)
        is_author = comment.name == current_user.username if current_user.is_authenticated else False
        is_admin = current_user.is_admin if current_user.is_authenticated else False
        
        if not (is_author or is_admin):
            logger.warning(f"Unauthorized restore attempt on comment {comment_id} by {current_user.username}")
            flash("You don't have permission to restore this comment.", "danger")
            return redirect(url_for('articles.read_more', article_id=article_id))
        
        comment.restore()
        db.session.commit()
        logger.info(f"Comment {comment_id} restored")
        flash("Comment restored successfully.", "success")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Restore comment error for comment {comment_id}: {str(e)}")
        flash("Error restoring comment.", "danger")
    
    return redirect(url_for('articles.read_more', article_id=article_id))
