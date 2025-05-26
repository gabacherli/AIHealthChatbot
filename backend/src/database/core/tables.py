"""
SQLAlchemy Core table definitions for the Health Chatbot application.
This module contains the explicit table definitions using SQLAlchemy Core.
"""

from sqlalchemy import (
    Table, Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, Index, UniqueConstraint, CheckConstraint, MetaData, Enum
)
from sqlalchemy.sql import func
from datetime import datetime

# Create metadata instance
metadata = MetaData()

# Users table definition
users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(80), nullable=False, unique=True),
    Column('email', String(120), unique=True, nullable=True),
    Column('password_hash', String(255), nullable=False),
    Column('role', String(20), nullable=False),
    Column('first_name', String(50), nullable=True),
    Column('last_name', String(50), nullable=True),
    Column('level_of_education', Enum(
        'elementary_school',
        'middle_school',
        'high_school',
        'associate_degree',
        'bachelor_degree',
        'master_degree',
        'doctoral_degree',
        'professional_degree',  # MD, JD, PharmD, etc.
        'other',
        name='education_level_enum'
    ), nullable=False),

    # Professional-specific fields
    Column('specialty', String(100), nullable=True),
    Column('license_number', String(50), nullable=True),
    Column('organization', String(200), nullable=True),

    # Timestamps
    Column('created_at', DateTime, nullable=False, default=func.now()),
    Column('updated_at', DateTime, nullable=False, default=func.now(), onupdate=func.now()),
    Column('last_login', DateTime, nullable=True),

    # Status
    Column('is_active', Boolean, nullable=False, default=True),

    # Indexes
    Index('idx_users_username', 'username'),
    Index('idx_users_email', 'email'),
    Index('idx_users_role', 'role'),
    Index('idx_users_level_of_education', 'level_of_education'),
    Index('idx_users_created_at', 'created_at'),

    # Constraints
    CheckConstraint("role IN ('patient', 'professional')", name='chk_users_role'),
)

# Patient-Professional Relationships table definition
patient_professional_relationships = Table(
    'patient_professional_relationships',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('patient_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('professional_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('relationship_type', String(50), nullable=False, default='primary'),
    Column('status', String(20), nullable=False, default='active'),

    # Permissions
    Column('can_view_documents', Boolean, nullable=False, default=True),
    Column('can_add_notes', Boolean, nullable=False, default=True),
    Column('can_request_tests', Boolean, nullable=False, default=False),

    # Timestamps
    Column('created_at', DateTime, nullable=False, default=func.now()),
    Column('updated_at', DateTime, nullable=False, default=func.now(), onupdate=func.now()),

    # Metadata
    Column('notes', Text, nullable=True),
    Column('created_by_id', Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True),

    # Indexes
    Index('idx_relationships_patient_id', 'patient_id'),
    Index('idx_relationships_professional_id', 'professional_id'),
    Index('idx_relationships_type', 'relationship_type'),
    Index('idx_relationships_status', 'status'),
    Index('idx_relationships_created_at', 'created_at'),

    # Constraints
    UniqueConstraint('patient_id', 'professional_id', name='unique_patient_professional'),
    CheckConstraint('patient_id != professional_id', name='different_users'),
    CheckConstraint("relationship_type IN ('primary_care', 'nurse', 'specialist', 'other')",
                   name='chk_relationship_type'),
    CheckConstraint("status IN ('active', 'inactive', 'pending', 'terminated')",
                   name='chk_relationship_status'),
)

# Audit Logs table definition
audit_logs = Table(
    'audit_logs',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
    Column('action', String(100), nullable=False),
    Column('resource_type', String(50), nullable=False),
    Column('resource_id', String(100), nullable=True),
    Column('details', Text, nullable=True),  # JSON stored as text
    Column('ip_address', String(45), nullable=True),
    Column('user_agent', String(500), nullable=True),
    Column('timestamp', DateTime, nullable=False, default=func.now()),

    # Indexes
    Index('idx_audit_user_id', 'user_id'),
    Index('idx_audit_action', 'action'),
    Index('idx_audit_resource_type', 'resource_type'),
    Index('idx_audit_resource_id', 'resource_id'),
    Index('idx_audit_timestamp', 'timestamp'),

    # Constraints
    CheckConstraint("resource_type IN ('document', 'relationship', 'user', 'chat', 'upload')",
                   name='chk_audit_resource_type'),
)

# Export all tables for easy access
__all__ = ['metadata', 'users', 'patient_professional_relationships', 'audit_logs']
