#!/usr/bin/env python
"""Test if files are being received in request"""
import sys
sys.path.insert(0, '.')

from app import create_app
from flask import request
import os

app = create_app()

# Print config info
print("\n=== FLASK CONFIGURATION ===")
print(f"UPLOAD_FOLDER: {app.config.get('UPLOAD_FOLDER')}")
print(f"ALLOWED_EXTENSIONS: {app.config.get('ALLOWED_EXTENSIONS')}")
print(f"MAX_CONTENT_LENGTH: {app.config.get('MAX_CONTENT_LENGTH')}")
print(f"Static folder: {app.static_folder}")
print(f"Static url path: {app.static_url_path}")

# Check if uploads directory exists and is writable
upload_folder = app.config.get('UPLOAD_FOLDER')
print(f"\n=== UPLOAD FOLDER CHECK ===")
print(f"Folder exists: {os.path.exists(upload_folder)}")
print(f"Is directory: {os.path.isdir(upload_folder)}")
print(f"Is writable: {os.access(upload_folder, os.W_OK)}")

# List files in uploads directory
if os.path.exists(upload_folder):
    files = os.listdir(upload_folder)
    print(f"Files in uploads directory ({len(files)} total):")
    for f in files[:5]:
        print(f"  - {f}")
    if len(files) > 5:
        print(f"  ... and {len(files) - 5} more")
