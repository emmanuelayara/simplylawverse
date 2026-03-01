#!/usr/bin/env python
"""
Test article approval and disapproval functionality
"""
import sys
sys.path.insert(0, '.')

from app import app
from extensions import db
from models import Article, User
from werkzeug.security import check_password_hash

print("\n" + "="*70)
print("ARTICLE APPROVAL/DISAPPROVAL FUNCTIONALITY TEST")
print("="*70)

with app.app_context():
    # Clear test articles
    db.session.query(Article).filter(Article.title.like('TEST%')).delete()
    
    # Create test articles
    print("\n[1] Creating test articles...")
    a1 = Article(
        title="TEST_ARTICLE_1",
        content="Content for test article 1",
        author="Test Author",
        email="test@example.com",
        status='pending',
        category='Technology'
    )
    
    a2 = Article(
        title="TEST_ARTICLE_2",
        content="Content for test article 2",
        author="Test Author",
        email="test@example.com",
        status='pending',
        category='Technology'
    )
    
    db.session.add_all([a1, a2])
    db.session.commit()
    
    print(f"    ✓ Article 1 (ID {a1.id}): {a1.status}")
    print(f"    ✓ Article 2 (ID {a2.id}): {a2.status}")
    
    # Create test client
    client = app.test_client()
    
    # Get login page for CSRF token
    print("\n[2] Getting login page...")
    login_page_resp = client.get('/admin/login')
    print(f"    ✓ Login page status: {login_page_resp.status_code}")
    
    import re
    match = re.search(r'name="csrf_token"[^>]*value="([^"]*)"', login_page_resp.data.decode())
    csrf_token = match.group(1) if match else ''
    print(f"    ✓ CSRF token extracted: {csrf_token[:20] if csrf_token else 'NOT FOUND'}...")
    
    # Login
    print("\n[3] Logging in with Flask test client...")
    with client:
        # Use Flask-Login's login_user directly in the test
        admin_user = User.query.filter_by(is_admin=True).first()
        
        from flask_login import login_user
        with client.session_transaction() as sess:
            login_user(admin_user)
        
        print(f"    ✓ Admin user manually logged in: {admin_user.username}")
        
        # Verify we can access dashboard
        dash_resp = client.get('/admin/dashboard')
        print(f"    ✓ Dashboard status after login: {dash_resp.status_code}")
        
        # Test approve
        print("\n[4] Testing APPROVE functionality...")
        approve_resp = client.post(f'/admin/approve/{a1.id}', follow_redirects=False)
        print(f"    ✓ Approve endpoint response: {approve_resp.status_code}")
        
        db.session.refresh(a1)
        print(f"    ✓ Article 1 status after approve: {a1.status}")
        if a1.status == 'approved':
            print("    ✓✓ SUCCESS: Article was APPROVED!")
        else:
            print(f"    ✗✗ FAILED: Article status is {a1.status}")
        
        # Test disapprove
        print("\n[5] Testing DISAPPROVE functionality...")
        disapprove_resp = client.post(f'/admin/disapprove/{a2.id}', follow_redirects=False)
        print(f"    ✓ Disapprove endpoint response: {disapprove_resp.status_code}")
        
        db.session.refresh(a2)
        print(f"    ✓ Article 2 status after disapprove: {a2.status}")
        if a2.status == 'disapproved':
            print("    ✓✓ SUCCESS: Article was DISAPPROVED!")
        else:
            print(f"    ✗✗ FAILED: Article status is {a2.status}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70 + "\n")
