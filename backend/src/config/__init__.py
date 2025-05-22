"""
Configuration module for the application.
This module handles loading the appropriate configuration based on the environment.
"""
import os
from .development import DevelopmentConfig
from .production import ProductionConfig

def get_config():
    """
    Get the configuration based on the environment.

    Returns:
        The configuration class for the current environment.
    """
    env = os.getenv("FLASK_ENV", "development")

    if env == "production":
        return ProductionConfig()
    else:
        return DevelopmentConfig()