#!/usr/bin/env python
import os
from app import create_app

app = create_app()
uf = app.config.get('UPLOAD_FOLDER')
print(f"UPLOAD_FOLDER: {uf}")
print(f"Exists: {os.path.exists(uf)}")
print(f"Writable: {os.access(uf, os.W_OK) if os.path.exists(uf) else 'N/A'}")
files = os.listdir(uf) if os.path.exists(uf) else []
print(f"Files in directory: {len(files)}")
for f in files[:3]:
    print(f"  - {f}")
