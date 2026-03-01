"""
Articles Blueprint - Handles article submission, viewing, drafts, and soft deletes.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from datetime import datetime
import os

from extensions import db, limiter
from forms import ArticleSubmissionForm, CommentForm
from models import Article, Comment
from security import (
    admin_required, sanitize_html, sanitize_string,
    validate_image_file, validate_document_file, get_safe_filename,
    ALLOWED_IMAGE_EXTENSIONS, ALLOWED_DOCUMENT_EXTENSIONS
)
from logger import get_logger

logger = get_logger(__name__)
articles_bp = Blueprint('articles', __name__)

COMMENTS_PER_PAGE = 10

# ============================================================================
# FILE UPLOAD
# ============================================================================

@articles_bp.route('/upload', methods=['GET', 'POST'])
def upload_cover_image():
    """Handle file uploads for cover images and documents"""
    if request.method == 'POST':
        try:
            # Check if file is in request
            if 'cover_image' not in request.files:
                flash('No file provided. Please select a file to upload.', 'danger')
                return redirect(request.url)

            file = request.files['cover_image']

            # Validate file
            is_valid, error_msg = validate_image_file(file)
            if not is_valid:
                flash(error_msg, 'danger')
                return redirect(request.url)

            # Check if directory is writable
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            
            if not os.access(upload_folder, os.W_OK):
                flash('Upload folder is not writable. Please contact administrator.', 'danger')
                logger.error(f"Upload folder not writable: {upload_folder}")
                return redirect(request.url)
            
            # Generate safe filename and save
            unique_filename = get_safe_filename(file.filename)
            filepath = os.path.join(upload_folder, unique_filename)
            file.save(filepath)
            
            logger.info(f"File uploaded successfully: {unique_filename}")
            flash('Upload successful!', 'success')
            return redirect(url_for('articles.upload_cover_image'))
                
        except Exception as e:
            logger.error(f"File upload error: {str(e)}")
            flash(f'An error occurred during upload: {str(e)}', 'danger')
            return redirect(request.url)

    return render_template('submit_article.html')


# ============================================================================
# ARTICLE SUBMISSION
# ============================================================================

@articles_bp.route('/submit', methods=['GET', 'POST'])
def submit_article():
    """Submit a new article for publication (guests and authenticated users)"""
    form = ArticleSubmissionForm()
    form.category.choices = [(cat, cat) for cat in [
        "Criminal Law", "Family Law", "Constitutional Law",
        "Tech Law", "Property Law", "Administrative Law",
        "International Law", "Contract Law", "Tort Law",
        "Succession Law", "Corporate Law", "Commercial Law",
        "Banking and Finance Law", "Securities Law", "Civil Litigation",
        "Criminal Litigation", "Alternative Dispute Resolution", "Environmental Law",
        "Energy Law", "Intellectual Property Law", "Copyright Law",
        "Patent Law", "Trademark Law", "Trade Secrets Law",
        "Labour and Employment Law", "Human Rights Law", "Health and Medical Law",
        "Insurance Law", "Sports and Entertainment Law", "Cyber Law"
    ]]
    
    if form.validate_on_submit():
        # Sanitize user inputs
        title = sanitize_string(form.title.data.strip(), max_length=250)
        category = sanitize_string(form.category.data, max_length=50)
        content = sanitize_html(form.content.data.strip())
        
        # Get author and email - prioritize form data, fall back to current_user
        if current_user.is_authenticated:
            # If authenticated user provided a custom author name in form, use it; otherwise use username
            author = sanitize_string(form.author.data.strip(), max_length=100) if form.author.data else current_user.username
            # Same for email - form takes priority, then current_user
            email = sanitize_string(form.email.data.strip(), max_length=120) if form.email.data else current_user.email
            author_source = "authenticated user"
        else:
            author = sanitize_string(form.author.data.strip(), max_length=100) if hasattr(form, 'author') and form.author.data else 'Guest'
            email = sanitize_string(form.email.data.strip(), max_length=120) if hasattr(form, 'email') and form.email.data else ''
            author_source = "guest"
        
        # Validate inputs
        if len(title) < 5 or len(title) > 250:
            flash("Title must be between 5 and 250 characters.", "danger")
            return redirect(request.url)
        
        if len(content) < 50 or len(content) > 50000:
            flash("Article must be between 50 and 50000 characters.", "danger")
            return redirect(request.url)
        
        try:
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            
            # Handle cover image upload
            cover_image_filename = None
            if 'cover_image' in request.files and request.files['cover_image'].filename:
                cover_image = request.files['cover_image']
                
                # Validate file
                is_valid, error_msg = validate_image_file(cover_image)
                if not is_valid:
                    flash(f'Cover image error: {error_msg}', 'danger')
                    return render_template('submit_article.html', form=form)
                
                try:
                    cover_image_filename = get_safe_filename(cover_image.filename)
                    full_path = os.path.join(upload_folder, cover_image_filename)
                    cover_image.save(full_path)
                    logger.info(f"✅ Saved cover image: {cover_image_filename}")
                except Exception as e:
                    flash(f'Error uploading cover image: {str(e)}', 'danger')
                    logger.warning(f"❌ Cover image upload error: {str(e)}")
                    return render_template('submit_article.html', form=form)
            
            # Handle document upload (optional)
            document_filename = None
            if 'document' in request.files and request.files['document'].filename:
                document = request.files['document']
                
                # Validate file
                is_valid, error_msg = validate_document_file(document)
                if not is_valid:
                    flash(f'Document error: {error_msg}', 'danger')
                    return render_template('submit_article.html', form=form)
                
                try:
                    document_filename = get_safe_filename(document.filename)
                    full_path = os.path.join(upload_folder, document_filename)
                    document.save(full_path)
                    logger.info(f"✅ Saved document: {document_filename}")
                except Exception as e:
                    flash(f'Error uploading document: {str(e)}', 'danger')
                    logger.warning(f"❌ Document upload error: {str(e)}")
                    return render_template('submit_article.html', form=form)
            
            article = Article(
                author=author,
                email=email,
                title=title,
                content=content,
                category=category,
                status='pending',  # Awaits admin approval
                cover_image=cover_image_filename,
                document_filename=document_filename
            )
            db.session.add(article)
            db.session.commit()
            logger.info(f"Article submitted by {author_source} ({author}): {title}")
            flash(f"Article '{title}' submitted successfully! It's awaiting admin approval.", "success")
            return redirect(url_for('public.home'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Article submission error for {author}: {str(e)}")
            flash(f"Error submitting article: {str(e)}", "danger")
            return redirect(request.url)
    else:
        if request.method == 'POST':
            author_name = current_user.username if current_user.is_authenticated else "guest"
            logger.warning(f"Article form validation failed for {author_name}: {form.errors}")
            flash("Form validation failed. Please check your inputs.", "danger")
    
    return render_template('submit_article.html', form=form)


# ============================================================================
# ARTICLE VIEWING & READING
# ============================================================================

@articles_bp.route('/article/<int:article_id>')
@articles_bp.route('/read/<int:article_id>')
@articles_bp.route('/read/<int:article_id>/page/<int:page>')
def read_more(article_id, page=1):
    """Display article with paginated comments"""
    # Get article and check if it's approved and not soft-deleted
    article = Article.query.get_or_404(article_id)
    if article.is_deleted() or article.status != 'approved':
        flash("This article is no longer available.", "warning")
        return redirect(url_for('public.home')), 404
    
    # Get paginated comments (excluding soft-deleted)
    paginated_comments = Comment.query.filter(
        Comment.article_id == article_id,
        Comment.parent_id.is_(None),  # Only root comments
        Comment.deleted_at.is_(None)  # Exclude soft-deleted comments
    ).order_by(Comment.date_posted.desc()).paginate(
        page=page,
        per_page=COMMENTS_PER_PAGE,
        error_out=False
    )
    
    form = CommentForm()
    return render_template(
        'read_more.html',
        article=article,
        paginated_comments=paginated_comments,
        page=page
    )


# ============================================================================
# LIKE SYSTEM
# ============================================================================

@articles_bp.route('/like/<int:article_id>', methods=['POST'])
def like_article(article_id):
    """Increment article like count"""
    try:
        article = Article.query.get_or_404(article_id)
        article.likes = (article.likes or 0) + 1
        db.session.commit()
        logger.info(f"Article {article_id} liked")
        flash('You liked the article.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Like article error for article {article_id}: {str(e)}")
        flash('Error liking article. Please try again.', 'danger')
    
    return redirect(request.referrer or url_for('articles.read_more', article_id=article_id))


# ============================================================================
# SOFT DELETE & RESTORE
# ============================================================================

@articles_bp.route('/article/<int:article_id>/delete', methods=['POST'])
@login_required
@admin_required
def soft_delete_article(article_id):
    """Soft delete an article (mark as deleted)"""
    try:
        article = Article.query.get_or_404(article_id)
        article.soft_delete()
        db.session.commit()
        logger.info(f"Article {article_id} soft-deleted by admin")
        flash(f"Article '{article.title}' has been deleted.", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Soft delete article error for article {article_id}: {str(e)}")
        flash("Error deleting article.", "danger")
    
    return redirect(url_for('admin.admin_dashboard'))


@articles_bp.route('/article/<int:article_id>/restore', methods=['POST'])
@login_required
@admin_required
def restore_article(article_id):
    """Restore a soft-deleted article"""
    try:
        article = Article.query.get_or_404(article_id)
        article.restore()
        db.session.commit()
        logger.info(f"Article {article_id} restored by admin")
        flash(f"Article '{article.title}' has been restored.", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Restore article error for article {article_id}: {str(e)}")
        flash("Error restoring article.", "danger")
    
    return redirect(url_for('admin.admin_dashboard'))


# ============================================================================
# ARTICLE DRAFTS
# ============================================================================

@articles_bp.route('/article/draft', methods=['GET', 'POST'])
@login_required
def create_draft():
    """Create a new article draft"""
    form = ArticleSubmissionForm()
    
    if form.validate_on_submit():
        try:
            article = Article(
                author=current_user.username,
                email=current_user.email,
                title=sanitize_string(form.title.data.strip(), max_length=250),
                content=sanitize_html(form.content.data.strip()),
                category=form.category.data,
                is_draft=True,  # Mark as draft
                status='pending'
            )
            db.session.add(article)
            db.session.commit()
            logger.info(f"Draft created by {current_user.username}")
            flash(f"Draft '{article.title}' saved successfully.", "success")
            return redirect(url_for('articles.view_my_drafts'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Draft creation error for {current_user.username}: {str(e)}")
            flash(f"Error saving draft: {str(e)}", "danger")
    
    return render_template('create_draft.html', form=form)


@articles_bp.route('/article/<int:article_id>/draft/edit', methods=['GET', 'POST'])
@login_required
def edit_draft(article_id):
    """Edit an existing draft"""
    article = Article.query.get_or_404(article_id)
    
    # Only author can edit their draft
    if article.author != current_user.username:
        logger.warning(f"Unauthorized edit attempt on article {article_id} by {current_user.username}")
        flash("You don't have permission to edit this draft.", "danger")
        return redirect(url_for('public.home'))
    
    if not article.is_draft:
        flash("Only drafts can be edited.", "warning")
        return redirect(url_for('articles.read_more', article_id=article_id))
    
    form = ArticleSubmissionForm()
    
    if form.validate_on_submit():
        try:
            article.title = sanitize_string(form.title.data.strip(), max_length=250)
            article.content = sanitize_html(form.content.data.strip())
            article.category = form.category.data
            article.date_submitted = datetime.utcnow()
            db.session.commit()
            logger.info(f"Draft {article_id} updated by {current_user.username}")
            flash("Draft updated successfully.", "success")
            return redirect(url_for('articles.view_my_drafts'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Draft edit error for article {article_id}: {str(e)}")
            flash(f"Error updating draft: {str(e)}", "danger")
    elif request.method == 'GET':
        form.title.data = article.title
        form.content.data = article.content
        form.category.data = article.category
    
    return render_template('edit_draft.html', form=form, article=article)


@articles_bp.route('/article/<int:article_id>/draft/submit', methods=['POST'])
@login_required
def submit_draft(article_id):
    """Submit a draft for publication"""
    article = Article.query.get_or_404(article_id)
    
    # Only author can submit their draft
    if article.author != current_user.username:
        logger.warning(f"Unauthorized submit attempt on article {article_id} by {current_user.username}")
        flash("You don't have permission to submit this draft.", "danger")
        return redirect(url_for('public.home'))
    
    if not article.is_draft:
        flash("Only drafts can be submitted.", "warning")
        return redirect(url_for('articles.read_more', article_id=article_id))
    
    try:
        article.is_draft = False
        article.status = 'pending'
        article.date_submitted = datetime.utcnow()
        db.session.commit()
        logger.info(f"Draft {article_id} submitted by {current_user.username}")
        flash(f"Draft '{article.title}' submitted for approval.", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Draft submit error for article {article_id}: {str(e)}")
        flash(f"Error submitting draft: {str(e)}", "danger")
    
    return redirect(url_for('articles.view_my_drafts'))


@articles_bp.route('/my-drafts')
@login_required
def view_my_drafts():
    """View author's drafts"""
    drafts = Article.query.filter_by(
        author=current_user.username,
        is_draft=True
    ).order_by(Article.date_submitted.desc()).all()
    
    return render_template('my_drafts.html', drafts=drafts)


# ============================================================================
# ARTICLE EDIT & DELETE
# ============================================================================

@articles_bp.route('/article/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    """Edit an approved or pending article"""
    article = Article.query.get_or_404(article_id)
    
    # Check permissions - only author or admin can edit
    if article.author != current_user.username and not current_user.is_admin:
        logger.warning(f"Unauthorized edit attempt on article {article_id} by {current_user.username}")
        flash("You don't have permission to edit this article.", "danger")
        return redirect(url_for('articles.read_more', article_id=article_id))
    
    # Prevent editing of approved/published articles
    if article.status == 'approved':
        logger.warning(f"Edit attempt on approved article {article_id} by {current_user.username}")
        flash("This article has been published and cannot be edited.", "warning")
        return redirect(url_for('articles.read_more', article_id=article_id))
    
    form = ArticleSubmissionForm()
    
    if form.validate_on_submit():
        try:
            article.title = sanitize_string(form.title.data.strip(), max_length=250)
            article.content = sanitize_html(form.content.data.strip())
            article.category = form.category.data
            
            # Update author if provided in form
            if form.author.data:
                article.author = sanitize_string(form.author.data.strip(), max_length=100)
            
            # Update email if provided in form
            if form.email.data:
                article.email = sanitize_string(form.email.data.strip(), max_length=120)
            
            # Handle file uploads
            if form.cover_image.data:
                is_valid, error_msg = validate_image_file(form.cover_image.data)
                if not is_valid:
                    flash(error_msg, 'danger')
                    return render_template('edit_article.html', form=form, article=article)
                
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                
                unique_filename = get_safe_filename(form.cover_image.data.filename)
                filepath = os.path.join(upload_folder, unique_filename)
                form.cover_image.data.save(filepath)
                article.image_filename = unique_filename
            
            if form.document.data:
                is_valid, error_msg = validate_document_file(form.document.data)
                if not is_valid:
                    flash(error_msg, 'danger')
                    return render_template('edit_article.html', form=form, article=article)
                
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                
                unique_filename = get_safe_filename(form.document.data.filename)
                filepath = os.path.join(upload_folder, unique_filename)
                form.document.data.save(filepath)
                article.document_filename = unique_filename
            
            db.session.commit()
            logger.info(f"Article {article_id} updated by {current_user.username}")
            flash("Article updated successfully!", "success")
            return redirect(url_for('articles.read_more', article_id=article_id))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Article edit error for article {article_id}: {str(e)}")
            flash(f"Error updating article: {str(e)}", "danger")
    elif request.method == 'GET':
        form.title.data = article.title
        form.content.data = article.content
        form.category.data = article.category
    
    return render_template('edit_article.html', form=form, article=article)


@articles_bp.route('/article/<int:article_id>/delete', methods=['POST'])
@login_required
def delete_article(article_id):
    """Delete an article (soft delete)"""
    article = Article.query.get_or_404(article_id)
    
    # Check permissions - only author or admin can delete
    if article.author != current_user.username and not current_user.is_admin:
        logger.warning(f"Unauthorized delete attempt on article {article_id} by {current_user.username}")
        flash("You don't have permission to delete this article.", "danger")
        return redirect(url_for('articles.read_more', article_id=article_id))
    
    # Prevent deletion of approved/published articles (except admins)
    if article.status == 'approved' and not current_user.is_admin:
        logger.warning(f"Delete attempt on approved article {article_id} by {current_user.username}")
        flash("This article has been published and cannot be deleted.", "warning")
        return redirect(url_for('articles.read_more', article_id=article_id))
    
    try:
        article_title = article.title
        article.soft_delete()
        db.session.commit()
        logger.info(f"Article {article_id} deleted by {current_user.username}")
        flash(f"Article '{article_title}' has been deleted.", "success")
        return redirect(url_for('public.home'))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Article delete error for article {article_id}: {str(e)}")
        flash("Error deleting article.", "danger")
        return redirect(url_for('articles.read_more', article_id=article_id))
