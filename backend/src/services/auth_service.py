"""
Authentication service.
This module contains the authentication service functions.

Note: In a real application, users would be stored in a database.
For this example, we're using a simple dictionary.
"""
from ..models.user import User

# Mock users database
USERS = {
    "gabriel": {"password": "gabriel123", "role": "patient"},
    "drmurilo": {"password": "drmurilo123", "role": "professional"}
}

def get_user_by_credentials(username, password):
    """
    Get a user by credentials.

    Args:
        username: The username.
        password: The password.

    Returns:
        The user if the credentials are valid, None otherwise.
    """
    user = USERS.get(username)
    if not user or user["password"] != password:
        return None

    return user
