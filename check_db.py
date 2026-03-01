#!/usr/bin/env python
"""Check article cover images in database using sqlite3"""
import sqlite3

db_path = 'instance/site.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all articles
cursor.execute("SELECT id, title, cover_image, status FROM article LIMIT 10")
rows = cursor.fetchall()

print(f"\n✓ Found {len(rows)} articles\n")
for row in rows:
    article_id, title, cover_image, status = row
    print(f"ID: {article_id}")
    print(f"  Title: {title[:50]}")
    print(f"  Cover Image: {cover_image}")
    print(f"  Status: {status}")
    print()

# Count stats
cursor.execute("SELECT COUNT(*) FROM article WHERE cover_image IS NOT NULL")
with_cover = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM article WHERE cover_image IS NULL")
without_cover = cursor.fetchone()[0]

print(f"\n✓ Articles WITH cover_image: {with_cover}")
print(f"✗ Articles WITHOUT cover_image: {without_cover}")

conn.close()
