"""
Authentication service.
This module contains the authentication service functions using SQLAlchemy Core.
"""
from datetime import datetime
from werkzeug.security import check_password_hash
from ..database.repositories.user_repository import UserRepository
from .audit_service import audit_service

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
        user_repo = UserRepository()
        user = user_repo.get_by_username(username)

        if not user or not check_password_hash(user.get('password_hash', ''), password):
            # Log failed login attempt
            audit_service.log_user_action(
                user_id=user.get('id') if user else None,
                action='login_failed',
                details={'username': username, 'reason': 'invalid_credentials'}
            )
            return None

        # Update last login time
        user_repo.update_last_login(user['id'], datetime.now())

        # Log successful login
        audit_service.log_user_action(
            user_id=user['id'],
            action='login_success',
            details={'username': username}
        )

        # Return user data in the expected format
        return {
            "id": user['id'],
            "username": user['username'],
            "role": user['role'],
            "email": user.get('email'),
            "first_name": user.get('first_name'),
            "last_name": user.get('last_name'),
            "full_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
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
        user_repo = UserRepository()
        user = user_repo.get_by_id(user_id)
        if not user:
            return None

        return {
            "id": user['id'],
            "username": user['username'],
            "role": user['role'],
            "email": user.get('email'),
            "first_name": user.get('first_name'),
            "last_name": user.get('last_name'),
            "full_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
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
        user_repo = UserRepository()
        user = user_repo.get_by_username(username)
        if not user:
            return None

        return {
            "id": user['id'],
            "username": user['username'],
            "role": user['role'],
            "email": user.get('email'),
            "first_name": user.get('first_name'),
            "last_name": user.get('last_name'),
            "full_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        }

    except Exception as e:
        return None
