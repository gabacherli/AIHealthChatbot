"""
Database models for the Health Chatbot application.
This module contains SQLAlchemy models for user management and patient-professional relationships.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model for patients and healthcare professionals."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)  # 'patient' or 'professional'
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    # Professional-specific fields
    license_number = db.Column(db.String(50), nullable=True)
    specialty = db.Column(db.String(100), nullable=True)
    organization = db.Column(db.String(200), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    patient_relationships = db.relationship(
        'PatientProfessionalRelationship',
        foreign_keys='PatientProfessionalRelationship.patient_id',
        backref='patient',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    professional_relationships = db.relationship(
        'PatientProfessionalRelationship',
        foreign_keys='PatientProfessionalRelationship.professional_id',
        backref='professional',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # Audit logs
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, username, password, role, email=None, first_name=None, last_name=None):
        """Initialize a user."""
        self.username = username
        self.set_password(password)
        self.role = role
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary."""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }
        
        if self.role == 'professional':
            data.update({
                'license_number': self.license_number,
                'specialty': self.specialty,
                'organization': self.organization
            })
        
        if include_sensitive:
            data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        
        return data
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class PatientProfessionalRelationship(db.Model):
    """Model for patient-professional relationships."""
    
    __tablename__ = 'patient_professional_relationships'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Relationship details
    relationship_status = db.Column(
        db.String(20), 
        nullable=False, 
        default='active',
        index=True
    )  # 'active', 'pending', 'inactive', 'terminated'
    
    relationship_type = db.Column(
        db.String(50), 
        nullable=False, 
        default='primary_care'
    )  # 'primary_care', 'specialist', 'consultant', 'emergency', 'referral'
    
    # Permissions
    can_view_documents = db.Column(db.Boolean, default=True, nullable=False)
    can_add_notes = db.Column(db.Boolean, default=True, nullable=False)
    can_request_tests = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    
    # Metadata
    notes = db.Column(db.Text, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('patient_id', 'professional_id', name='unique_patient_professional'),
        db.CheckConstraint('patient_id != professional_id', name='different_users'),
    )
    
    def __init__(self, patient_id, professional_id, relationship_type='primary_care', 
                 relationship_status='active', created_by_id=None):
        """Initialize a relationship."""
        self.patient_id = patient_id
        self.professional_id = professional_id
        self.relationship_type = relationship_type
        self.relationship_status = relationship_status
        self.created_by_id = created_by_id
    
    def to_dict(self, include_users=True):
        """Convert relationship to dictionary."""
        data = {
            'id': self.id,
            'patient_id': self.patient_id,
            'professional_id': self.professional_id,
            'relationship_status': self.relationship_status,
            'relationship_type': self.relationship_type,
            'can_view_documents': self.can_view_documents,
            'can_add_notes': self.can_add_notes,
            'can_request_tests': self.can_request_tests,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'notes': self.notes,
            'created_by_id': self.created_by_id
        }
        
        if include_users:
            data['patient'] = self.patient.to_dict() if self.patient else None
            data['professional'] = self.professional.to_dict() if self.professional else None
        
        return data
    
    def is_active(self):
        """Check if relationship is active."""
        return self.relationship_status == 'active'
    
    def __repr__(self):
        return f'<Relationship Patient:{self.patient_id} Professional:{self.professional_id} ({self.relationship_status})>'


class AuditLog(db.Model):
    """Audit log for HIPAA compliance and security tracking."""
    
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    resource_type = db.Column(db.String(50), nullable=False, index=True)  # 'document', 'relationship', 'user'
    resource_id = db.Column(db.String(100), nullable=True, index=True)
    details = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __init__(self, action, resource_type, user_id=None, resource_id=None, 
                 details=None, ip_address=None, user_agent=None):
        """Initialize an audit log entry."""
        self.action = action
        self.resource_type = resource_type
        self.user_id = user_id
        self.resource_id = resource_id
        self.details = details
        self.ip_address = ip_address
        self.user_agent = user_agent
    
    def to_dict(self):
        """Convert audit log to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'user': self.user.to_dict() if self.user else None
        }
    
    def __repr__(self):
        return f'<AuditLog {self.action} on {self.resource_type}:{self.resource_id}>'
