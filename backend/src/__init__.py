"""
Application factory module.
This module contains the application factory function.
"""
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import get_config
from .api import api_bp
from .utils.error_handlers import register_error_handlers

def create_app(test_config=None):
    """
    Create and configure the Flask application.

    Args:
        test_config: Test configuration to use instead of the default.

    Returns:
        The configured Flask application.
    """

    app = Flask(__name__)

    if test_config:
        app.config.from_mapping(test_config)
    else:
        config = get_config()
        app.config.from_object(config)

    # Configure file upload settings
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

    # Create upload folder if it doesn't exist
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

    # Create vector DB folder if using local storage
    if not config.VECTOR_DB_URL and config.VECTOR_DB_LOCAL_PATH:
        os.makedirs(config.VECTOR_DB_LOCAL_PATH, exist_ok=True)

    CORS(app)
    JWTManager(app)

    register_error_handlers(app)

    app.register_blueprint(api_bp)

    return app