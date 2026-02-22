"""
Database Migration Guide - Schema Improvements

This script provides step-by-step instructions for migrating to the new database schema.
It includes SQL for manual migration if Flask-Migrate doesn't work perfectly.

Run after models.py has been updated.
"""

# ============================================================================
# STEP 1: BACKUP YOUR DATABASE
# ============================================================================

"""
Before making any changes, backup your database:

PostgreSQL:
  pg_dump your_database > backup_$(date +%Y%m%d_%H%M%S).sql

SQLite (Flask default):
  cp instance/app.db instance/app.db.backup

MySQL:
  mysqldump -u username -p database_name > backup.sql
"""

# ============================================================================
# STEP 2: CREATE FLASK MIGRATION
# ============================================================================

"""
Using Flask-Migrate (recommended approach):

1. Open terminal in project directory
2. Run:
   
   flask db migrate -m "Improve database design: consolidate status, add indices, enhance visitor tracking"
   
3. This creates a new file in migrations/versions/
4. Review the generated migration file
5. Apply it:
   
   flask db upgrade

Done! Skip to STEP 4 (Verify Migration)
"""

# ============================================================================
# STEP 3: MANUAL MIGRATION (If Flask-Migrate doesn't work)
# ============================================================================

"""
For PostgreSQL - Run these SQL commands in order:

```sql
-- 1. Create indices on Article table
CREATE INDEX idx_article_status ON article(status);
CREATE INDEX idx_article_category ON article(category);
CREATE INDEX idx_article_date_posted ON article(date_posted);
CREATE INDEX idx_article_status_category ON article(status, category);

-- 2. Update Comment table
-- Make email NOT NULL (first set existing NULLs to default)
UPDATE comment SET email = 'anonymous' WHERE email IS NULL;
ALTER TABLE comment ALTER COLUMN email SET NOT NULL;
ALTER TABLE comment ALTER COLUMN email SET DEFAULT 'anonymous';

-- Create indices on Comment table
CREATE INDEX idx_comment_article_id ON comment(article_id);
CREATE INDEX idx_comment_parent_id ON comment(parent_id);
CREATE INDEX idx_comment_article_date ON comment(article_id, date_posted);

-- 3. Expand Article title field (if needed)
ALTER TABLE article ALTER COLUMN title TYPE VARCHAR(200);

-- 4. Add new columns to Visit table
ALTER TABLE visit ADD COLUMN user_id INTEGER REFERENCES "user"(id);
ALTER TABLE visit ADD COLUMN session_id VARCHAR(255);
ALTER TABLE visit ADD COLUMN ip_address VARCHAR(45);
ALTER TABLE visit ADD COLUMN visitor_hash VARCHAR(64);
ALTER TABLE visit ADD COLUMN user_agent VARCHAR(500);
ALTER TABLE visit ADD COLUMN referer VARCHAR(500);
ALTER TABLE visit ADD COLUMN duration_seconds INTEGER DEFAULT 0;

-- 5. Make article_id NOT NULL in Visit
UPDATE visit SET article_id = 1 WHERE article_id IS NULL;
ALTER TABLE visit ALTER COLUMN article_id SET NOT NULL;

-- 6. Create indices on Visit table
CREATE INDEX idx_visit_article_id ON visit(article_id);
CREATE INDEX idx_visit_user_id ON visit(user_id);
CREATE INDEX idx_visit_session_id ON visit(session_id);
CREATE INDEX idx_visit_visitor_hash ON visit(visitor_hash);
CREATE INDEX idx_visit_timestamp ON visit(timestamp);
CREATE INDEX idx_visit_article_date ON visit(article_id, timestamp);
CREATE INDEX idx_visit_user_date ON visit(user_id, timestamp);
CREATE INDEX idx_visit_session_date ON visit(session_id, timestamp);
CREATE INDEX idx_visit_hash_date ON visit(visitor_hash, timestamp);

-- 7. Drop old 'approved' column from Article (if exists)
ALTER TABLE article DROP COLUMN IF EXISTS approved;
```

For SQLite - Run these SQL commands:

```sql
-- SQLite doesn't support ALTER COLUMN directly, use this approach:
-- 1. Create new comment table without nullable email
BEGIN TRANSACTION;

-- Create temporary table with new schema
CREATE TABLE comment_new (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL DEFAULT 'anonymous',
    content TEXT NOT NULL,
    date_posted DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    article_id INTEGER NOT NULL,
    parent_id INTEGER,
    FOREIGN KEY(article_id) REFERENCES article(id),
    FOREIGN KEY(parent_id) REFERENCES comment(id)
);

-- Copy data, replacing NULL emails
INSERT INTO comment_new
SELECT id, name, COALESCE(email, 'anonymous'), content, date_posted, article_id, parent_id
FROM comment;

-- Drop old table and rename
DROP TABLE comment;
ALTER TABLE comment_new RENAME TO comment;

-- Create indices
CREATE INDEX idx_comment_article_id ON comment(article_id);
CREATE INDEX idx_comment_parent_id ON comment(parent_id);
CREATE INDEX idx_comment_article_date ON comment(article_id, date_posted);

-- 2. Create new visit table with all fields
CREATE TABLE visit_new (
    id INTEGER PRIMARY KEY,
    article_id INTEGER NOT NULL,
    user_id INTEGER,
    session_id VARCHAR(255),
    ip_address VARCHAR(45),
    visitor_hash VARCHAR(64),
    user_agent VARCHAR(500),
    referer VARCHAR(500),
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    duration_seconds INTEGER DEFAULT 0,
    FOREIGN KEY(article_id) REFERENCES article(id),
    FOREIGN KEY(user_id) REFERENCES "user"(id)
);

-- Copy existing visit data
INSERT INTO visit_new (id, article_id, timestamp)
SELECT id, article_id, timestamp FROM visit;

-- Drop old table and rename
DROP TABLE visit;
ALTER TABLE visit_new RENAME TO visit;

-- Create indices
CREATE INDEX idx_visit_article_id ON visit(article_id);
CREATE INDEX idx_visit_user_id ON visit(user_id);
CREATE INDEX idx_visit_session_id ON visit(session_id);
CREATE INDEX idx_visit_visitor_hash ON visit(visitor_hash);
CREATE INDEX idx_visit_timestamp ON visit(timestamp);
CREATE INDEX idx_visit_article_date ON visit(article_id, timestamp);
CREATE INDEX idx_visit_user_date ON visit(user_id, timestamp);
CREATE INDEX idx_visit_session_date ON visit(session_id, timestamp);
CREATE INDEX idx_visit_hash_date ON visit(visitor_hash, timestamp);

-- 3. Add indices to article table
CREATE INDEX idx_article_status ON article(status);
CREATE INDEX idx_article_category ON article(category);
CREATE INDEX idx_article_date_posted ON article(date_posted);
CREATE INDEX idx_article_status_category ON article(status, category);

COMMIT;
```
"""

# ============================================================================
# STEP 4: VERIFY MIGRATION
# ============================================================================

"""
Test that the migration worked by running this in Python shell:

    python
    >>> from app import app, db
    >>> from models import Article, Comment, Visit
    >>> 
    >>> with app.app_context():
    ...     # Test Article indices
    ...     approved = Article.query.filter_by(status='approved').first()
    ...     print(f"✅ Article query works: {approved}")
    ...     
    ...     # Test Comment indices
    ...     comments = Comment.query.filter_by(article_id=1).all()
    ...     print(f"✅ Comment query works: {len(comments)} comments")
    ...     
    ...     # Check no null emails
    ...     null_emails = Comment.query.filter_by(email=None).count()
    ...     print(f"✅ No null emails: {null_emails == 0}")
    ...     
    ...     # Test Visit indices
    ...     visits = Visit.query.filter_by(article_id=1).all()
    ...     print(f"✅ Visit query works: {len(visits)} visits")
    ...     
    ...     print("\\n✅ ALL TESTS PASSED")

Expected output:
  ✅ Article query works: <Article 1: Title>
  ✅ Comment query works: 5 comments
  ✅ No null emails: True
  ✅ Visit query works: 42 visits
  ✅ ALL TESTS PASSED
"""

# ============================================================================
# STEP 5: UPDATE APPLICATION CODE
# ============================================================================

"""
Update routes.py to use the new Visit tracking:

OLD CODE (routes.py - comment route):
    new_comment = Comment(
        name=form.name.data,
        email=form.email.data,
        content=form.content.data,
        article_id=article_id
    )

NEW CODE:
    new_comment = Comment(
        name=form.name.data,
        email=form.email.data or 'anonymous',  # Ensure never null
        content=form.content.data,
        article_id=article_id
    )

---

OLD CODE (routes.py - visit tracking):
    visit = Visit(article_id=article_id, timestamp=datetime.utcnow())
    db.session.add(visit)

NEW CODE:
    from flask import request, session
    
    visitor_hash = Visit.generate_visitor_hash(
        request.remote_addr,
        request.user_agent.string
    )
    
    visit = Visit(
        article_id=article_id,
        user_id=current_user.id if current_user.is_authenticated else None,
        session_id=session.get('session_id'),
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        referer=request.referrer,
        visitor_hash=visitor_hash,
        timestamp=datetime.utcnow(),
        duration_seconds=0
    )
    db.session.add(visit)
"""

# ============================================================================
# STEP 6: TEST IN DEVELOPMENT
# ============================================================================

"""
Before deploying to production:

1. Run the application locally:
   flask run

2. Test each feature:
   - Create a new comment
   - Check it has email (not null)
   - View an article
   - Check visit was recorded

3. Run tests:
   pytest test_validation.py -v (existing tests)

4. Check database:
   - Verify indices exist
   - Verify no null comments.email
   - Verify visits are being recorded

5. If all works, proceed to production deployment
"""

# ============================================================================
# STEP 7: PRODUCTION DEPLOYMENT
# ============================================================================

"""
For production:

1. Backup production database
2. Apply migration in staging first
3. Test thoroughly
4. Deploy to production during low-traffic window
5. Monitor for errors
6. Keep backup for 30 days minimum

Rollback procedure (if needed):
  flask db downgrade  # Reverts to previous version
"""

# ============================================================================
# STEP 8: ANALYTICS QUERIES
# ============================================================================

"""
Now you can run these analytics queries:

Total visits to an article:
  visits = Visit.query.filter_by(article_id=5).count()

Unique authenticated visitors:
  unique_users = db.session.query(Visit.user_id).filter(
      Visit.article_id == 5,
      Visit.user_id.isnot(None)
  ).distinct().count()

Unique anonymous visitors (by session):
  unique_sessions = db.session.query(Visit.session_id).filter(
      Visit.article_id == 5,
      Visit.session_id.isnot(None)
  ).distinct().count()

Unique visitors (by fingerprint):
  unique_visitors = db.session.query(Visit.visitor_hash).filter(
      Visit.article_id == 5,
      Visit.visitor_hash.isnot(None)
  ).distinct().count()

Top referring sources:
  db.session.query(Visit.referer, func.count()).filter(
      Visit.article_id == 5
  ).group_by(Visit.referer).order_by(func.count().desc()).all()

Recent activity (last 7 days):
  from datetime import timedelta
  recent = Visit.query.filter(
      Visit.article_id == 5,
      Visit.timestamp > datetime.utcnow() - timedelta(days=7)
  ).all()
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
Common issues and solutions:

Issue: "No such table: comment_new"
Solution: You may have other constraints. Try:
  - Drop foreign key constraints first
  - Recreate them after copying data
  - Check SQLite syntax for your version

Issue: "Column 'approved' already dropped"
Solution: The 'approved' field may have already been removed
  - This is fine, it was the goal
  - Verify Article table only has 'status' field

Issue: "Indices not found after migration"
Solution: Check if indices were actually created
  PostgreSQL: SELECT * FROM pg_indexes WHERE tablename='article';
  SQLite: PRAGMA index_list(article);
  MySQL: SHOW INDEX FROM article;

Issue: Comments have null email after migration
Solution: Run this fix:
  Comment.query.filter_by(email=None).update({'email': 'anonymous'})
  db.session.commit()

Issue: Visit tracking not recording
Solution: Make sure you updated routes.py with new Visit() parameters
  - Check that all required fields are provided
  - Verify article_id is not null
"""

# ============================================================================
# CHECKLIST
# ============================================================================

"""
Migration Checklist:

[ ] Step 1: Backup database
[ ] Step 2: Create migration (flask db migrate)
[ ] Step 3: Review migration file
[ ] Step 4: Apply migration (flask db upgrade)
[ ] Step 5: Verify indices exist
[ ] Step 6: Verify no null emails in comments
[ ] Step 7: Update routes.py code
[ ] Step 8: Test in development
[ ] Step 9: Run existing tests
[ ] Step 10: Test analytics queries
[ ] Step 11: Deploy to production
[ ] Step 12: Monitor for errors
[ ] Step 13: Keep backup for 30 days

COMPLETED WHEN ALL ITEMS CHECKED ✅
"""

if __name__ == '__main__':
    print("Database Migration Guide")
    print("Follow the steps above to migrate your database schema")
    print("See documentation for detailed instructions")
