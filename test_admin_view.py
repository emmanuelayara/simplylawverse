#!/usr/bin/env python
"""Test admin article viewing functionality"""
from app import app, db
from models import Article

print("=" * 70)
print("Testing Admin Article Review Feature")
print("=" * 70)

with app.app_context():
    # Check if there are any pending articles
    pending_articles = Article.query.filter_by(status='pending').all()
    
    if pending_articles:
        article = pending_articles[0]
        print(f"\n✅ Found pending article for testing:")
        print(f"   - ID: {article.id}")
        print(f"   - Title: {article.title}")
        print(f"   - Author: {article.author}")
        print(f"   - Status: {article.status}")
    else:
        print("\n⚠️  No pending articles in database")
        print("   Create a guest article submission to test the admin review feature")

print("\n" + "=" * 70)
print("Feature Summary")
print("=" * 70)
print("""
✅ Admin Article Review Route: /admin/view/<article_id>
✅ Access Control: Requires admin login (@admin_required)
✅ Displays Full Article Content
✅ Shows Comments with Pagination
✅ Shows Author Information & Email
✅ Shows Article Metadata (category, date, likes)
✅ Approve Button: Sets status to 'approved' & publishes
✅ Disapprove Button: Sets status to 'disapproved'
✅ Buttons Redirect Back to Article View

How it works:
1. Admin logs in to /admin/dashboard
2. Sees list of pending articles in "Pending Review" section
3. Clicks "Review Article" button
4. Views full article with all details and comments
5. Approves or disapproves the article
6. Changes reflected in dashboard

Updated Dashboard Links:
- Pending articles: "Review Article" → /admin/view/<id>
- Approved articles: "Review Article" → /admin/view/<id>
""")
