from flask import Flask
import os
from extensions import db, login_manager  # Remove 'migrate' from import

def create_app():
    app = Flask(__name__)
    # Get the absolute path to the project directory
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
    
    # ------------------ CONFIG ------------------
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    
    # Upload folder
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder
    
    # ------------------ INIT EXTENSIONS ------------------
    db.init_app(app)
    login_manager.init_app(app)
    # Remove this line: migrate.init_app(app, db)


    # Import models HERE (after db.init_app but before db.create_all)
    from models import User, Article, Comment, Message, Visit
    
    # ------------------ CREATE TABLES ------------------
    with app.app_context():
        db.create_all()  # This creates all tables defined in models.py
    
    # ------------------ REGISTER ROUTES ------------------
    from routes import register_routes
    register_routes(app)
    
    return app
    
# 👇 Needed for `flask run`
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)