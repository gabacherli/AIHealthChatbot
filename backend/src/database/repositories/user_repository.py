"""
User repository with SQLAlchemy Core.
This module provides ORM-like patterns for user data operations.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select, and_, or_, func
from ..core.repository import BaseRepository
from ..core.tables import users
from ...constants.education_levels import validate_education_level

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository):
    """
    User repository providing ORM-like patterns for user operations.
    Extends BaseRepository with user-specific methods.
    """

    def __init__(self):
        """Initialize the user repository."""
        super().__init__(users)

    def create_user(self, username: str, password: str, role: str, level_of_education: str,
                   email: Optional[str] = None, first_name: Optional[str] = None,
                   last_name: Optional[str] = None, **kwargs) -> Optional[int]:
        """
        Create a new user with password hashing.

        Args:
            username: Unique username
            password: Plain text password (will be hashed)
            role: User role ('patient' or 'professional')
            level_of_education: Required education level (must be one of: 'elementary_school', 'middle_school', 'high_school', 'associate_degree', 'bachelor_degree', 'master_degree', 'doctoral_degree', 'professional_degree', 'other')
            email: Optional email address
            first_name: Optional first name
            last_name: Optional last name
            **kwargs: Additional fields for professionals

        Returns:
            User ID if successful, None otherwise

        Raises:
            ValueError: If username/email already exists or invalid data
        """
        # Validate required fields
        if not username or not password or not role or not level_of_education:
            raise ValueError("Username, password, role, and level_of_education are required")

        if role not in ['patient', 'professional']:
            raise ValueError("Role must be 'patient' or 'professional'")

        # Validate education level
        if not validate_education_level(level_of_education):
            raise ValueError(f"Invalid education level '{level_of_education}'. Must be one of: {', '.join(['elementary_school', 'middle_school', 'high_school', 'associate_degree', 'bachelor_degree', 'master_degree', 'doctoral_degree', 'professional_degree', 'other'])}")

        # Check if username already exists
        if self.find_by_username(username):
            raise ValueError(f"Username '{username}' already exists")

        # Check if email already exists (if provided)
        if email and self.find_by_email(email):
            raise ValueError(f"Email '{email}' already exists")

        # Prepare user data
        user_data = {
            'username': username,
            'password_hash': generate_password_hash(password),
            'role': role,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'level_of_education': level_of_education,
            'is_active': True
        }

        # Add professional-specific fields
        if role == 'professional':
            user_data.update({
                'specialty': kwargs.get('specialty'),
                'license_number': kwargs.get('license_number'),
                'organization': kwargs.get('organization')
            })

        return self.create(user_data)

    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Find a user by username.

        Args:
            username: Username to search for

        Returns:
            User dictionary or None if not found
        """
        return self.find_one(username=username)

    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by username (alias for find_by_username).

        Args:
            username: Username to search for

        Returns:
            User dictionary or None if not found
        """
        return self.find_by_username(username)

    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a user by ID.

        Args:
            user_id: User ID to search for

        Returns:
            User dictionary or None if not found
        """
        return self.find_by_id(user_id)

    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find a user by email.

        Args:
            email: Email to search for

        Returns:
            User dictionary or None if not found
        """
        return self.find_one(email=email)

    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with username and password.

        Args:
            username: Username
            password: Plain text password

        Returns:
            User dictionary if authentication successful, None otherwise
        """
        user = self.find_by_username(username)

        if user and user.get('is_active', False):
            if check_password_hash(user['password_hash'], password):
                # Update last login timestamp
                self.update_last_login(user['id'])
                return user

        return None

    def update_last_login(self, user_id: int, login_time: Optional[datetime] = None) -> bool:
        """
        Update the last login timestamp for a user.

        Args:
            user_id: User ID
            login_time: Optional login time (defaults to current time)

        Returns:
            True if successful, False otherwise
        """
        if login_time is None:
            login_time = datetime.now()
        return self.update_by_id(user_id, {'last_login': login_time})

    def change_password(self, user_id: int, new_password: str) -> bool:
        """
        Change a user's password.

        Args:
            user_id: User ID
            new_password: New plain text password

        Returns:
            True if successful, False otherwise
        """
        password_hash = generate_password_hash(new_password)
        return self.update_by_id(user_id, {'password_hash': password_hash})

    def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate a user account.

        Args:
            user_id: User ID

        Returns:
            True if successful, False otherwise
        """
        return self.update_by_id(user_id, {'is_active': False})

    def activate_user(self, user_id: int) -> bool:
        """
        Activate a user account.

        Args:
            user_id: User ID

        Returns:
            True if successful, False otherwise
        """
        return self.update_by_id(user_id, {'is_active': True})

    def find_professionals(self, specialty: Optional[str] = None,
                          organization: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find healthcare professionals with optional filtering.

        Args:
            specialty: Optional specialty filter
            organization: Optional organization filter

        Returns:
            List of professional user dictionaries
        """
        criteria = {'role': 'professional', 'is_active': True}

        if specialty:
            criteria['specialty'] = specialty

        if organization:
            criteria['organization'] = organization

        return self.find_many(order_by='last_name', **criteria)

    def find_patients(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Find patient users.

        Args:
            limit: Optional limit on number of results

        Returns:
            List of patient user dictionaries
        """
        return self.find_many(
            role='patient',
            is_active=True,
            limit=limit,
            order_by='last_name'
        )

    def search_users(self, search_term: str, role: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search users by name, username, or email.

        Args:
            search_term: Search term
            role: Optional role filter

        Returns:
            List of matching user dictionaries
        """
        try:
            # Build search query
            search_pattern = f"%{search_term}%"

            stmt = select(self.table).where(
                and_(
                    self.table.c.is_active == True,
                    or_(
                        self.table.c.username.ilike(search_pattern),
                        self.table.c.first_name.ilike(search_pattern),
                        self.table.c.last_name.ilike(search_pattern),
                        self.table.c.email.ilike(search_pattern)
                    )
                )
            )

            if role:
                stmt = stmt.where(self.table.c.role == role)

            stmt = stmt.order_by(self.table.c.last_name, self.table.c.first_name)

            with self.engine.connection() as conn:
                result = conn.execute(stmt)
                return [self._row_to_dict(row) for row in result.fetchall()]

        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return []

    def get_user_stats(self) -> Dict[str, Any]:
        """
        Get user statistics.

        Returns:
            Dictionary with user statistics
        """
        try:
            with self.engine.connection() as conn:
                # Total users
                total_stmt = select(func.count()).select_from(self.table)
                total_users = conn.execute(total_stmt).scalar()

                # Active users
                active_stmt = select(func.count()).select_from(self.table).where(
                    self.table.c.is_active == True
                )
                active_users = conn.execute(active_stmt).scalar()

                # Users by role
                role_stmt = select(
                    self.table.c.role,
                    func.count().label('count')
                ).group_by(self.table.c.role)

                role_counts = {}
                for row in conn.execute(role_stmt):
                    role_counts[row.role] = row.count

                return {
                    'total_users': total_users,
                    'active_users': active_users,
                    'inactive_users': total_users - active_users,
                    'role_counts': role_counts
                }

        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}

# Global user repository instance
user_repository = UserRepository()

__all__ = ['UserRepository', 'user_repository']
