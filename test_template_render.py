#!/usr/bin/env python
"""Test if cover images display in templates"""
from app import create_app
from models import Article

app = create_app()

with app.test_request_context():
    from flask import url_for
    
    with app.app_context():
        # Get the article with cover image we just created
        article = Article.query.filter_by(id=9).first()
        
        if article and article.cover_image:
            image_url = url_for('static', filename='uploads/' + article.cover_image)
            print(f"\n✅ Article {article.id}: {article.title}")
            print(f"   Cover image filename: {article.cover_image}")
            print(f"   Generated URL: {image_url}")
            print(f"   Full URL would be: http://localhost:5000{image_url}")
            
            # Check if file exists
            import os
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], article.cover_image)
            print(f"   File exists on disk: {os.path.exists(full_path)}")
            
            # Test what the template will render
            print(f"\n   Template will render:")
            print(f'   <img src="{image_url}" alt="{article.title}" />')
        else:
            print("❌ Article not found or no cover image")
