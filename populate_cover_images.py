#!/usr/bin/env python
"""Populate existing test articles with cover images"""
import sqlite3
import os

db_path = 'instance/site.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get the uploaded cover image filename
upload_folder = 'static/uploads'
uploaded_files = os.listdir(upload_folder)
image_file = [f for f in uploaded_files if f.startswith('1772') and f.endswith('.jpg')]

if image_file:
    cover_image = image_file[0]
    print(f"\n📝 Using cover image: {cover_image}")
    
    # Update existing articles to use this cover image
    article_ids_to_update = [1, 2, 3, 4, 5, 6]  # The test articles
    
    for article_id in article_ids_to_update:
        cursor.execute("UPDATE article SET cover_image = ? WHERE id = ?", (cover_image, article_id))
        print(f"   ✅ Article {article_id} updated with cover image")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Database updated successfully!")
    
    # Verify
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM article WHERE cover_image IS NOT NULL")
    with_cover = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM article WHERE cover_image IS NULL")
    without_cover = cursor.fetchone()[0]
    conn.close()
    
    print(f"\n📊 Article status:")
    print(f"   Articles WITH cover images: {with_cover}")
    print(f"   Articles WITHOUT cover images: {without_cover}")
else:
    print("❌ No cover image found!")
