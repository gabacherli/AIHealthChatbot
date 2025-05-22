"""
API module for the application.
This module contains all the API routes and resources.
"""
from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api")

from .auth.routes import auth_bp
from .chat.routes import chat_bp
from .health.routes import health_bp
from .documents import documents_bp

api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(chat_bp)
api_bp.register_blueprint(health_bp)
api_bp.register_blueprint(documents_bp)
