#!/usr/bin/env python
import os
from app import create_app

app = create_app()

print(f"App static_folder: {app.static_folder}")
print(f"App static_url_path: {app.static_url_path}")
print(f"UPLOAD_FOLDER config: {app.config.get('UPLOAD_FOLDER')}")

# Test url_for in test request context
with app.test_request_context():
    from flask import url_for
    
    # Simulate what template does
    test_image = "test_image.jpg"
    url = url_for('static', filename='uploads/' + test_image)
    print(f"\ntest url_for('static', filename='uploads/{test_image}'):")
    print(f"  {url}")
    
    # Check if that file would be served from correct location  
    upload_folder = app.config.get('UPLOAD_FOLDER')
    test_file_path = os.path.join(upload_folder, test_image)
    print(f"\nWould look for file at: {test_file_path}")
    print(f"File exists: {os.path.exists(test_file_path)}")
