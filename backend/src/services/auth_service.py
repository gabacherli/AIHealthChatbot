"""
Authentication service.
This module contains the authentication service functions using SQLAlchemy models.
"""
from datetime import datetime
from ..models.database import User, db
from .audit_service import AuditService

# Keep the mock users for migration purposes
USERS = {
    "gabriel": {"password": "gabriel123", "role": "patient"},
    "drmurilo": {"password": "drmurilo123", "role": "professional"}
}

audit_service = AuditService()

def get_user_by_credentials(username, password):
    """
    Get a user by credentials using database.

    Args:
        username: The username.
        password: The password.

    Returns:
        The user dictionary if the credentials are valid, None otherwise.
    """
    try:
        # Query user from database
        user = User.query.filter_by(username=username, is_active=True).first()

        if not user or not user.check_password(password):
            # Log failed login attempt
            audit_service.log_user_action(
                user_id=user.id if user else None,
                action='login_failed',
                details={'username': username, 'reason': 'invalid_credentials'}
            )
            return None

        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Log successful login
        audit_service.log_user_action(
            user_id=user.id,
            action='login_success',
            details={'username': username}
        )

        # Return user data in the expected format
        return {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.get_full_name()
        }

    except Exception as e:
        return None

def get_user_by_id(user_id):
    """
    Get a user by ID.

    Args:
        user_id: The user ID.

    Returns:
        The user dictionary if found, None otherwise.
    """
    try:
        user = User.query.filter_by(id=user_id, is_active=True).first()
        if not user:
            return None

        return {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.get_full_name()
        }

    except Exception as e:
        return None

def get_user_by_username(username):
    """
    Get a user by username.

    Args:
        username: The username.

    Returns:
        The user dictionary if found, None otherwise.
    """
    try:
        user = User.query.filter_by(username=username, is_active=True).first()
        if not user:
            return None

        return {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.get_full_name()
        }

    except Exception as e:
        return None
