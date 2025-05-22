"""
Production configuration for the application.
This module contains the production-specific configuration.
"""
import os
from .base import BaseConfig

class ProductionConfig(BaseConfig):
    """Production configuration class."""
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv("PROD_JWT_KEY")
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv("PROD_OPENAI_KEY")
