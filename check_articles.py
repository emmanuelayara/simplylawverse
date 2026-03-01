#!/usr/bin/env python
"""Check article cover images in database"""
from models import Article, db
from app import app

with app.app_context():
    articles = Article.query.all()
    print(f"\n✓ Total articles: {len(articles)}\n")
    
    for article in articles[:10]:  # First 10
        print(f"ID: {article.id}")
        print(f"  Title: {article.title[:50]}")
        print(f"  Cover Image: {article.cover_image}")
        print(f"  Status: {article.status}")
        print()
    
    # Count articles with cover images
    with_cover = Article.query.filter(Article.cover_image != None).count()
    without_cover = Article.query.filter(Article.cover_image == None).count()
    
    print(f"\n✓ Articles WITH cover_image: {with_cover}")
    print(f"✗ Articles WITHOUT cover_image: {without_cover}")
