# Simply Lawverse - Project Setup Guide

## 🎯 Project Overview

**Simply Lawverse** is a production-ready corporate law firm website built with:
- **Frontend**: HTML/CSS (Tailwind CSS)
- **Backend**: Flask + SQLAlchemy
- **Database**: PostgreSQL
- **Payments**: Paystack (Nigeria)
- **Deployment**: Render
- **CMS**: Blog/articles management with Flask

### Key Features
✅ Professional corporate law services showcase  
✅ Online consultation booking with Paystack payments  
✅ Client intake forms with document uploads  
✅ Service management (6 corporate law services)  
✅ Blog/legal articles section  
✅ Admin dashboard for managing services and bookings  
✅ Email confirmations and notifications  
✅ Availability scheduling  
✅ Mobile-responsive design  
✅ SEO-friendly structure  

## 📁 Project Structure

```
simplylawverse/
├── app.py                          # Flask app factory
├── config.py                       # Configuration management
├── models.py                       # Database models
├── forms.py                        # WTForms for validation
├── requirements.txt                # Python dependencies
├── extensions.py                   # Flask extensions
├── logger.py                       # Logging setup
├── paystack_client.py             # Paystack payment integration
├── seed_database.py               # Database seeding script
│
├── components/
│   └── logo.py                    # SVG logo component
│
├── blueprints/
│   ├── public.py                  # Public pages
│   ├── services.py                # Services listing and detail
│   ├── bookings.py                # Booking/consultation flow
│   ├── auth.py                    # Authentication
│   ├── articles.py                # Blog articles
│   ├── admin.py                   # Admin dashboard
│   ├── comments.py                # Article comments
│   └── contact.py                 # Contact forms
│
├── templates/
│   ├── base.html                  # Base template with Tailwind
│   ├── components/
│   │   ├── header.html            # Navigation and logo
│   │   └── footer.html            # Footer
│   ├── pages/
│   │   ├── home.html              # Homepage
│   │   ├── about.html             # About lawyer/firm
│   │   └── blog.html              # Blog listing
│   ├── services/
│   │   ├── index.html             # Services listing
│   │   └── detail.html            # Individual service page
│   ├── bookings/
│   │   ├── index.html             # Booking intake form
│   │   ├── select_consultation.html
│   │   ├── confirm.html           # Booking confirmation
│   │   └── success.html           # Payment success page
│   ├── legal/
│   │   ├── privacy-policy.html
│   │   ├── terms.html
│   │   └── disclaimer.html
│   └── emails/
│       └── booking_confirmation.html
│
├── static/
│   ├── uploads/                   # Client document uploads
│   └── logo.svg                   # SVG logo file
│
├── migrations/                    # Alembic migrations
└── docs/
    ├── DEPLOYMENT_GUIDE.md        # Production deployment
    └── PROJECT_SETUP.md           # This file
```

## 🗄️ Database Models

### Core Models

**Service**
- Represents offered legal services
- Fields: name, slug, description, pricing, SEO metadata
- 6 default services included (company registration, contract drafting, compliance, etc.)

**ConsultationType**
- Represents consultation packages (30-min, 60-min, retainer)
- Fields: duration, price in NGN, features/includes
- 4 default types included

**Booking**
- Represents a consultation appointment
- Links to Service and ConsultationType
- Payment tracking (Paystack reference, status)
- Client intake information
- Status workflow: pending → confirmed → completed

**ClientIntake**
- Initial information gathering form
- Company details, legal issue description
- Document upload support
- Status: pending → reviewed → scheduled

**AdminAvailability**
- Lawyer availability scheduling
- Date/time slots with duration
- Auto-generates available times for booking

**Article**
- Blog articles and legal resources
- Status: pending → approved → published
- Categories, soft delete support
- Comments and visit tracking

## 🚀 Getting Started

### 1. Environment Setup

```bash
# Clone and enter directory
cd simplylawverse
python -m venv myenv
source myenv/Scripts/activate  # Windows: myenv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create `.env` file:

```
FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=postgresql://user:password@localhost:5432/lawfirm_dev

# Paystack (get from https://paystack.com)
PAYSTACK_PUBLIC_KEY=pk_test_xxxxx
PAYSTACK_SECRET_KEY=sk_test_xxxxx

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@simplylawverse.com

# Upload settings
MAX_CONTENT_LENGTH=5242880
UPLOAD_FOLDER=static/uploads
```

### 4. Database Setup

```bash
# Create PostgreSQL database
createdb lawfirm_dev

# Run migrations
flask db upgrade

# Seed with initial data
python seed_database.py
```

### 5. Run Development Server

```bash
flask run
# Visit http://localhost:5000
```

## 🔑 Key Endpoints

### Public Routes
- `/` - Homepage with services overview
- `/services` - Services listing
- `/services/<slug>` - Individual service detail
- `/blog` - Blog articles
- `/about` - About lawyer and firm
- `/book` - Consultation booking
- `/legal/privacy-policy` - Privacy policy
- `/legal/terms` - Terms of service
- `/legal/disclaimer` - Legal disclaimer

### Admin Routes (Protected)
- `/admin/` - Dashboard
- `/admin/services` - Manage services
- `/admin/consultations` - Manage consultation types
- `/admin/availability` - Set availability
- `/admin/bookings` - View bookings
- `/admin/articles` - Manage blog articles

## 💳 Paystack Integration

### How It Works

1. **User submits booking form**
   - ClientIntake created
   - Redirects to consultation selection

2. **User selects consultation type and date**
   - Shows available time slots
   - Selects preferred time

3. **Booking confirmation & payment**
   - Booking record created
   - Paystack payment initialized
   - User redirected to Paystack checkout

4. **Payment processing**
   - User completes payment on Paystack
   - Webhook/callback verification
   - Booking confirmed after successful payment
   - Confirmation email sent

### Testing Paystack

Use test cards:
- Card: 4111 1111 1111 1111
- CVV: any 3 digits
- Expiry: any future date
- Amount: any amount

## ✉️ Email Configuration

### Gmail Setup
1. Enable 2-Factor Authentication
2. Create app-specific password at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Use app password in `MAIL_PASSWORD`

### Custom SMTP
Update `.env`:
```
MAIL_SERVER=your-smtp-server.com
MAIL_PORT=587
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-email-password
MAIL_USE_TLS=true
```

## 🎨 Customization Guide

### Logo
- Located in `components/logo.py`
- SVG format, geometric design
- Colors: black, gold, white variants
- Update `public/logo.svg` for static version

### Colors & Styling
In `templates/base.html`:
```javascript
colors: {
  'law-dark': '#1a1a1a',      // Main dark color
  'law-blue': '#003d7a',      // Primary blue
  'law-gold': '#b8860b',      // Accent gold
  'law-gray': '#f5f5f5',      // Background
}
```

### Services
Edit `seed_database.py` to add/modify:
- Service names and descriptions
- Pricing
- Timeline
- Who it's for

Re-seed:
```bash
python seed_database.py
```

### Consultation Types
Modify in `seed_database.py`:
- Duration
- Price
- Features (document review, written advice, follow-up)

## 🔒 Security Features

✅ CSRF protection with Flask-WTF  
✅ Password hashing with Bcrypt  
✅ SQL injection prevention via SQLAlchemy ORM  
✅ XSS protection via Bleach sanitization  
✅ Rate limiting on forms  
✅ Secure session cookies  
✅ HTTPS only in production  
✅ Security headers (HSTS, CSP, X-Frame-Options)  
✅ Input validation and sanitization  
✅ Attorney-client privilege protection  

## 📊 Admin Features

### Booking Management
- View all bookings with filters
- Check payment status
- Download uploaded documents
- Add notes to bookings
- Cancel bookings if needed

### Service Management
- Create/edit services
- Set pricing tiers
- Manage timelines
- SEO metadata
- Publish/unpublish services

### Availability Management
- Set working hours
- Bulk create availability
- Manage time slots
- Set max concurrent bookings

### Blog Management
- Create/edit/delete articles
- Categories and tags
- Draft support
- SEO optimization
- Publish schedule

## 🧪 Testing

### Manual Testing Checklist

- [ ] Homepage loads correctly
- [ ] Services display with proper formatting
- [ ] Booking form validates correctly
- [ ] File upload works (PDF, DOC, DOCX)
- [ ] Paystack payment flow completes
- [ ] Confirmation email received
- [ ] Admin dashboard loads
- [ ] Mobile responsive design works
- [ ] Legal pages accessible
- [ ] Blog articles display

### Test Data
Run seed script to populate:
- 6 Services with realistic Nigerian law firm content
- 4 Consultation types with pricing
- 60 days of availability slots (Mon-Fri, 9-5)

## 📈 Performance Optimization

✅ Database indexing on frequently queried fields  
✅ Query optimization with SQLAlchemy relationships  
✅ Static file caching with cache-busting  
✅ CSS/JS minification (Tailwind via CDN)  
✅ Image optimization  
✅ Pagination on blog/articles  
✅ Connection pooling for database  

## 🐛 Debugging

### View Logs
```bash
# Development
flask run --debug

# Production (Render dashboard shows logs)
```

### Common Issues

**Payment not processing**
- Check Paystack keys in environment
- Verify account balance
- Check payment logs in Flask app

**Emails not sending**
- Verify SMTP credentials
- Check firewall allows SMTP port
- Try Gmail app-specific password

**Database errors**
- Check `DATABASE_URL` format
- Verify PostgreSQL is running
- Check connection pooling settings

## 📚 Documentation

- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Production deployment to Render
- [README.md](./README.md) - Project overview
- Code comments throughout for implementation details

## 🎯 Next Steps

1. **Customize Content**
   - Add lawyer profile
   - Update service descriptions
   - Write initial blog posts

2. **Set Up Legal Terms**
   - Customize privacy policy
   - Review terms of service
   - Add firm disclaimer

3. **Configure Emails**
   - Set up Gmail/SMTP
   - Customize email templates
   - Test email delivery

4. **Deploy to Production**
   - Create Render account
   - Deploy with guide in DEPLOYMENT_GUIDE.md
   - Set up monitoring
   - Test payment processing

5. **Marketing Preparation**
   - SEO optimization
   - Social media setup
   - Content calendar

## 💡 FAQs

**Q: Can I add more services?**
A: Yes, modify `seed_database.py` and re-seed, or add via admin panel.

**Q: How do I change pricing?**
A: Update `ConsultationType` prices in `seed_database.py` or via admin panel.

**Q: Can clients reschedule bookings?**
A: Feature framework exists for future implementation.

**Q: Is there a client portal?**
A: Planned for future enhancement; currently bookings are confirmed via email.

**Q: Can I accept payments via another gateway?**
A: Yes, replace Paystack client with another provider (Flutterwave, etc.)

---

**Happy coding. This is production-ready software for a professional Nigerian law firm. 🇳🇬⚖️**