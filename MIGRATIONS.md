# Flask-Migrate Setup Guide

## Overview
This project uses **Flask-Migrate** for database schema management. This replaces the old `db.create_all()` approach with proper database migrations for production readiness.

## Key Changes Made

1. **extensions.py**: Added `Migrate` initialization
2. **app.py**: 
   - Imported `migrate` from extensions
   - Initialized with `migrate.init_app(app, db)`
   - Removed `db.create_all()` call - migrations handle schema creation now
3. **Migrations folder**: Created with Alembic configuration

## Common Commands

### First Time Setup (already done)
```bash
# Initialize migrations folder
flask db init

# Create initial migration snapshot
flask db migrate -m "Initial migration: create tables"

# Apply migrations to database
flask db upgrade
```

### During Development

#### After modifying models:
```bash
# Create a new migration file
flask db migrate -m "Add new field to Article"

# Review the generated migration file in migrations/versions/
# Edit if needed for custom logic

# Apply the migration
flask db upgrade
```

#### To downgrade (undo) the last migration:
```bash
flask db downgrade
```

#### To see migration history:
```bash
flask db history
```

#### To check current database version:
```bash
flask db current
```

## Migration File Structure

Migration files are stored in `migrations/versions/` with naming like:
```
abc123def456_add_new_field_to_article.py
```

Each migration file contains:
- `upgrade()`: Changes to apply
- `downgrade()`: Changes to revert

## Best Practices

1. **Always review generated migrations** - Alembic isn't perfect
2. **Test migrations** before deploying:
   ```bash
   flask db upgrade  # Apply
   flask db downgrade  # Revert
   flask db upgrade  # Apply again
   ```
3. **Write descriptive migration messages**:
   ```bash
   flask db migrate -m "Add is_published flag to Article and set default to False"
   ```
4. **Never manually edit alembic_version table** - Let Flask-Migrate handle it
5. **Keep migrations in git** - They're part of your codebase

## Deployment

### First deployment (with existing data):
```bash
flask db upgrade  # Apply all migrations
```

### Subsequent deployments:
```bash
flask db upgrade  # Apply any new migrations
```

## Troubleshooting

### Error: "Can't locate revision"
- The database has a reference to a migration that doesn't exist
- Solution: Clear alembic_version table and recreate migrations

### Migration doesn't detect your changes
- Alembic autogenerate may miss some changes
- Solution: Review and manually edit the migration file

### Need to see the SQL being generated:
```bash
flask db upgrade --sql  # Shows SQL without applying
```

## References
- [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
