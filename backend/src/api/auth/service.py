"""
Authentication service.
This module contains the service functions for authentication.
"""
# This will be moved to a database in a near future
from ...services.auth_service import USERS

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
