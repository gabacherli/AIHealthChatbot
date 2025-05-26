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


def run_alembic_migrations(app):
    """
    Run Alembic migrations automatically on application startup.

    Args:
        app: Flask application instance for logging
    """
    try:
        from alembic.config import Config
        from alembic import command

        app.logger.info("Running Alembic migrations...")

        # Get the directory containing this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(current_dir)
        alembic_ini_path = os.path.join(backend_dir, 'alembic.ini')

        if not os.path.exists(alembic_ini_path):
            app.logger.warning(f"Alembic config file not found at {alembic_ini_path}")
            return

        # Create Alembic config
        alembic_cfg = Config(alembic_ini_path)

        # Set the script location relative to the backend directory
        alembic_cfg.set_main_option('script_location', os.path.join(backend_dir, 'alembic'))

        # Run migrations to head
        command.upgrade(alembic_cfg, 'head')

        app.logger.info("Alembic migrations completed")

    except ImportError:
        app.logger.warning("Alembic not installed, skipping migrations")
    except Exception as e:
        app.logger.error(f"Failed to run Alembic migrations: {e}")
        # Don't raise the exception to prevent app startup failure
        # In production, you might want to raise this to ensure migrations succeed


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

    # Configure CORS with explicit settings for development and Docker
    CORS(app,
         origins=[
             "http://localhost:3000",      # React dev server (local)
             "http://127.0.0.1:3000",      # Alternative localhost
             "http://frontend:3000",       # Docker container name
             "http://0.0.0.0:3000",        # Docker host binding
             "file://"                     # For local HTML files
         ],
         allow_headers=[
             "Content-Type",
             "Authorization",
             "X-Requested-With",
             "Accept",
             "Origin",
             "Access-Control-Request-Method",
             "Access-Control-Request-Headers"
         ],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
         supports_credentials=False,  # Set to False to avoid credential issues
         expose_headers=["Content-Range", "X-Content-Range"],
         max_age=86400,  # Cache preflight requests for 24 hours
         send_wildcard=False,
         automatic_options=True  # Automatically handle OPTIONS requests
    )

    # Initialize SQLAlchemy Core database system
    try:
        from .database.core.engine import db_engine
        db_engine.create_tables()
        app.logger.info("SQLAlchemy Core database system initialized")
    except Exception as e:
        app.logger.error(f"Error initializing SQLAlchemy Core: {e}")

    # Run Alembic migrations automatically
    try:
        run_alembic_migrations(app)
        app.logger.info("Alembic migrations completed successfully")
    except Exception as e:
        app.logger.error(f"Error running Alembic migrations: {e}")

    app.logger.info("Using database system: SQLAlchemy Core")

    JWTManager(app)

    register_error_handlers(app)

    app.register_blueprint(api_bp)

    return app