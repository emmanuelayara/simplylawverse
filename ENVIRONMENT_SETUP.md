# Environment Setup Guide - Simply Lawverse

## Quick Start

### 1. Copy the Environment Template
```bash
cp .env.example .env
```

### 2. Edit .env with Your Settings
```bash
# Edit the .env file with your actual configuration
nano .env
# or use your preferred editor
```

## Environment Configurations

### Development Environment

**Best for:** Local development, testing features

**.env settings:**
```
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///site.db
SESSION_COOKIE_SECURE=false
PREFERRED_URL_SCHEME=http
```

**Benefits:**
- Uses SQLite (no database setup needed)
- Debug mode enabled
- Hot reload on file changes
- Detailed error messages

**Start development server:**
```bash
python -m flask run --debug
# or
export FLASK_ENV=development
python app.py
```

---

### Production Environment

**Best for:** Live deployment

**Requirements:**
1. Generate a strong SECRET_KEY
2. Use PostgreSQL or MySQL (not SQLite)
3. Set up HTTPS/SSL
4. Configure email service
5. Set environment variables

**.env settings:**
```
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=<your-strong-random-key>
DATABASE_URL=postgresql://user:password@localhost:5432/simplylawverse
SESSION_COOKIE_SECURE=true
PREFERRED_URL_SCHEME=https
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

**Step-by-step Production Setup:**

#### 1. Generate Secure SECRET_KEY
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output and set it in .env as SECRET_KEY

#### 2. Set Up PostgreSQL Database

**Install PostgreSQL:**
```bash
# On Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# On macOS
brew install postgresql

# On Windows
# Download from https://www.postgresql.org/download/windows/
```

**Create database and user:**
```bash
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE simplylawverse_db;
CREATE USER simplylawverse WITH PASSWORD 'strong-password';
ALTER ROLE simplylawverse SET client_encoding TO 'utf8';
ALTER ROLE simplylawverse SET default_transaction_isolation TO 'read committed';
ALTER ROLE simplylawverse SET default_transaction_deferrable TO on;
ALTER ROLE simplylawverse SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE simplylawverse_db TO simplylawverse;
\q
```

**Set DATABASE_URL in .env:**
```
DATABASE_URL=postgresql://simplylawverse:strong-password@localhost:5432/simplylawverse_db
```

**Install Python driver:**
```bash
pip install psycopg2-binary
```

#### 3. Alternative: MySQL Database

**Install MySQL:**
```bash
# On Ubuntu/Debian
sudo apt-get install mysql-server

# On macOS
brew install mysql

# On Windows
# Download from https://dev.mysql.com/downloads/mysql/
```

**Create database and user:**
```bash
mysql -u root -p

# In MySQL shell:
CREATE DATABASE simplylawverse_db;
CREATE USER 'simplylawverse'@'localhost' IDENTIFIED BY 'strong-password';
GRANT ALL PRIVILEGES ON simplylawverse_db.* TO 'simplylawverse'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**Set DATABASE_URL in .env:**
```
DATABASE_URL=mysql+pymysql://simplylawverse:strong-password@localhost:3306/simplylawverse_db
```

**Install Python driver:**
```bash
pip install pymysql
```

#### 4. Set Up Email Service

**Option A: Gmail (recommended for small deployments)**
1. Enable 2-Factor Authentication on Gmail
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Set in .env:
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

**Option B: SendGrid**
1. Create account at https://sendgrid.com
2. Get API key from Settings → API Keys
3. Set in .env:
```
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
```

**Option C: AWS SES**
1. Set up AWS account and SES
2. Get SMTP credentials from AWS Console
3. Set in .env:
```
MAIL_SERVER=email-smtp.region.amazonaws.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-ses-username
MAIL_PASSWORD=your-ses-password
```

#### 5. Configure HTTPS/SSL

Use a reverse proxy like Nginx with Let's Encrypt:

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

#### 6. Deploy with Gunicorn

```bash
pip install gunicorn

# Start application
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

---

## Testing Environment

**Best for:** Running automated tests

**.env settings (automatic):**
```
FLASK_ENV=testing
SQLALCHEMY_DATABASE_URI=sqlite:///:memory:
WTF_CSRF_ENABLED=False
```

**Run tests:**
```bash
pytest
# or
python -m unittest discover
```

---

## Database Migrations

After changing models, create migrations:

```bash
# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade

# Downgrade (revert last migration)
flask db downgrade
```

---

## Security Checklist for Production

- [ ] Set strong `SECRET_KEY` (use `secrets` module)
- [ ] Use PostgreSQL or MySQL (not SQLite)
- [ ] Enable HTTPS/SSL certificates
- [ ] Set `SESSION_COOKIE_SECURE=true`
- [ ] Set `FLASK_DEBUG=0`
- [ ] Configure email service (SMTP)
- [ ] Set up proper logging and monitoring
- [ ] Create regular database backups
- [ ] Configure firewall rules
- [ ] Use environment variables for all secrets
- [ ] Set up monitoring/alerting
- [ ] Configure rate limiting
- [ ] Enable CSRF protection
- [ ] Regular security updates

---

## Troubleshooting

### "SQLite is not suitable for production"
**Solution:** Use PostgreSQL or MySQL. Set `DATABASE_URL` in .env:
```
DATABASE_URL=postgresql://user:pass@localhost:5432/db
```

### "SECRET_KEY must be set in production"
**Solution:** Generate and set SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Database connection errors
**Solution:** Check DATABASE_URL format:
- PostgreSQL: `postgresql://user:pass@host:5432/dbname`
- MySQL: `mysql+pymysql://user:pass@host:3306/dbname`
- SQLite: `sqlite:///site.db` (development only)

### Email not sending
**Solution:** Verify SMTP settings:
- Test connection: `telnet smtp.gmail.com 587`
- Check app-specific password for Gmail
- Verify firewall allows outbound SMTP

---

## Environment Variables Reference

| Variable | Dev Value | Prod Value | Required |
|----------|-----------|-----------|----------|
| FLASK_ENV | development | production | Yes |
| SECRET_KEY | dev-key | random-strong-key | Yes |
| DATABASE_URL | sqlite:///site.db | postgresql://... | Yes |
| MAIL_USERNAME | email@gmail.com | production-email | If using email |
| MAIL_PASSWORD | app-password | production-password | If using email |
| SESSION_COOKIE_SECURE | false | true | Yes |
| PREFERRED_URL_SCHEME | http | https | Yes |

---

## Additional Resources

- Flask Configuration: https://flask.palletsprojects.com/config/
- PostgreSQL Setup: https://www.postgresql.org/download/
- SSL/HTTPS: https://letsencrypt.org/
- Gunicorn: https://gunicorn.org/
- Nginx: https://nginx.org/

