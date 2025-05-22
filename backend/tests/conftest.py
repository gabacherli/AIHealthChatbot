"""
Test configuration.
This module contains fixtures for tests.
"""
import pytest
from src import create_app

@pytest.fixture
def app():
    """
    Create a Flask application for testing.
    
    Returns:
        A Flask application configured for testing.
    """
    app = create_app({
        "TESTING": True,
        "JWT_SECRET_KEY": "test-key",
    })
    
    yield app

@pytest.fixture
def client(app):
    """
    Create a test client for the application.
    
    Args:
        app: The Flask application.
        
    Returns:
        A test client for the application.
    """
    return app.test_client()
