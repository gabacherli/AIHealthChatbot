"""
Development configuration for the application.
This module contains the development-specific configuration.
"""
import os
from .base import BaseConfig

class DevelopmentConfig(BaseConfig):
    """Development configuration class."""
    
    # Flask settings
    DEBUG = True
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv("DEV_JWT_KEY", "dev-jwt-key")
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv("DEV_OPENAI_KEY")
