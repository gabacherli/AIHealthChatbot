"""
Base configuration for the application.
This module contains the base configuration class that other environment-specific
configurations will inherit from.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class BaseConfig:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-please-change")
    DEBUG = False
    TESTING = False
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-key-please-change")
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = "gpt-4o-mini"
    EMBEDDING_MODEL = "multi-qa-MiniLM-L6-cos-v1"
    
    # Application settings
    CHUNK_DATA_PATH = "data/"
