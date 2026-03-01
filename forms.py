from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, HiddenField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
import re

def validate_email_format(form, field):
    """Custom email validator with strict formatting"""
    if not field.data:
        return
    
    # RFC 5322 simplified pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, field.data):
        raise ValidationError('Invalid email address format.')
    
    # Check length
    if len(field.data) > 120:
        raise ValidationError('Email address is too long (max 120 characters).')

def validate_no_xss(form, field):
    """Validator to detect common XSS patterns"""
    if not field.data:
        return
    
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'on\w+\s*=',  # onerror=, onclick=, etc.
        r'<iframe',
        r'<object',
        r'<embed',
        r'<img.*?on'
    ]
    
    text_lower = field.data.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, text_lower):
            raise ValidationError('Input contains potentially dangerous content.')

class CommentForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired('Name is required.'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters.'),
        validate_no_xss
    ])
    email = StringField('Email', validators=[
        Optional(),
        Length(max=120, message='Email must not exceed 120 characters.'),
        validate_email_format
    ])
    content = TextAreaField('Comment', validators=[
        DataRequired('Comment is required.'),
        Length(min=2, max=5000, message='Comment must be between 2 and 5000 characters.'),
        validate_no_xss
    ])
    parent_id = HiddenField()
    submit = SubmitField('Post Comment')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired('Name is required.'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters.'),
        validate_no_xss
    ])
    email = StringField('Email', validators=[
        DataRequired('Email is required.'),
        Length(max=120, message='Email must not exceed 120 characters.'),
        validate_email_format
    ])
    message = TextAreaField('Message', validators=[
        DataRequired('Message is required.'),
        Length(min=10, max=5000, message='Message must be between 10 and 5000 characters.'),
        validate_no_xss
    ])
    submit = SubmitField('Send')


class AdminRegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=150)])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(),EqualTo('password', message='Passwords must match.')])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Reset Password')

class ArticleSubmissionForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired('Title is required.'),
        Length(min=5, max=200, message='Title must be between 5 and 200 characters.'),
        validate_no_xss
    ])
    author = StringField('Author Name', validators=[
        Optional(),  # Not required for authenticated users
        Length(min=2, max=100, message='Author name must be between 2 and 100 characters.'),
        validate_no_xss
    ])
    content = TextAreaField('Content', validators=[
        DataRequired('Article content is required.'),
        Length(min=50, max=50000, message='Content must be between 50 and 50,000 characters.'),
        validate_no_xss
    ])
    email = StringField('Email Address', validators=[
        Optional(),  # Not required for authenticated users
        Length(max=120, message='Email must not exceed 120 characters.'),
        validate_email_format
    ])
    category = SelectField('Category', validators=[DataRequired('Category is required.')], choices=[])
    cover_image = FileField('Cover Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only image files are allowed (JPG, PNG, GIF).')
    ])
    document = FileField('Supporting Document', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx'], 'Only documents are allowed (PDF, DOC, DOCX).')
    ])
    submit = SubmitField('Submit')
    
    def validate_author(self, field):
        """Ensure author is provided for guest users"""
        if not current_user.is_authenticated and not field.data:
            raise ValidationError('Author name is required.')
    
    def validate_email(self, field):
        """Ensure email is provided for guest users"""
        if not current_user.is_authenticated and not field.data:
            raise ValidationError('Email address is required.')


class EditProfileForm(FlaskForm):
    """Form for users to edit their profile information"""
    username = StringField('Username', validators=[
        DataRequired('Username is required.'),
        Length(min=3, max=150, message='Username must be between 3 and 150 characters.'),
        validate_no_xss
    ])
    email = StringField('Email Address', validators=[
        DataRequired('Email is required.'),
        Length(max=120, message='Email must not exceed 120 characters.'),
        validate_email_format
    ])
    submit = SubmitField('Save Changes')
    
    def validate_username(self, field):
        """Check if username is already taken by another user"""
        from models import User
        if field.data != current_user.username:
            user = User.query.filter_by(username=field.data).first()
            if user:
                raise ValidationError('Username already taken. Please choose another.')
    
    def validate_email(self, field):
        """Check if email is already registered to another user"""
        from models import User
        if field.data != current_user.email:
            user = User.query.filter_by(email=field.data).first()
            if user:
                raise ValidationError('Email already registered. Please use another.')


class ChangePasswordForm(FlaskForm):
    """Form for users to change their password"""
    current_password = PasswordField('Current Password', validators=[
        DataRequired('Current password is required.')
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired('New password is required.'),
        Length(min=8, message='Password must be at least 8 characters.'),
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired('Please confirm your new password.'),
        EqualTo('new_password', message='Passwords must match.')
    ])
    submit = SubmitField('Change Password')
    
    def validate_current_password(self, field):
        """Verify that current password is correct"""
        from werkzeug.security import check_password_hash
        if not check_password_hash(current_user.password, field.data):
            raise ValidationError('Current password is incorrect.')
    
    def validate_new_password(self, field):
        """Ensure new password is different from old password"""
        from werkzeug.security import check_password_hash
        if check_password_hash(current_user.password, field.data):
            raise ValidationError('New password must be different from current password.')
        
        # Check password strength requirements
        password = field.data
        has_uppercase = any(c.isupper() for c in password)
        has_lowercase = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{};\':"|,.<>?/' for c in password)
        
        if not (has_uppercase and has_lowercase and has_digit and has_special):
            raise ValidationError(
                'Password must contain uppercase, lowercase, number, and special character.'
            )


# ==================== CORPORATE LAW FIRM FORMS ====================

class ClientIntakeForm(FlaskForm):
    """Form for initial client intake - collects info before booking"""
    
    full_name = StringField('Full Name', validators=[
        DataRequired('Full name is required.'),
        Length(min=2, max=150, message='Name must be between 2 and 150 characters.'),
        validate_no_xss
    ])
    
    email = StringField('Email Address', validators=[
        DataRequired('Email is required.'),
        Email('Invalid email address.'),
        validate_email_format
    ])
    
    phone = StringField('Phone Number', validators=[
        DataRequired('Phone number is required.'),
        Length(min=10, max=20, message='Phone must be between 10 and 20 characters.'),
    ])
    
    company_name = StringField('Company Name', validators=[
        Optional(),
        Length(min=2, max=200, message='Company name must be between 2 and 200 characters.'),
        validate_no_xss
    ])
    
    cac_status = SelectField('CAC Registration Status', 
        choices=[
            ('', 'Select CAC Status (Optional)'),
            ('registered', 'Company Registered with CAC'),
            ('not_registered', 'Not Yet Registered with CAC'),
        ],
        validators=[Optional()]
    )
    
    issue_description = TextAreaField('Describe Your Legal Issue', validators=[
        DataRequired('Please describe your legal issue.'),
        Length(min=20, max=2000, message='Description must be between 20 and 2000 characters.'),
        validate_no_xss
    ], render_kw={"rows": 6, "placeholder": "Please provide details about your legal matter..."})
    
    document_upload = FileField('Upload Supporting Document (PDF, DOC, DOCX)', validators=[
        FileAllowed(['pdf', 'doc', 'docx'], 'Only PDF and Word documents allowed.'),
    ])
    
    submit = SubmitField('Submit Intake Form')


class BookingSelectionForm(FlaskForm):
    """Form for selecting consultation type and date"""
    
    consultation_type_id = SelectField('Select Consultation Type',
        coerce=int,
        validators=[DataRequired('Please select a consultation type.')]
    )
    
    scheduled_date = StringField('Preferred Date & Time',
        validators=[DataRequired('Please select a date and time.')]
    )
    
    submit = SubmitField('Continue to Payment')


class BookingConfirmationForm(FlaskForm):
    """Form for final booking confirmation before payment"""
    
    client_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=150),
    ])
    
    client_email = StringField('Email', validators=[
        DataRequired(),
        Email(),
    ])
    
    client_phone = StringField('Phone Number', validators=[
        DataRequired(),
        Length(min=10, max=20),
    ])
    
    company_name = StringField('Company Name', validators=[
        DataRequired(),
        Length(min=2, max=200),
    ])
    
    cac_status = SelectField('CAC Status',
        choices=[
            ('registered', 'Registered'),
            ('not_registered', 'Not Registered'),
        ],
        validators=[DataRequired()]
    )
    
    issue_description = TextAreaField('Legal Issue Description', validators=[
        DataRequired(),
        Length(min=20, max=2000),
    ], render_kw={"rows": 4})
    
    document_upload = FileField('Upload Document (Optional)', validators=[
        FileAllowed(['pdf', 'doc', 'docx'], 'PDF and Word documents only.'),
    ])
    
    consent = HiddenField('consent', validators=[DataRequired()])  # Hidden field for consent checkbox
    
    submit = SubmitField('Proceed to Payment')


class ServiceForm(FlaskForm):
    """Admin form for managing services"""
    
    name = StringField('Service Name', validators=[
        DataRequired(),
        Length(min=5, max=200),
    ])
    
    slug = StringField('URL Slug', validators=[
        DataRequired(),
        Length(min=5, max=200),
    ])
    
    description = TextAreaField('Short Description', validators=[
        DataRequired(),
        Length(min=20, max=500),
    ])
    
    detailed_content = TextAreaField('Detailed Service Description', validators=[
        DataRequired(),
        Length(min=100, max=5000),
    ], render_kw={"rows": 10})
    
    who_needs_it = TextAreaField('Who This Service is For', validators=[
        DataRequired(),
        Length(min=50, max=1000),
    ])
    
    typical_timeline = StringField('Typical Timeline', validators=[
        DataRequired(),
        Length(min=5, max=100),
    ])
    
    base_price = StringField('Base Price (NGN)', validators=[Optional()])
    
    seo_title = StringField('SEO Title', validators=[Optional(), Length(max=255)])
    seo_description = StringField('SEO Description', validators=[Optional(), Length(max=500)])
    seo_keywords = StringField('SEO Keywords', validators=[Optional(), Length(max=500)])
    
    submit = SubmitField('Save Service')


class ConsultationTypeForm(FlaskForm):
    """Admin form for managing consultation types"""
    
    name = StringField('Consultation Type Name', validators=[
        DataRequired(),
        Length(min=5, max=150),
    ])
    
    duration_minutes = StringField('Duration (minutes)', validators=[
        DataRequired(),
    ])
    
    price_naira = StringField('Price (NGN)', validators=[
        DataRequired(),
    ])
    
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=20, max=500),
    ], render_kw={"rows": 4})
    
    includes_document_review = SelectField('Includes Document Review',
        choices=[('', 'No'), ('yes', 'Yes')],
        validators=[Optional()]
    )
    
    includes_written_advice = SelectField('Includes Written Advice',
        choices=[('', 'No'), ('yes', 'Yes')],
        validators=[Optional()]
    )
    
    includes_follow_up = SelectField('Includes Follow-up Session',
        choices=[('', 'No'), ('yes', 'Yes')],
        validators=[Optional()]
    )
    
    submit = SubmitField('Save Consultation Type')


class AvailabilityForm(FlaskForm):
    """Admin form for managing availability"""
    
    date = StringField('Date', validators=[
        DataRequired('Date is required.'),
    ])
    
    start_time = StringField('Start Time', validators=[
        DataRequired('Start time is required.'),
    ])
    
    end_time = StringField('End Time', validators=[
        DataRequired('End time is required.'),
    ])
    
    slot_duration_minutes = StringField('Slot Duration (minutes)', validators=[
        DataRequired(),
    ])
    
    max_slots = StringField('Maximum Slots', validators=[
        DataRequired(),
    ])
    
    notes = TextAreaField('Notes', validators=[Optional()])
    
    submit = SubmitField('Save Availability')