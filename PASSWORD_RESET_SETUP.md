# Password Reset Setup Guide

## Overview
The forgot password feature allows users to reset their password via email. This uses Flask-Mail to send secure password reset tokens.

## Setup Instructions

### 1. Gmail Setup (Recommended for Development)

If using Gmail, follow these steps:

1. **Enable 2-Factor Authentication** on your Gmail account:
   - Go to https://myaccount.google.com
   - Click "Security" on the left
   - Scroll to "How you sign in to Google"
   - Enable 2-Step Verification

2. **Generate an App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Google will generate a 16-character password
   - Copy this password

3. **Update `.env` file**:
   ```
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=xxxx xxxx xxxx xxxx  (the 16-char password from step 2)
   MAIL_DEFAULT_SENDER=noreply@simplylawverse.com
   ```

4. **Test the setup**:
   ```bash
   python -c "
   from app import app, mail
   with app.app_context():
       from flask_mail import Message
       msg = Message('Test Email', recipients=['your-email@gmail.com'], body='Test')
       mail.send(msg)
       print('✓ Test email sent successfully!')
   "
   ```

### 2. Alternative Email Services

#### SendGrid
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=SG.xxxxxxxxxxxxx
```

#### AWS SES
```env
MAIL_SERVER=email-smtp.region.amazonaws.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-username
MAIL_PASSWORD=your-password
```

#### Mailgun
```env
MAIL_SERVER=smtp.mailgun.org
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=postmaster@yourdomain.com
MAIL_PASSWORD=your-password
```

## How It Works

### User Flow:
1. User clicks "Forgot Password" on login page
2. User enters their email address
3. System generates a secure token (valid for 30 minutes)
4. Email is sent with a reset link containing the token
5. User clicks link in email
6. User enters new password
7. Password is updated and user can log in

### Security Features:
- ✓ Tokens expire after 30 minutes
- ✓ Tokens are cryptographically signed
- ✓ Only registered email receives the reset link
- ✓ No email enumeration (same message for valid/invalid emails)
- ✓ New password is hashed before storing

## Files Modified/Created

### Modified:
- `.env` - Added email configuration
- `extensions.py` - Added Flask-Mail initialization
- `app.py` - Added mail configuration
- `forms.py` - Added ForgotPasswordForm and ResetPasswordForm
- `models.py` - Added token generation/verification methods to User model
- `routes.py` - Added forgot_password and reset_password routes
- `templates/admin_login.html` - Added forgot password link

### Created:
- `templates/forgot_password.html` - Forgot password form
- `templates/reset_password.html` - Reset password form

## Testing the Feature

### Without sending real emails (Development):
```bash
# Set testing mode in .env
MAIL_DEBUG=True
```

### With real emails:
Make sure `.env` is configured with valid email credentials.

### Manual testing:
1. Register an admin account
2. Log out
3. Click "Forgot Password" on login page
4. Enter your email
5. Check your email for reset link
6. Click link and set new password
7. Log in with new password

## Troubleshooting

### "Email service is currently unavailable"
- Check `.env` has correct email credentials
- Verify MAIL_SERVER and MAIL_PORT are correct
- Check if 2FA is enabled for Gmail

### Email not arriving
- Check spam folder
- Verify sender email is correct
- Check app logs for errors

### Token expired error
- Tokens valid for 30 minutes
- User must click reset link within 30 minutes
- If expired, user can request another reset

### "Invalid or expired token"
- Token may have expired (30 min timeout)
- URL may have been modified
- Try requesting another password reset

## Environment Variables Needed

```env
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@simplylawverse.com
```

## Production Deployment

For production, use a transactional email service like:
- SendGrid (recommended)
- AWS SES
- Mailgun
- Postmark

This ensures better deliverability and provides bounce handling.

## References
- [Flask-Mail Documentation](https://pythonhosted.org/Flask-Mail/)
- [itsdangerous Documentation](https://itsdangerous.palletsprojects.com/)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
