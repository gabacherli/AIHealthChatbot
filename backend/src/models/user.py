"""
User model.
This module contains the user model for the application.

Note: In a real application, this would be a database model.
For this example, we're using a simple dictionary.
"""

class User:
    """User model."""
    
    def __init__(self, username, password, role):
        """
        Initialize a user.
        
        Args:
            username: The username.
            password: The password.
            role: The role.
        """
        self.username = username
        self.password = password  # TODO: Hash this
        self.role = role
    
    def to_dict(self):
        """
        Convert the user to a dictionary.
        
        Returns:
            A dictionary representation of the user.
        """
        return {
            "username": self.username,
            "password": self.password,
            "role": self.role
        }
