from datetime import datetime, timedelta
from extensions import db
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer
import os
import hashlib
from enum import Enum


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(100), nullable=False)
    __table_args__ = (
        db.UniqueConstraint('email', name='uq_user_email'),
    )
    
    def get_reset_token(self, expires_sec=1800):
        """Generate a password reset token (valid for 30 minutes)"""
        s = URLSafeTimedSerializer(os.environ.get('SECRET_KEY', 'dev-secret-key'))
        return s.dumps({'user_id': self.id})
    
    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        """Verify password reset token and return user if valid"""
        s = URLSafeTimedSerializer(os.environ.get('SECRET_KEY', 'dev-secret-key'))
        try:
            data = s.loads(token, max_age=expires_sec)
            return User.query.get(data.get('user_id'))
        except Exception:
            return None



class Article(db.Model):
    """
    Article model with optimized design.
    
    Status field consolidates approval workflow:
    - 'pending': Initial submission, awaiting review
    - 'approved': Approved and published
    - 'rejected': Rejected by admin
    - 'archived': Archived/deleted content
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Optimized status field (replaces redundant 'approved' boolean)
    # Values: 'pending', 'approved', 'rejected', 'archived'
    status = db.Column(
        db.String(20),
        nullable=False,
        default='pending',
        index=True  # ✅ Frequently queried
    )
    
    # Content metadata
    category = db.Column(
        db.String(100),
        nullable=False,
        default='General',
        index=True  # ✅ Frequently used for filtering
    )
    
    # Engagement metrics
    likes = db.Column(db.Integer, default=0, nullable=False)
    views = db.Column(db.Integer, default=0, nullable=False)
    
    # File attachments
    cover_image = db.Column(db.String(255), nullable=True)
    document_filename = db.Column(db.String(255), nullable=True)
    
    # ✅ Soft delete support - allows retracting deleted articles
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # ✅ Draft support - authors can save drafts before submission
    is_draft = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    comments = db.relationship('Comment', backref='article', lazy=True, cascade='all, delete-orphan')
    visits = db.relationship('Visit', backref='article', lazy=True, cascade='all, delete-orphan')
    
    # Composite index for common queries (status + category)
    __table_args__ = (
        db.Index('idx_article_status_category', 'status', 'category'),
        db.Index('idx_article_date_posted', 'date_posted'),
        db.Index('idx_article_deleted_at', 'deleted_at'),  # ✅ For soft delete queries
        db.Index('idx_article_is_draft', 'is_draft'),  # ✅ For draft queries
    )
    
    def soft_delete(self):
        """Soft delete article - marks as deleted but retains data"""
        self.deleted_at = datetime.utcnow()
        self.status = 'archived'
    
    def restore(self):
        """Restore soft-deleted article"""
        self.deleted_at = None
    
    def is_deleted(self):
        """Check if article is soft-deleted"""
        return self.deleted_at is not None
    
    def __repr__(self):
        return f'<Article {self.id}: {self.title[:30]}>'


class Comment(db.Model):
    """
    Comment model for article discussions.
    
    Email is required to track commenter identity.
    Use 'Anonymous <random>' format for anonymous comments.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(
        db.String(120),
        nullable=False,  # ✅ Required field
        default='anonymous'
    )
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Foreign keys with indices for quick lookup
    article_id = db.Column(
        db.Integer,
        db.ForeignKey('article.id'),
        nullable=False,
        index=True  # ✅ Frequently queried
    )
    parent_id = db.Column(
        db.Integer,
        db.ForeignKey('comment.id'),
        nullable=True,
        index=True  # ✅ For nested comment queries
    )
    
    # ✅ Soft delete support - allows retracting comments
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    replies = db.relationship(
        'Comment',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # Composite index for efficient article comment queries
    __table_args__ = (
        db.Index('idx_comment_article_date', 'article_id', 'date_posted'),
        db.Index('idx_comment_deleted_at', 'deleted_at'),  # ✅ For soft delete queries
    )
    
    def soft_delete(self):
        """Soft delete comment - marks as deleted but retains data"""
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Restore soft-deleted comment"""
        self.deleted_at = None
    
    def is_deleted(self):
        """Check if comment is soft-deleted"""
        return self.deleted_at is not None
    
    def __repr__(self):
        return f'<Comment {self.id}: {self.name}>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)


class Visit(db.Model):
    """
    Enhanced visit tracking model.
    
    Tracks article visits with user/session identification for unique visitor analytics.
    
    Visitor Identification Strategy:
    1. For authenticated users: Use user_id
    2. For anonymous users: Use session_id (from Flask session)
    3. Fallback: Use IP + user_agent hash
    """
    id = db.Column(db.Integer, primary_key=True)
    
    # Article reference
    article_id = db.Column(
        db.Integer,
        db.ForeignKey('article.id', name='fk_visit_article_id'),
        nullable=False,
        index=True  # ✅ Frequently queried
    )
    
    # Visitor identification (in priority order)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', name='fk_visit_user_id'),
        nullable=True,
        index=True  # ✅ For authenticated user analytics
    )
    session_id = db.Column(
        db.String(255),
        nullable=True,
        index=True  # ✅ For anonymous session tracking
    )
    ip_address = db.Column(db.String(45), nullable=True)  # Supports IPv4 and IPv6
    
    # Visitor fingerprint (for deduplication)
    visitor_hash = db.Column(
        db.String(64),
        nullable=True,
        index=True  # ✅ For unique visitor identification
    )
    
    # Metadata
    user_agent = db.Column(db.String(500), nullable=True)
    referer = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    duration_seconds = db.Column(db.Integer, default=0, nullable=False)  # Time spent on page
    
    # Relationship
    user = db.relationship('User', backref='visits', foreign_keys=[user_id])
    
    # Composite indices for analytics queries
    __table_args__ = (
        db.Index('idx_visit_article_date', 'article_id', 'timestamp'),
        db.Index('idx_visit_user_date', 'user_id', 'timestamp'),
        db.Index('idx_visit_session_date', 'session_id', 'timestamp'),
        db.Index('idx_visit_hash_date', 'visitor_hash', 'timestamp'),
    )
    
    @staticmethod
    def generate_visitor_hash(ip_address, user_agent):
        """Generate unique visitor hash from IP and user agent"""
        if not ip_address or not user_agent:
            return None
        fingerprint = f"{ip_address}:{user_agent}"
        return hashlib.sha256(fingerprint.encode()).hexdigest()
    
    def __repr__(self):
        return f'<Visit {self.id}: Article {self.article_id} at {self.timestamp}>'


# ==================== CORPORATE LAW SERVICES ====================

class Service(db.Model):
    """
    Legal service offerings model
    Represents the different corporate legal services offered by the firm
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=False)  # Short description
    detailed_content = db.Column(db.Text, nullable=False)  # Full service page content
    
    # Service details
    who_needs_it = db.Column(db.Text, nullable=False)  # Target audience
    typical_timeline = db.Column(db.String(255), nullable=False)  # e.g., "2-4 weeks"
    base_price = db.Column(db.Float, nullable=True)  # Optional starting price
    
    # Metadata
    icon_class = db.Column(db.String(100), nullable=True)  # For styling
    order = db.Column(db.Integer, default=0)  # Display order
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # SEO
    seo_title = db.Column(db.String(255), nullable=True)
    seo_description = db.Column(db.String(500), nullable=True)
    seo_keywords = db.Column(db.String(500), nullable=True)
    
    # Relationships
    bookings = db.relationship('Booking', backref='service', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.Index('idx_service_slug', 'slug'),
        db.Index('idx_service_is_active', 'is_active'),
        db.Index('idx_service_order', 'order'),
    )
    
    def __repr__(self):
        return f'<Service {self.name}>'


class ConsultationType(db.Model):
    """
    Consultation type model
    Defines different consultation packages (30-min, 60-min, retainer, etc.)
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)  # 30, 60, etc.
    price_naira = db.Column(db.Float, nullable=False)  # Price in NGN
    description = db.Column(db.Text, nullable=False)
    
    # Features/includes
    includes_document_review = db.Column(db.Boolean, default=False)
    includes_written_advice = db.Column(db.Boolean, default=False)
    includes_follow_up = db.Column(db.Boolean, default=False)
    
    # Admin settings
    is_active = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='consultation_type', lazy=True)
    
    __table_args__ = (
        db.Index('idx_consultation_is_active', 'is_active'),
        db.Index('idx_consultation_order', 'order'),
    )
    
    def __repr__(self):
        return f'<ConsultationType {self.name} ({self.duration_minutes}min)>'


class ClientIntake(db.Model):
    """
    Client intake form submission
    Collects preliminary information before booking
    """
    id = db.Column(db.Integer, primary_key=True)
    
    # Personal information
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    
    # Company information
    company_name = db.Column(db.String(200), nullable=False)
    cac_status = db.Column(db.String(50), nullable=False)  # "Registered" or "Not registered"
    
    # Legal issue details
    issue_description = db.Column(db.Text, nullable=False)
    
    # Document upload
    document_filename = db.Column(db.String(255), nullable=True)
    document_path = db.Column(db.String(500), nullable=True)
    document_upload_date = db.Column(db.DateTime, nullable=True)
    
    # Status
    status = db.Column(db.String(50), default='pending', nullable=False)  # pending, reviewed, scheduled, archived
    notes = db.Column(db.Text, nullable=True)  # Admin notes
    
    # Metadata
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    reviewed_by = db.relationship('User', backref='intake_reviews')
    
    __table_args__ = (
        db.Index('idx_intake_email', 'email'),
        db.Index('idx_intake_status', 'status'),
        db.Index('idx_intake_submitted_at', 'submitted_at'),
    )
    
    def __repr__(self):
        return f'<ClientIntake {self.full_name} - {self.company_name}>'


class Booking(db.Model):
    """
    Consultation booking model
    Represents a scheduled consultation appointment with payment tracking
    """
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic information
    client_name = db.Column(db.String(150), nullable=False)
    client_email = db.Column(db.String(120), nullable=False)
    client_phone = db.Column(db.String(20), nullable=False)
    
    # Company information
    company_name = db.Column(db.String(200), nullable=False)
    cac_status = db.Column(db.String(50), nullable=False)  # "Registered" or "Not registered"
    
    # Legal issue
    issue_description = db.Column(db.Text, nullable=False)
    
    # Appointment details
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False, index=True)
    consultation_type_id = db.Column(db.Integer, db.ForeignKey('consultation_type.id'), nullable=False, index=True)
    scheduled_date = db.Column(db.DateTime, nullable=False)
    
    # Payment information
    amount_naira = db.Column(db.Float, nullable=False)
    payment_reference = db.Column(db.String(255), nullable=True, unique=True, index=True)  # Paystack reference
    payment_status = db.Column(db.String(50), default='pending', nullable=False)  # pending, completed, failed, refunded
    
    # Status
    booking_status = db.Column(db.String(50), default='pending', nullable=False)  # pending, confirmed, completed, cancelled
    
    # Document upload
    document_filename = db.Column(db.String(255), nullable=True)
    document_path = db.Column(db.String(500), nullable=True)
    
    # Confirmation
    confirmation_token = db.Column(db.String(255), nullable=True, unique=True)
    email_sent = db.Column(db.Boolean, default=False)
    email_sent_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payment_completed_at = db.Column(db.DateTime, nullable=True)
    consultation_date_start = db.Column(db.DateTime, nullable=True)
    consultation_date_end = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Admin notes
    admin_notes = db.Column(db.Text, nullable=True)
    
    __table_args__ = (
        db.Index('idx_booking_client_email', 'client_email'),
        db.Index('idx_booking_scheduled_date', 'scheduled_date'),
        db.Index('idx_booking_payment_status', 'payment_status'),
        db.Index('idx_booking_booking_status', 'booking_status'),
        db.Index('idx_booking_service_id', 'service_id'),
        db.Index('idx_booking_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f'<Booking {self.client_name} - {self.scheduled_date}>'
    
    def is_payment_completed(self):
        """Check if payment is completed"""
        return self.payment_status == 'completed'
    
    def is_confirmed(self):
        """Check if booking is confirmed"""
        return self.booking_status == 'confirmed' and self.is_payment_completed()
    
    @staticmethod
    def generate_confirmation_token():
        """Generate a unique confirmation token"""
        return os.urandom(32).hex()


class AdminAvailability(db.Model):
    """
    Admin availability management
    Track when the lawyer is available for consultations
    """
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)  # e.g., 09:00
    end_time = db.Column(db.Time, nullable=False)    # e.g., 17:00
    is_available = db.Column(db.Boolean, default=True)
    max_slots = db.Column(db.Integer, default=1)  # How many slots available
    
    # Slot duration (usually matches consultation type)
    slot_duration_minutes = db.Column(db.Integer, default=30)
    
    # Notes
    notes = db.Column(db.String(255), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_availability_date', 'date'),
        db.Index('idx_availability_is_available', 'is_available'),
        db.UniqueConstraint('date', 'start_time', 'end_time', name='uq_availability_slot'),
    )
    
    def __repr__(self):
        return f'<AdminAvailability {self.date} {self.start_time}-{self.end_time}>'
    
    def get_available_slots(self):
        """Calculate available time slots for this availability window"""
        from datetime import time, datetime as dt, timedelta
        
        slots = []
        start_dt = dt.combine(self.date, self.start_time)
        end_dt = dt.combine(self.date, self.end_time)
        current = start_dt
        
        while current + timedelta(minutes=self.slot_duration_minutes) <= end_dt:
            slot_end = current + timedelta(minutes=self.slot_duration_minutes)
            slots.append({
                'start': current,
                'end': slot_end,
                'start_time': current.strftime('%H:%M'),
                'end_time': slot_end.strftime('%H:%M'),
            })
            current = slot_end
        
        return slots