"""
Base configuration for the application.
This module contains the base configuration class that other environment-specific
configurations will inherit from.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from root-level .env file
# Get the path to the root directory (two levels up from this file)
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / '.env'
load_dotenv(dotenv_path=env_path)

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

    # Medical embedding models
    MEDICAL_TEXT_EMBEDDING_MODEL = os.getenv("MEDICAL_TEXT_EMBEDDING_MODEL", "emilyalsentzer/Bio_ClinicalBERT")
    MEDICAL_IMAGE_EMBEDDING_MODEL = os.getenv("MEDICAL_IMAGE_EMBEDDING_MODEL", "microsoft/BiomedVLP-CXR-BERT-specialized")

    # Vector database settings
    VECTOR_DB_URL = os.getenv("VECTOR_DB_URL", "")
    VECTOR_DB_API_KEY = os.getenv("VECTOR_DB_API_KEY", "")
    VECTOR_DB_LOCAL_PATH = os.getenv("VECTOR_DB_LOCAL_PATH", "./qdrant_data")
    VECTOR_DB_COLLECTION = os.getenv("VECTOR_DB_COLLECTION", "health_documents")
    VECTOR_SIZE = 768  # Default size for most embedding models

    # Document processing settings
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads/")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx', 'doc', 'csv', 'xlsx', 'xls',
        'dcm', 'dicom', 'ima', 'img'  # DICOM medical image formats
    }

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///health_chatbot.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Application settings
    CHUNK_DATA_PATH = "data/"

    # Medical disclaimer settings
    MEDICAL_RELEVANCE_THRESHOLD = float(os.getenv("MEDICAL_RELEVANCE_THRESHOLD", "0.8"))
    PATHOLOGICAL_CONFIDENCE_THRESHOLD = float(os.getenv("PATHOLOGICAL_CONFIDENCE_THRESHOLD", "0.6"))

    # Medical disclaimer templates - Portuguese (default)
    PATIENT_DISCLAIMER_TEMPLATE_PT = "⚠️ Nota: A confiança da análise de IA é limitada para {sources}. Revisão profissional recomendada para avaliação definitiva."
    PROFESSIONAL_DISCLAIMER_TEMPLATE_PT = "⚠️ Nota Clínica: Confiança da classificação de IA limitada para {sources}. Revisão manual aconselhada para precisão diagnóstica."

    # Medical disclaimer templates - English
    PATIENT_DISCLAIMER_TEMPLATE_EN = "⚠️ Note: AI analysis confidence is limited for {sources}. Professional review recommended for definitive assessment."
    PROFESSIONAL_DISCLAIMER_TEMPLATE_EN = "⚠️ Clinical Note: AI classification confidence limited for {sources}. Manual review advised for diagnostic accuracy."
