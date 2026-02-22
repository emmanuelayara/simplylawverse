# Simply Lawverse - Production Deployment Guide

A production-ready corporate law firm website for Nigerian lawyers offering corporate legal services, online consultations, and legal articles with Paystack payment integration.

## 🎯 Quick Start (Development)

### 1. Prerequisites
- Python 3.9+
- PostgreSQL database
- Paystack account (free)

### 2. Installation

```bash
# Clone repository
cd simplylawverse

# Create virtual environment  
python -m venv myenv
source myenv/Scripts/activate  # On Windows: myenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

### 3. Configure Environment Variables

Edit `.env`:

```
FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/lawfirm
PAYSTACK_PUBLIC_KEY=your-paystack-public-key
PAYSTACK_SECRET_KEY=your-paystack-secret-key
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@simplylawverse.com
```

### 4. Database Setup

```bash
# Create database
createdb lawfirm

# Run migrations
flask db upgrade

# Seed initial data (services, consultation types, availability)
python seed_database.py
```

### 5. Run Development Server

```bash
flask run
# Access at http://localhost:5000
```

## 🚀 Production Deployment (Render)

### 1. Prepare for Production

```bash
# Create Procfile (already included)
# Ensure all environment variables are set in Render
# Update requirements.txt if needed
pip freeze > requirements.txt
```

### 2. Deploy to Render

1. Go to [render.com](https://render.com)
2. Sign up and create new PostgreSQL database
3. Create new Web Service
4. Connect your GitHub repository
5. Set Environment Variables:
   - `FLASK_ENV=production`
   - `SECRET_KEY=` (generate new one)
   - All Paystack keys
   - Database URL (from Render PostgreSQL)
   - Mail credentials

### 3. Post-Deployment Setup

After deploying to Render:

```bash
# Run database migrations (in Render environment)
flask db upgrade

# Seed data
python seed_database.py
```

Or use Render's dashboard to run one-off commands.

## 💳 Paystack Integration Setup

### 1. Create Paystack Account
- Go to [https://paystack.com](https://paystack.com)
- Sign up and verify your account
- Get your Public and Secret keys from Dashboard

### 2. Configure in Flask
Environment variables are automatically loaded. Payment flow:
- User books consultation
- Form data → Database
- Initialize Paystack payment
- User redirected to Paystack
- Payment verified on callback
- Confirmation email sent
- Booking confirmed

### 3. Test Paystack
Use test cards from Paystack documentation:
- Card: 4111 1111 1111 1111
- CVV: any 3 digits
- Expiry: any future date

## 📧 Email Configuration

### Gmail Setup
1. Enable 2-Factor Authentication
2. Generate App Password
3. Use App Password in `.env` as `MAIL_PASSWORD`
4. Set `MAIL_USERNAME` to your Gmail address

### Custom Email
Use any SMTP provider by updating:
```
MAIL_SERVER=smtp.provider.com
MAIL_PORT=587
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-password
```

## 🎨 Customization

### Logo
To customize the logo:
1. Edit [Logo SVG component](./components/logo.py)
2. Update `/public/logo.svg` for static version
3. Logo displays in header and documents

### Services
Edit/add services:
1. Go to admin panel (if admin section set up)
2. Or edit `seed_database.py` and re-seed

### Styling
- Tailwind CSS via CDN (no build step needed)
- Colors configured in `base.html`
- Dark mode: intentionally not included (professional look)
- Modify color vars in `tailwind.config`:
  - `law-dark`: #1a1a1a
  - `law-blue`: #003d7a
  - `law-gold`: #b8860b

## 🔒 Security Checklist

For Production:

- [ ] Set `FLASK_ENV=production`
- [ ] Generate strong `SECRET_KEY`
- [ ] Use HTTPS only (Render provides automatic HTTPS)
- [ ] Enable database backups
- [ ] Set `SESSION_COOKIE_SECURE=true`
- [ ] Review all environment variables
- [ ] Update `Referrer-Policy` headers
- [ ] Enable CORS if needed, restrict origins
- [ ] Implement rate limiting on booking forms
- [ ] Regular security updates for dependencies

## 📊 Database Management

### Backup
```bash
# PostgreSQL backup
pg_dump lawfirm > backup.sql

# Restore
psql lawfirm < backup.sql
```

### Migrations
```bash
# Create new migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade

# Rollback
flask db downgrade
```

## 📱 Mobile & SEO

### Mobile Responsive
- All templates are mobile-first responsive
- Tested on common screen sizes
- Touch-friendly buttons and forms

### SEO Features
- Meta tags on all pages
- Semantic HTML structure
- Server-side rendering by default
- XML sitemap (can be added)
- Mobile-friendly design

## 🛠 Troubleshooting

### Database Connection Error
```bash
# Check connection string
echo $DATABASE_URL

# Verify PostgreSQL is running
psql --version
```

### Email Not Sending
- Check SMTP credentials
- Verify firewall allows SMTP
- Check email logs in Flask app
- Test with Gmail app-specific password

### Paystack Payment Fails
- Verify keys are correct
- Check Paystack account balance
- Review payment logs
- Test with test cards

### Static Files Not Loading
```bash
# In production, ensure:
# 1. Collect static files (if using whitespace)
# 2. Configure CDN or serve directly
# 3. Check STATIC_FOLDER in config
```

## 📈 Monitoring

### Key Metrics to Track
- Booking conversion rate
- Payment success rate
- Average response time
- Error rates
- Email delivery success

### Logging
Check Flask logs:
```bash
# Development
flask run --debug

# Production (Render shows logs in dashboard)
# Or:
tail -f /var/log/app.log
```

## 🔄 Maintenance

### Regular Tasks
- Monitor booking queue
- Review client feedback
- Update blog/articles
- Check payment reconciliation
- Update security dependencies

### Monthly
- Review server logs
- Check backup status
- Update content as needed
- Monitor performance metrics

## 📞 Support

For issues:
1. Check logs first
2. Review Paystack/email configurations
3. Test in development environment
4. Check database integrity

## 🚀 Next Steps

### Future Enhancements
- [ ] Client portal for viewing bookings
- [ ] Retainer subscription management
- [ ] Legal templates library
- [ ] Compliance reminder system
- [ ] WhatsApp integration for bookings
- [ ] Invoice/receipt generation
- [ ] Document e-signature integration

---

**Made with ❤️ for Nigerian Law Firms**

Last Updated: February 2026