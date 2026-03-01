# routes.py
import os
from datetime import datetime, timedelta

from flask import (
    render_template, redirect, url_for, flash, request, current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message as MailMessage
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_

from extensions import db, login_manager, mail, limiter
from forms import (
    LoginForm, ArticleSubmissionForm, AdminRegisterForm,
    ContactForm, CommentForm, ForgotPasswordForm, ResetPasswordForm
)
from models import User, Article, Comment, Message, Visit
from security import (
    admin_required, sanitize_html, sanitize_string, validate_email,
    validate_image_file, validate_document_file, get_safe_filename,
    ALLOWED_IMAGE_EXTENSIONS, ALLOWED_DOCUMENT_EXTENSIONS
)

# ✅ Legacy function - kept for backward compatibility
def allowed_file(filename):
    """Legacy function - use validate_image_file() instead"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


# ✅ All routes are now registered inside this function
def register_routes(app):

    # ------------------------------------
    # 🔐 User Loader
    # ------------------------------------
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ------------------------------------
    # 📁 File Upload
    # ------------------------------------
    @app.route('/upload', methods=['GET', 'POST'])
    def upload_cover_image():
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
                    return redirect(request.url)
                
                # Generate safe filename and save
                unique_filename = get_safe_filename(file.filename)
                filepath = os.path.join(upload_folder, unique_filename)
                file.save(filepath)
                
                flash('Upload successful!', 'success')
                return redirect(url_for('upload_cover_image'))
                
            except Exception as e:
                flash(f'An error occurred during upload: {str(e)}', 'danger')
                print(f"❌ File upload error: {str(e)}")
                return redirect(request.url)

        return render_template('submit_article.html')

    # ------------------------------------
    # 🏠 Home Page
    # ------------------------------------
    @app.route('/')
    def home():
        page = request.args.get('page', 1, type=int)
        category = request.args.get('category')
        search_query = request.args.get('search', '', type=str)
        per_page = 6

        query = Article.query.filter(Article.status == 'approved')

        if category:
            query = query.filter(Article.category == category)

        if search_query:
            query = query.filter(
                or_(
                    Article.title.ilike(f'%{search_query}%'),
                    Article.content.ilike(f'%{search_query}%')
                )
            )

        articles = query.order_by(Article.date_posted.desc()) \
                        .paginate(page=page, per_page=per_page)

        categories = db.session.query(Article.category).distinct().all()

        return render_template(
            'home.html',
            articles=articles,
            categories=categories,
            selected_category=category,
            search_query=search_query,
        )

    # ------------------------------------
    # 🛠️ Admin Approvals
    # ------------------------------------
    @app.route('/admin/approve/<int:article_id>')
    @login_required
    @admin_required
    def approve_article(article_id):
        try:
            article = Article.query.get_or_404(article_id)
            article.status = 'approved'
            db.session.commit()
            flash('Article approved successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error approving article.', 'danger')
            print(f"❌ Approve article error: {str(e)}")
        
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/disapprove/<int:article_id>')
    @login_required
    @admin_required
    def disapprove_article(article_id):
        try:
            article = Article.query.get_or_404(article_id)
            article.status = 'disapproved'
            db.session.commit()
            flash('Article disapproved.', 'warning')
        except Exception as e:
            db.session.rollback()
            flash('Error disapproving article.', 'danger')
            print(f"❌ Disapprove article error: {str(e)}")
        
        return redirect(url_for('admin_dashboard'))

    # ------------------------------------
    # 📖 Article Views
    # ------------------------------------
    @app.route('/article/<int:article_id>')
    def view_article(article_id):
        article = Article.query.get_or_404(article_id)
        return render_template('view_article.html', article=article)

    @app.route('/read/<int:article_id>')
    @app.route('/read/<int:article_id>/page/<int:page>')
    def read_more(article_id, page=1):
        article = Article.query.get_or_404(article_id)
        # ✅ Don't show soft-deleted articles
        if article.is_deleted():
            flash("This article is no longer available.", "warning")
            return redirect(url_for('home'))
        
        article.views = article.views + 1 if article.views else 1
        db.session.commit()

        # ✅ Create visit with full tracking data
        visitor_hash = Visit.generate_visitor_hash(
            request.remote_addr,
            request.user_agent.string
        )
        
        visit = Visit(
            article_id=article.id,
            user_id=current_user.id if current_user.is_authenticated else None,
            session_id=request.cookies.get('session'),
            ip_address=request.remote_addr,
            visitor_hash=visitor_hash,
            user_agent=request.user_agent.string,
            referer=request.referrer,
            timestamp=datetime.utcnow(),
            duration_seconds=0  # Will be updated by JavaScript
        )
        db.session.add(visit)
        db.session.commit()

        # ✅ Paginate comments - show top-level comments with pagination
        COMMENTS_PER_PAGE = 10
        
        # Get only non-deleted, top-level comments (parent_id IS NULL)
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

    # ------------------------------------
    # ❤️ Like System
    # ------------------------------------
    @app.route('/like/<int:article_id>', methods=['POST'])
    def like_article(article_id):
        try:
            article = Article.query.get_or_404(article_id)
            article.likes = (article.likes or 0) + 1
            db.session.commit()
            flash('You liked the article.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error liking article. Please try again.', 'danger')
            print(f"❌ Like article error: {str(e)}")
        
        return redirect(request.referrer or url_for('read_more', article_id=article_id))

    # ------------------------------------
    # 📝 Article Submission
    # ------------------------------------
    @app.route('/submit', methods=['GET', 'POST'])
    def submit_article():
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
            "Real Estate Law", "Transportation Law", "Cyber Law",
            "Data Protection and Privacy Law", "Space Law", "Sports and Entertainment Law",
            "Media and Communications Law", "Education Law", "Agricultural Law",
            "Animal Law", "Maritime and Admiralty Law", "Immigration Law",
            "Tax Law", "Military Law", "Bankruptcy Law",
            "Consumer Protection Law", "Public Interest Law", "Customary and Indigenous Law"
        ]]

        if form.validate_on_submit():
            app.logger.info(f"✅ Form validation passed")
            app.logger.info(f"DEBUG: request.files keys: {list(request.files.keys())}")
            app.logger.info(f"DEBUG: request.files: {request.files}")
            try:
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)

                # Sanitize all text inputs before storing
                sanitized_author = sanitize_string(form.author.data, max_length=100)
                sanitized_title = sanitize_string(form.title.data, max_length=200)
                sanitized_content = sanitize_html(form.content.data)
                sanitized_email = sanitize_string(form.email.data, max_length=120)
                
                # Validate sanitized email
                if not validate_email(sanitized_email):
                    flash('Invalid email address.', 'danger')
                    return render_template('submit_article.html', form=form)

                cover_image_filename = None
                print(f"DEBUG: request.files keys: {list(request.files.keys())}")
                print(f"DEBUG: 'cover_image' in request.files: {'cover_image' in request.files}")
                if 'cover_image' in request.files:
                    print(f"DEBUG: request.files['cover_image']: {request.files['cover_image']}")
                    print(f"DEBUG: filename: {request.files['cover_image'].filename}")
                if 'cover_image' in request.files and request.files['cover_image'].filename:
                    cover_image = request.files['cover_image']
                    print(f"DEBUG: Processing cover_image: {cover_image.filename}")
                    
                    # Validate file
                    is_valid, error_msg = validate_image_file(cover_image)
                    if not is_valid:
                        flash(f'Cover image error: {error_msg}', 'danger')
                        return render_template('submit_article.html', form=form)
                    
                    try:
                        cover_image_filename = get_safe_filename(cover_image.filename)
                        full_path = os.path.join(upload_folder, cover_image_filename)
                        cover_image.save(full_path)
                        print(f"✅ Saved cover image: {cover_image_filename}")
                    except Exception as e:
                        flash(f'Error uploading cover image: {str(e)}', 'danger')
                        print(f"❌ Cover image upload error: {str(e)}")
                        return render_template('submit_article.html', form=form)

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
                        document.save(os.path.join(upload_folder, document_filename))
                        print(f"✅ Saved document: {document_filename}")
                    except Exception as e:
                        flash(f'Error uploading document: {str(e)}', 'danger')
                        print(f"❌ Document upload error: {str(e)}")
                        return render_template('submit_article.html', form=form)

                article = Article(
                    author=sanitized_author,
                    email=sanitized_email,
                    title=sanitized_title,
                    content=sanitized_content,
                    category=form.category.data,
                    cover_image=cover_image_filename,
                    document_filename=document_filename
                )

                db.session.add(article)
                db.session.commit()
                flash('Article submitted successfully and is awaiting approval.', 'success')
                return redirect(url_for('home'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error submitting article: {str(e)}', 'danger')
                print(f"❌ Article submission error: {str(e)}")
                return render_template('submit_article.html', form=form)
        
        else:
            if request.method == 'POST':
                print("❌ Form validation FAILED!")
                print(f"Form errors: {form.errors}")
                # Flash the errors to the user
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f"{field}: {error}", 'danger')

        return render_template('submit_article.html', form=form)

    # ------------------------------------
    # 👤 Admin Registration & Login
    # ------------------------------------
    @app.route('/admin/register', methods=['GET', 'POST'])
    @limiter.limit("5 per day")  # Limit registration attempts
    def register_admin():
        form = AdminRegisterForm()
        if form.validate_on_submit():
            # Sanitize inputs
            username = sanitize_string(form.username.data, max_length=150)
            email = sanitize_string(form.email.data, max_length=100)
            
            # Check if username already exists
            if User.query.filter_by(username=username).first():
                flash("Username already exists.", "danger")
                return redirect(url_for('register_admin'))
            
            # Check if email already exists
            if User.query.filter_by(email=email).first():
                flash("Email already registered.", "danger")
                return redirect(url_for('register_admin'))

            try:
                hashed_password = generate_password_hash(form.password.data)
                new_admin = User(
                    username=username,
                    email=email,
                    password=hashed_password,
                    is_admin=True
                )
                db.session.add(new_admin)
                db.session.commit()
                flash("Admin registered successfully!", "success")
                return redirect(url_for('admin_login'))
            except Exception as e:
                db.session.rollback()
                flash("An error occurred during registration. Please try again.", "danger")
                print(f"❌ Registration error: {str(e)}")
        return render_template('admin_register.html', form=form)

    @app.route('/admin/login', methods=['GET', 'POST'])
    @limiter.limit("10 per minute")  # Rate limit login attempts
    def admin_login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data) and user.is_admin:
                login_user(user)
                return redirect(url_for('admin_dashboard'))
            # Generic message to prevent user enumeration
            flash('Invalid credentials or not an admin.', 'danger')
        return render_template('admin_login.html', form=form)

    # ------------------------------------
    # � Forgot Password & Reset
    # ------------------------------------
    def send_reset_email(user):
        """Send password reset email to user"""
        token = user.get_reset_token()
        reset_url = url_for('reset_password', token=token, _external=True)
        
        try:
            msg = MailMessage(
                subject='Password Reset Request',
                recipients=[user.email],
                body=f'''To reset your password, visit the following link:
{reset_url}

This link will expire in 30 minutes.

If you did not make this request, please ignore this email.
'''
            )
            mail.send(msg)
            return True
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            return False

    @app.route('/forgot-password', methods=['GET', 'POST'])
    @limiter.limit("5 per hour")  # Rate limit password reset requests
    def forgot_password():
        """Handle forgot password request"""
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        
        form = ForgotPasswordForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            
            if user:
                if send_reset_email(user):
                    flash('An email has been sent with instructions to reset your password.', 'info')
                else:
                    flash('Email service is currently unavailable. Please try again later.', 'danger')
            else:
                # Don't reveal if email exists (security best practice)
                flash('An email has been sent with instructions to reset your password.', 'info')
            
            return redirect(url_for('admin_login'))
        
        return render_template('forgot_password.html', form=form)

    @app.route('/reset-password/<token>', methods=['GET', 'POST'])
    def reset_password(token):
        """Handle password reset with token"""
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        
        user = User.verify_reset_token(token)
        if not user:
            flash('That is an invalid or expired token.', 'danger')
            return redirect(url_for('admin_login'))
        
        form = ResetPasswordForm()
        if form.validate_on_submit():
            try:
                hashed_password = generate_password_hash(form.password.data)
                user.password = hashed_password
                db.session.commit()
                flash('Your password has been reset! You can now log in with your new password.', 'success')
                return redirect(url_for('admin_login'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred. Please try again.', 'danger')
                print(f"❌ Password reset error: {str(e)}")
        
        return render_template('reset_password.html', form=form)

    # ------------------------------------
    # �📊 Admin Dashboard
    # ------------------------------------
    @app.route('/admin/dashboard')
    @login_required
    @admin_required
    def admin_dashboard():
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

    # ------------------------------------
    # 🔓 Logout
    # ------------------------------------
    @app.route('/admin/logout')
    @login_required
    def admin_logout():
        logout_user()
        flash('Logged out.', 'info')
        return redirect(url_for('home'))

    # ------------------------------------
    # 📄 Misc Routes
    # ------------------------------------
    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/contact', methods=['GET', 'POST'])
    @limiter.limit("5 per hour")  # Rate limit contact form submissions
    def contact():
        form = ContactForm()
        if form.validate_on_submit():
            try:
                # Sanitize all inputs before storing
                sanitized_name = sanitize_string(form.name.data, max_length=100)
                sanitized_email = sanitize_string(form.email.data, max_length=120)
                sanitized_message = sanitize_html(form.message.data)
                
                # Validate email
                if not validate_email(sanitized_email):
                    flash("Invalid email address.", "danger")
                    return render_template('contact.html', form=form)
                
                new_message = Message(
                    name=sanitized_name,
                    email=sanitized_email,
                    message=sanitized_message
                )
                db.session.add(new_message)
                db.session.commit()
                flash("Your message has been sent successfully!", "success")
                return redirect(url_for('contact'))
            except Exception as e:
                db.session.rollback()
                flash("An error occurred while sending your message. Please try again.", "danger")
                print(f"❌ Contact form error: {str(e)}")
        return render_template('contact.html', form=form)

    @app.route('/messages')
    @login_required
    @admin_required
    def view_messages():
        messages = Message.query.order_by(Message.date_sent.desc()).all()
        return render_template('messages.html', messages=messages)
    @app.route('/article/<int:article_id>/comment', methods=['POST'])
    @limiter.limit("10 per hour")  # Rate limit comment submissions
    def comment(article_id):
        try:
            # Validate article exists
            article = Article.query.get_or_404(article_id)
            
            # Get form data with validation and sanitization
            name = sanitize_string(request.form.get('name', '').strip(), max_length=100)
            email = sanitize_string(request.form.get('email', '').strip(), max_length=120)
            content = sanitize_html(request.form.get('comment', '').strip())
            
            # Validate required fields
            if not name or not content:
                flash("Name and comment are required.", "danger")
                return redirect(url_for('read_more', article_id=article_id))
            
            # Validate name length
            if len(name) < 2:
                flash("Name must be at least 2 characters.", "danger")
                return redirect(url_for('read_more', article_id=article_id))
            
            # Validate comment length
            if len(content) < 2 or len(content) > 5000:
                flash("Comment must be between 2 and 5000 characters.", "danger")
                return redirect(url_for('read_more', article_id=article_id))
            
            # Validate email if provided
            if email:
                if not validate_email(email):
                    flash("Invalid email address format.", "danger")
                    return redirect(url_for('read_more', article_id=article_id))
            
            new_comment = Comment(
                name=name,
                email=email if email else 'anonymous',  # ✅ Always has a value, never null
                content=content,
                article_id=article_id
            )
            db.session.add(new_comment)
            db.session.commit()
            flash("Comment posted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while posting your comment. Please try again.", "danger")
            print(f"❌ Comment error: {str(e)}")
        
        return redirect(url_for('read_more', article_id=article_id))

    # ------------------------------------
    # 🗑️ Soft Delete & Restore
    # ------------------------------------
    @app.route('/article/<int:article_id>/delete', methods=['POST'])
    @login_required
    @admin_required
    def soft_delete_article(article_id):
        """Soft delete an article - can be restored later"""
        try:
            article = Article.query.get_or_404(article_id)
            article.soft_delete()
            db.session.commit()
            flash(f"Article '{article.title}' soft deleted. You can restore it from admin panel.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting article: {str(e)}", "danger")
        
        return redirect(url_for('admin_dashboard'))

    @app.route('/article/<int:article_id>/restore', methods=['POST'])
    @login_required
    @admin_required
    def restore_article(article_id):
        """Restore a soft-deleted article"""
        try:
            article = Article.query.get_or_404(article_id)
            article.restore()
            article.status = 'pending'  # Reset to pending for review
            db.session.commit()
            flash(f"Article '{article.title}' restored successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error restoring article: {str(e)}", "danger")
        
        return redirect(url_for('admin_dashboard'))

    @app.route('/comment/<int:comment_id>/delete', methods=['POST'])
    @login_required
    def soft_delete_comment(comment_id):
        """Soft delete a comment - can be restored later"""
        try:
            comment = Comment.query.get_or_404(comment_id)
            
            # ✅ Allow author or admin to delete
            if current_user.is_admin or current_user.username == comment.name:
                comment.soft_delete()
                db.session.commit()
                flash("Comment deleted successfully. You can restore it later.", "success")
            else:
                flash("You don't have permission to delete this comment.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting comment: {str(e)}", "danger")
        
        return redirect(request.referrer or url_for('home'))

    @app.route('/comment/<int:comment_id>/restore', methods=['POST'])
    @login_required
    def restore_comment(comment_id):
        """Restore a soft-deleted comment"""
        try:
            comment = Comment.query.get_or_404(comment_id)
            
            # ✅ Allow author or admin to restore
            if current_user.is_admin or current_user.username == comment.name:
                comment.restore()
                db.session.commit()
                flash("Comment restored successfully.", "success")
            else:
                flash("You don't have permission to restore this comment.", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"Error restoring comment: {str(e)}", "danger")
        
        return redirect(request.referrer or url_for('home'))

    # ------------------------------------
    # 📝 Article Drafts
    # ------------------------------------
    @app.route('/article/draft', methods=['GET', 'POST'])
    @login_required
    def create_draft():
        """Create or update article draft"""
        form = ArticleSubmissionForm()
        
        if form.validate_on_submit():
            try:
                article = Article(
                    author=current_user.username,
                    email=current_user.email,
                    title=form.title.data,
                    content=form.content.data,
                    category=form.category.data,
                    is_draft=True,  # ✅ Mark as draft
                    status='pending'  # Drafts start as pending
                )
                db.session.add(article)
                db.session.commit()
                flash(f"Draft '{article.title}' saved successfully.", "success")
                return redirect(url_for('view_my_drafts'))
            except Exception as e:
                db.session.rollback()
                flash(f"Error saving draft: {str(e)}", "danger")
        
        return render_template('create_draft.html', form=form)

    @app.route('/article/<int:article_id>/draft/edit', methods=['GET', 'POST'])
    @login_required
    def edit_draft(article_id):
        """Edit article draft"""
        article = Article.query.get_or_404(article_id)
        
        # ✅ Only author can edit their draft
        if article.author != current_user.username:
            flash("You don't have permission to edit this draft.", "danger")
            return redirect(url_for('home'))
        
        if not article.is_draft:
            flash("Only drafts can be edited.", "warning")
            return redirect(url_for('view_article', article_id=article_id))
        
        form = ArticleSubmissionForm()
        
        if form.validate_on_submit():
            try:
                article.title = form.title.data
                article.content = form.content.data
                article.category = form.category.data
                article.date_submitted = datetime.utcnow()
                db.session.commit()
                flash("Draft updated successfully.", "success")
                return redirect(url_for('view_my_drafts'))
            except Exception as e:
                db.session.rollback()
                flash(f"Error updating draft: {str(e)}", "danger")
        elif request.method == 'GET':
            form.title.data = article.title
            form.content.data = article.content
            form.category.data = article.category
        
        return render_template('edit_draft.html', form=form, article=article)

    @app.route('/article/<int:article_id>/draft/submit', methods=['POST'])
    @login_required
    def submit_draft(article_id):
        """Submit draft for publication"""
        article = Article.query.get_or_404(article_id)
        
        # ✅ Only author can submit their draft
        if article.author != current_user.username:
            flash("You don't have permission to submit this draft.", "danger")
            return redirect(url_for('home'))
        
        if not article.is_draft:
            flash("Only drafts can be submitted.", "warning")
            return redirect(url_for('view_article', article_id=article_id))
        
        try:
            article.is_draft = False
            article.status = 'pending'
            article.date_submitted = datetime.utcnow()
            db.session.commit()
            flash(f"Draft '{article.title}' submitted for approval.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error submitting draft: {str(e)}", "danger")
        
        return redirect(url_for('view_my_drafts'))

    @app.route('/my-drafts')
    @login_required
    def view_my_drafts():
        """View author's drafts"""
        drafts = Article.query.filter_by(
            author=current_user.username,
            is_draft=True
        ).order_by(Article.date_submitted.desc()).all()
        
        return render_template('my_drafts.html', drafts=drafts)

    # ------------------------------------
    # 💬 Threaded Comments
    # ------------------------------------
    @app.route('/comment/<int:parent_id>/reply', methods=['POST'])
    @limiter.limit("10 per hour")
    def reply_to_comment(parent_id):
        """Reply to a specific comment (threading)"""
        try:
            parent_comment = Comment.query.get_or_404(parent_id)
            article_id = parent_comment.article_id
            
            # Get form data
            name = sanitize_string(request.form.get('name', '').strip(), max_length=100)
            email = sanitize_string(request.form.get('email', '').strip(), max_length=120)
            content = sanitize_html(request.form.get('reply', '').strip())
            
            # Validate required fields
            if not name or not content:
                flash("Name and reply are required.", "danger")
                return redirect(url_for('read_more', article_id=article_id))
            
            if len(content) < 2 or len(content) > 5000:
                flash("Reply must be between 2 and 5000 characters.", "danger")
                return redirect(url_for('read_more', article_id=article_id))
            
            if email and not validate_email(email):
                flash("Invalid email address format.", "danger")
                return redirect(url_for('read_more', article_id=article_id))
            
            # ✅ Create reply comment with parent_id set
            reply = Comment(
                name=name,
                email=email if email else 'anonymous',
                content=content,
                article_id=article_id,
                parent_id=parent_id  # ✅ Link to parent comment
            )
            db.session.add(reply)
            db.session.commit()
            flash("Reply posted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error posting reply: {str(e)}", "danger")
            print(f"❌ Reply error: {str(e)}")
        
        return redirect(url_for('read_more', article_id=article_id, _anchor=f'comment-{parent_id}'))
