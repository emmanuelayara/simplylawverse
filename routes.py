# routes.py
import os
from datetime import datetime, timedelta

from flask import (
    render_template, redirect, url_for, flash, request, current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_

from extensions import db, login_manager
from forms import (
    LoginForm, ArticleSubmissionForm, AdminRegisterForm,
    ContactForm, CommentForm
)
from models import User, Article, Comment, Message, Visit

# ✅ Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
            if 'cover_image' not in request.files:
                flash('No file part')
                return redirect(request.url)

            file = request.files['cover_image']

            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
                flash('Upload successful!')
                return redirect(url_for('upload_cover_image'))

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
    def approve_article(article_id):
        article = Article.query.get_or_404(article_id)
        article.status = 'approved'
        db.session.commit()
        flash('Article approved successfully.', 'success')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/disapprove/<int:article_id>')
    def disapprove_article(article_id):
        article = Article.query.get_or_404(article_id)
        article.status = 'disapproved'
        db.session.commit()
        flash('Article disapproved.', 'warning')
        return redirect(url_for('admin_dashboard'))

    # ------------------------------------
    # 📖 Article Views
    # ------------------------------------
    @app.route('/article/<int:article_id>')
    def view_article(article_id):
        article = Article.query.get_or_404(article_id)
        return render_template('view_article.html', article=article)

    @app.route('/read/<int:article_id>')
    def read_more(article_id):
        article = Article.query.get_or_404(article_id)
        article.views = article.views + 1 if article.views else 1
        db.session.commit()

        visit = Visit(article_id=article.id)
        db.session.add(visit)
        db.session.commit()

        form = CommentForm()
        comments = Comment.query.filter_by(article_id=article_id).order_by(Comment.date_posted.desc()).all()
        return render_template('read_more.html', article=article, comments=comments)

    # ------------------------------------
    # ❤️ Like System
    # ------------------------------------
    @app.route('/like/<int:article_id>', methods=['POST'])
    def like_article(article_id):
        article = Article.query.get_or_404(article_id)
        article.likes = (article.likes or 0) + 1
        db.session.commit()
        flash('You liked the article.', 'success')
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
            print("✅ Form validated successfully!")
            
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)

            cover_image_filename = None
            if 'cover_image' in request.files:
                cover_image = request.files['cover_image']
                if cover_image and cover_image.filename != '':
                    cover_image_filename = secure_filename(cover_image.filename)
                    full_path = os.path.join(upload_folder, cover_image_filename)
                    cover_image.save(full_path)
                    print(f"✅ Saved cover image: {cover_image_filename}")

            document_filename = None
            if 'document' in request.files:
                document = request.files['document']
                if document and document.filename != '':
                    document_filename = secure_filename(document.filename)
                    document.save(os.path.join(upload_folder, document_filename))

            article = Article(
                author=form.author.data,
                email=form.email.data,
                title=form.title.data,
                content=form.content.data,
                category=form.category.data,
                cover_image=cover_image_filename,
                document_filename=document_filename
            )

            db.session.add(article)
            db.session.commit()
            flash('Article submitted successfully and is awaiting approval.', 'success')
            return redirect(url_for('home'))
        
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
    def register_admin():
        form = AdminRegisterForm()
        if form.validate_on_submit():
            if User.query.filter_by(username=form.username.data).first():
                flash("Username already exists.", "danger")
                return redirect(url_for('register_admin'))

            hashed_password = generate_password_hash(form.password.data)
            new_admin = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password,
                is_admin=True
            )
            db.session.add(new_admin)
            db.session.commit()
            flash("Admin registered successfully!", "success")
            return redirect(url_for('admin_login'))
        return render_template('admin_register.html', form=form)

    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data) and user.is_admin:
                login_user(user)
                return redirect(url_for('admin_dashboard'))
            flash('Invalid credentials or not an admin.', 'danger')
        return render_template('admin_login.html', form=form)

    # ------------------------------------
    # 📊 Admin Dashboard
    # ------------------------------------
    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        if not current_user.is_admin:
            flash('Access denied.', 'danger')
            return redirect(url_for('home'))

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
    def contact():
        form = ContactForm()
        if form.validate_on_submit():
            new_message = Message(
                name=form.name.data,
                email=form.email.data,
                message=form.message.data
            )
            db.session.add(new_message)
            db.session.commit()
            flash("Your message has been sent successfully!", "success")
            return redirect(url_for('contact'))
        return render_template('contact.html', form=form)

    @app.route('/messages')
    @login_required
    def view_messages():
        messages = Message.query.order_by(Message.date_sent.desc()).all()
        return render_template('messages.html', messages=messages)

    @app.route('/article/<int:article_id>/comment', methods=['POST'])
    def comment(article_id):
        name = request.form['name']
        content = request.form['comment']
        comment = Comment(name=name, content=content, article_id=article_id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('read_more', article_id=article_id))
