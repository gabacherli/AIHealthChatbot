"""
Database initialization utilities.
This module contains functions for initializing the database and migrating existing data.
"""
import os
from datetime import datetime
from ..models.database import db, User, PatientProfessionalRelationship, AuditLog
from ..services.auth_service import USERS


def init_database(app):
    """
    Initialize the database with tables and migrate existing users.

    Args:
        app: Flask application instance
    """
    with app.app_context():
        # Create all tables
        db.create_all()

        # Migrate existing users from dictionary to database
        migrate_existing_users()

        # Create sample relationships for testing
        create_sample_relationships()




def migrate_existing_users():
    """Migrate existing users from dictionary storage to database."""
    for username, user_data in USERS.items():
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            continue

        # Create new user
        user = User(
            username=username,
            password=user_data['password'],  # Will be hashed in User.__init__
            role=user_data['role']
        )

        # Add professional-specific data for sample users
        if user.role == 'professional':
            if username == 'drmurilo':
                user.first_name = 'Dr. Murilo'
                user.last_name = 'Santos'
                user.email = 'drmurilo@healthchatbot.com'
                user.specialty = 'Internal Medicine'
                user.license_number = 'MD123456'
                user.organization = 'Health Chatbot Medical Center'
        else:  # patient
            if username == 'gabriel':
                user.first_name = 'Gabriel'
                user.last_name = 'Silva'
                user.email = 'gabriel@example.com'

        db.session.add(user)

    db.session.commit()


def create_sample_relationships():
    """Create sample patient-professional relationships for testing."""
    print("Creating sample relationships...")

    # Get users
    gabriel = User.query.filter_by(username='gabriel').first()
    dr_murilo = User.query.filter_by(username='drmurilo').first()

    if gabriel and dr_murilo:
        # Check if relationship already exists
        existing_rel = PatientProfessionalRelationship.query.filter_by(
            patient_id=gabriel.id,
            professional_id=dr_murilo.id
        ).first()

        if not existing_rel:
            # Create relationship
            relationship = PatientProfessionalRelationship(
                patient_id=gabriel.id,
                professional_id=dr_murilo.id,
                relationship_type='primary_care',
                relationship_status='active',
                created_by_id=dr_murilo.id
            )
            relationship.notes = 'Sample patient-doctor relationship for testing'

            db.session.add(relationship)
            db.session.commit()

            # Log the relationship creation
            audit_log = AuditLog(
                action='relationship_created',
                resource_type='relationship',
                resource_id=str(relationship.id),
                user_id=dr_murilo.id,
                details={
                    'patient_id': gabriel.id,
                    'professional_id': dr_murilo.id,
                    'relationship_type': 'primary_care'
                }
            )
            db.session.add(audit_log)
            db.session.commit()




def create_additional_sample_users():
    """Create additional sample users for testing."""
    sample_users = [
        {
            'username': 'patient_jane',
            'password': 'jane123',
            'role': 'patient',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@example.com'
        },
        {
            'username': 'patient_john',
            'password': 'john123',
            'role': 'patient',
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'john.smith@example.com'
        },
        {
            'username': 'dr_sarah',
            'password': 'sarah123',
            'role': 'professional',
            'first_name': 'Dr. Sarah',
            'last_name': 'Johnson',
            'email': 'dr.sarah@healthchatbot.com',
            'specialty': 'Cardiology',
            'license_number': 'MD789012',
            'organization': 'Heart Care Medical Center'
        },
        {
            'username': 'dr_mike',
            'password': 'mike123',
            'role': 'professional',
            'first_name': 'Dr. Michael',
            'last_name': 'Brown',
            'email': 'dr.mike@healthchatbot.com',
            'specialty': 'Dermatology',
            'license_number': 'MD345678',
            'organization': 'Skin Health Clinic'
        }
    ]

    for user_data in sample_users:
        # Check if user already exists
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if existing_user:
            continue

        # Create new user
        user = User(
            username=user_data['username'],
            password=user_data['password'],
            role=user_data['role'],
            email=user_data.get('email'),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name')
        )

        # Add professional-specific fields
        if user.role == 'professional':
            user.specialty = user_data.get('specialty')
            user.license_number = user_data.get('license_number')
            user.organization = user_data.get('organization')

        db.session.add(user)

    db.session.commit()


def create_sample_relationships_extended():
    """Create additional sample relationships."""
    # Get users
    jane = User.query.filter_by(username='patient_jane').first()
    john = User.query.filter_by(username='patient_john').first()
    dr_sarah = User.query.filter_by(username='dr_sarah').first()
    dr_mike = User.query.filter_by(username='dr_mike').first()
    dr_murilo = User.query.filter_by(username='drmurilo').first()

    relationships_to_create = []

    if jane and dr_sarah:
        relationships_to_create.append({
            'patient': jane,
            'professional': dr_sarah,
            'type': 'specialist',
            'notes': 'Cardiology consultation for heart palpitations'
        })

    if jane and dr_murilo:
        relationships_to_create.append({
            'patient': jane,
            'professional': dr_murilo,
            'type': 'primary_care',
            'notes': 'Primary care physician'
        })

    if john and dr_mike:
        relationships_to_create.append({
            'patient': john,
            'professional': dr_mike,
            'type': 'specialist',
            'notes': 'Dermatology consultation for skin condition'
        })

    for rel_data in relationships_to_create:
        # Check if relationship already exists
        existing_rel = PatientProfessionalRelationship.query.filter_by(
            patient_id=rel_data['patient'].id,
            professional_id=rel_data['professional'].id
        ).first()

        if not existing_rel:
            relationship = PatientProfessionalRelationship(
                patient_id=rel_data['patient'].id,
                professional_id=rel_data['professional'].id,
                relationship_type=rel_data['type'],
                relationship_status='active',
                created_by_id=rel_data['professional'].id
            )
            relationship.notes = rel_data['notes']

            db.session.add(relationship)

    db.session.commit()


def reset_database(app):
    """
    Reset the database by dropping and recreating all tables.
    WARNING: This will delete all data!

    Args:
        app: Flask application instance
    """
    with app.app_context():
        db.drop_all()
        db.create_all()
        migrate_existing_users()
        create_additional_sample_users()
        create_sample_relationships()
        create_sample_relationships_extended()


def get_database_stats(app):
    """
    Get database statistics.

    Args:
        app: Flask application instance

    Returns:
        dict: Database statistics
    """
    with app.app_context():
        stats = {
            'users': {
                'total': User.query.count(),
                'patients': User.query.filter_by(role='patient').count(),
                'professionals': User.query.filter_by(role='professional').count(),
                'active': User.query.filter_by(is_active=True).count()
            },
            'relationships': {
                'total': PatientProfessionalRelationship.query.count(),
                'active': PatientProfessionalRelationship.query.filter_by(relationship_status='active').count(),
                'pending': PatientProfessionalRelationship.query.filter_by(relationship_status='pending').count(),
                'inactive': PatientProfessionalRelationship.query.filter_by(relationship_status='inactive').count()
            },
            'audit_logs': {
                'total': AuditLog.query.count(),
                'last_24h': AuditLog.query.filter(
                    AuditLog.timestamp >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                ).count()
            }
        }
        return stats
