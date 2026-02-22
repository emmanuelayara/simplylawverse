# Simply Lawverse 🇳🇬⚖️

**Professional Corporate Legal Services Website for Nigerian Lawyers**

A production-ready law firm website offering online consultations, legal services, and blog content with integrated Paystack payments for Nigeria.

---

## ✨ Features

### 🎯 Professional Website
- **Minimal, professional design** - Conservative aesthetic appropriate for law firm
- **Mobile-responsive** - Works perfectly on all devices
- **Fast loading** - Optimized performance
- **SEO-friendly** - Proper structure, meta tags, semantic HTML

### 📋 Services Management
- **6 Corporate Legal Services:**
  - Company Registration & CAC Filings
  - Contract Drafting & Review
  - Corporate Governance & Compliance
  - Regulatory Advisory
  - Due Diligence & Transaction Support
  - SME & Startup Legal Retainers

### 💼 Consultation Booking System
- **Flexible consultation packages** (30-min, 60-min, 90-min, retainer)
- **Client intake forms** with document uploads
- **Availability management** - Set working hours and time slots
- **Payment integration** - Seamless Paystack checkout
- **Confirmation emails** - Automated client notifications
- **Admin dashboard** - Manage bookings and documents

### 💳 Paystack Payment Integration
- **Secure payment processing** for Nigerian customers
- **Multiple consultation packages** at different price points
- **Payment verification** and booking confirmation
- **Invoice generation** and payment receipts
- **Support for NGN (Nigerian Naira)**

### 📝 Blog & Legal Resources
- **Legal articles** and compliance guides
- **Categories and tags** for organization
- **Search functionality** across articles
- **Related articles** suggestions
- **Professional legal content** - No lorem ipsum

### 🔐 Security & Compliance
- **Attorney-client privilege** protection
- **Secure document uploads** (PDF, DOC, DOCX)
- **CSRF protection** and input validation
- **Data encryption** and secure storage
- **Privacy policy** and legal disclaimers
- **SSL/HTTPS** in production

### 👨‍⚖️ Admin Dashboard
- **Service management** - Add, edit, publish services
- **Availability scheduling** - Set working hours
- **Booking management** - View and manage consultations
- **Client document access** - Download and review uploads
- **Article publishing** - Create and edit blog posts

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | HTML5, CSS3, Tailwind CSS |
| **Backend** | Python, Flask |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy |
| **Forms** | WTForms with validation |
| **Payments** | Paystack API |
| **Email** | Flask-Mail (SMTP) |
| **Authentication** | Flask-Login, Bcrypt |
| **Deployment** | Render (PaaS) |
| **Logo** | Custom SVG |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL
- Paystack account (free at [paystack.com](https://paystack.com))

### Installation

```bash
# Clone and setup
git clone https://github.com/yourusername/simplylawverse.git
cd simplylawverse

# Create virtual environment
python -m venv myenv
source myenv/Scripts/activate  # Windows: myenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Paystack keys, database URL, email settings

# Setup database
flask db upgrade
python seed_database.py

# Run
flask run
# Visit http://localhost:5000
```

For detailed setup, see [PROJECT_SETUP.md](./PROJECT_SETUP.md)

---

## 📦 Project Structure

```
simplylawverse/
├── app.py                      # Flask application
├── models.py                   # Database models
├── forms.py                    # Form validation
├── paystack_client.py         # Payment integration
├── seed_database.py           # Sample data
├── blueprints/
│   ├── services.py            # Services routes
│   ├── bookings.py            # Booking/payment flow
│   ├── articles.py            # Blog articles
│   └── ...
├── templates/
│   ├── pages/                 # Public pages
│   ├── services/              # Service pages
│   ├── bookings/              # Booking forms
│   └── legal/                 # Legal pages
└── static/
    ├── uploads/               # Client documents
    └── logo.svg              # Brand logo
```

---

## 🌐 Site Routes

### Public Pages
- `/` - Homepage with services overview
- `/services` - All services listing
- `/services/<slug>` - Individual service detail
- `/blog` - Legal articles and insights
- `/about` - About lawyer and firm
- `/book` - Book consultation (3-step form)
- `/contact` - Get in touch
- `/legal/privacy-policy` - Privacy policy
- `/legal/terms` - Terms of service
- `/legal/disclaimer` - Legal disclaimer

### Admin Routes (Protected)
- `/admin/` - Dashboard
- `/admin/services` - Manage services
- `/admin/bookings` - View and manage bookings
- `/admin/availability` - Set working hours
- `/admin/articles` - Manage blog content

---

## 💳 Payment Flow

```
1. User fills intake form (name, company, issue description)
   ↓
2. User selects consultation type & available time slot
   ↓
3. Booking confirmation with price in NGN
   ↓
4. Redirected to Paystack checkout
   ↓
5. User completes payment
   ↓
6. Payment verified & booking confirmed
   ↓
7. Confirmation email sent to client
   ↓
8. Admin notified of new booking
```

---

## ⚙️ Configuration

### Environment Variables

```env
# Flask
FLASK_ENV=production
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:password@host:5432/lawfirm

# Paystack
PAYSTACK_PUBLIC_KEY=pk_live_xxxxx
PAYSTACK_SECRET_KEY=sk_live_xxxxx

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Upload
MAX_CONTENT_LENGTH=5242880
UPLOAD_FOLDER=static/uploads
```

### Services Customization

Edit `seed_database.py`:
- Add/modify services and pricing
- Set consultation durations
- Update availability hours

---

## 🎨 Design

### Brand Colors
- **Dark Navy** (#1a1a1a) - Main text and headings
- **Professional Blue** (#003d7a) - Primary action color
- **Muted Gold** (#b8860b) - Accent color
- **Off-white** (#fafaf8) - Background

### Typography
- **Serif fonts** for professional headings
- **Sans-serif** for body text
- **High contrast** for accessibility
- **Generous spacing** for readability

### Logo
Custom minimal geometric SVG:
- No gavels or scales clichés
- Thin, professional lines
- Works in black, white, and gold
- Symmetrical and balanced

---

## 📱 Responsive Design

✅ Mobile-first approach  
✅ Tailwind CSS responsive utilities  
✅ Touch-friendly buttons and forms  
✅ Readable font sizes on all devices  
✅ Optimized for screens 320px to 4K  

---

## 🔒 Security

✅ CSRF protection  
✅ SQL injection prevention  
✅ XSS protection  
✅ Secure password hashing  
✅ Input validation  
✅ Secure file uploads  
✅ HTTPS/SSL in production  
✅ Rate limiting  
✅ Secure session management  
✅ Attorney-client privileged communication  

---

## 📊 Database Models

### Main Models
- **Service** - Legal services offered
- **ConsultationType** - Consultation packages
- **Booking** - Consultation appointments with payment
- **ClientIntake** - Initial client information
- **AdminAvailability** - Lawyer availability slots
- **Article** - Blog articles and legal resources
- **User** - Admin users
- **Comment** - Article comments

All models include:
- Proper indexing for performance
- Relationships and constraints
- Timestamps and status tracking
- Soft delete support where appropriate

---

## 🚀 Deployment

### Deploy to Render

1. Create Render account
2. Connect GitHub repository
3. Create PostgreSQL database
4. Set environment variables
5. Deploy with automatic updates

For detailed instructions, see [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

### Production Checklist
- [ ] Set `FLASK_ENV=production`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure Paystack live keys
- [ ] Set up email (Gmail or custom SMTP)
- [ ] Enable database backups
- [ ] Review security headers
- [ ] Test payment processing
- [ ] Update legal disclaimers

---

## 📧 Email Integration

Automated emails sent for:
- **Booking confirmations** - Sent to client after payment
- **Admin notifications** - Alert on new bookings
- **Password resets** - Secure reset links
- **Contact form responses** - Acknowledgment emails

Supports:
- Gmail (with app passwords)
- Custom SMTP servers
- All major email providers

---

## 📚 Documentation

- **[PROJECT_SETUP.md](./PROJECT_SETUP.md)** - Complete setup guide
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Production deployment
- **Inline code comments** - Implementation details
- **Model docstrings** - Database structure

---

## 🧪 Testing

### Test Paystack Payment
Use test cards from Paystack documentation:
- Card: 4111 1111 1111 1111
- CVV: any 3 digits
- Expiry: any future date

### Manual Test Checklist
- [ ] Booking form validation
- [ ] File upload (PDF, DOC, DOCX)
- [ ] Paystack payment flow
- [ ] Email delivery
- [ ] Mobile responsiveness
- [ ] Admin dashboard access
- [ ] Database queries performance

---

## 🎯 Use Cases

### Perfect For
✅ Nigerian corporate law practitioners  
✅ Freelance lawyers wanting to scale  
✅ Law firms targeting startups/SMEs  
✅ Lawyers offering remote consultations  
✅ Legal service providers needing online presence  

### Typical Users
- 📊 **Corporate lawyers** offering retainer services
- 🚀 **Startup lawyers** serving founders
- 💼 **SME advisors** helping small businesses
- 🌍 **Remote consultants** in Nigeria

---

## 🔄 Future Enhancements

Planned features:
- [ ] Client portal for viewing past consultations
- [ ] Retainer subscription management
- [ ] Legal templates library
- [ ] Compliance reminder system
- [ ] WhatsApp integration for bookings
- [ ] Invoice and receipt generation
- [ ] Document e-signature support
- [ ] Video consultation integration

---

## 📝 Legal Compliance

This website includes:
- Privacy policy template
- Terms of service
- Legal disclaimer
- Attorney-client privilege notice
- Consultation limitations
- Refund policy

**Lawyers using this platform should:**
- ✓ Customize with firm details
- ✓ Review legal disclaimers
- ✓ Ensure compliance with local bar regulations
- ✓ Maintain confidentiality
- ✓ Have errors & omissions insurance

---

## 🆘 Troubleshooting

### Common Issues

**Paystack payment not working**
- Verify secret key is correct
- Check account has sufficient balance
- Review payment logs

**Emails not sending**
- Verify SMTP credentials
- Use Gmail app-specific password (not regular password)
- Check firewall allows SMTP port

**Database connection error**
- Verify PostgreSQL is running
- Check `DATABASE_URL` format
- Confirm database exists

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for more troubleshooting.

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make your changes
4. Submit pull request

---

## 📄 License

This project is provided as-is for Nigerian law practitioners. Customize and deploy for your practice.

---

## 📞 Support

For questions or issues:
1. Check documentation first
2. Review code comments
3. Check Flask/Paystack logs
4. Test in development environment

---

## 🙏 Acknowledgments

Built with ❤️ for Nigerian lawyers and entrepreneurs.

- Inspired by professional legal practices
- Designed for African business context
- Built for Nigerian payment ecosystem (Paystack)
- Focused on accessibility and clarity

---

## 🎉 Get Started

```bash
# Clone repository
git clone <your-repo-url>
cd simplylawverse

# Follow PROJECT_SETUP.md for full instructions
```

**Your professional law firm website awaits! 🚀**

---

**Made for Nigerian Lawyers 🇳🇬 | Production Ready ✅ | Paystack Integrated ✅ | Open Source ❤️**

**Last Updated: February 2026**