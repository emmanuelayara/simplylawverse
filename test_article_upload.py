#!/usr/bin/env python
"""Test article submission with cover image"""
import os
import re
from app import create_app
from io import BytesIO
from PIL import Image

app = create_app()

# Create a test image
def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    img_io.name = 'test_cover.jpg'
    return img_io

# Test form submission
with app.test_client() as client:
    print("=" * 60)
    print("TESTING ARTICLE SUBMISSION WITH COVER IMAGE")
    print("=" * 60)
    
    # First, get the form to extract CSRF token
    print("\n[1] Getting form page...")
    response = client.get('/submit')
    print(f"    Status: {response.status_code}")
    
    # Extract CSRF token
    form_data_text = response.get_data(as_text=True)
    csrf_match = re.search(r'value="([a-f0-9]+)".*csrf_token', form_data_text, re.DOTALL)
    if not csrf_match:
        # Try alternative pattern
        csrf_match = re.search(r'csrf_token.*?value="([^"]+)"', form_data_text, re.DOTALL)
    
    csrf_token = csrf_match.group(1) if csrf_match else None
    print(f"    CSRF token: {csrf_token[:20] if csrf_token else 'NOT FOUND'}...")
    
    # Prepare form data
    test_image = create_test_image()
    
    form_data = {
        'author': 'Test Author',
        'email': 'test@example.com',
        'title': 'Test Article with Cover Image 2',
        'content': 'This is a test article with a cover image. ' * 50,  # Ensure > 300 words
        'category': 'Criminal Law',  # Use exact category from the form
        'cover_image': (test_image, 'test_cover.jpg'),
        'submit': 'Submit'
    }
    
    if csrf_token:
        form_data['csrf_token'] = csrf_token
    
    print("\n[2] Submitting form data:")
    print(f"    - Author: {form_data['author']}")
    print(f"    - Title: {form_data['title']}")
    print(f"    - Email: {form_data['email']}")
    print(f"    - Category: {form_data['category']}")
    print(f"    - Cover image: test_cover.jpg")
    print(f"    - CSRF token: included: {bool(csrf_token)}")
    
    # Submit the form
    response = client.post('/submit', data=form_data, follow_redirects=True, content_type='multipart/form-data')
    
    print(f"\n    Response status: {response.status_code}")
    
    # Check database for new article
    from models import Article
    with app.app_context():
        articles = Article.query.filter_by(title='Test Article with Cover Image 2').all()
        print(f"\n[3] Database check:")
        print(f"    Articles found: {len(articles)}")
        
        for article in articles:
            print(f"\n    Article ID: {article.id}")
            print(f"    Title: {article.title}")
            print(f"    Cover image filename: {article.cover_image}")
            print(f"    Status: {article.status}")
            
            if article.cover_image:
                upload_folder = app.config.get('UPLOAD_FOLDER')
                file_path = os.path.join(upload_folder, article.cover_image)
                print(f"    File path: {file_path}")
                print(f"    File exists on disk: {os.path.exists(file_path)}")
            else:
                print(f"    ❌ No cover image in database!")
