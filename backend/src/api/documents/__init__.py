"""
Documents API package.
"""
from flask import Blueprint

documents_bp = Blueprint("documents", __name__, url_prefix="/documents")

from . import routes
from .sharing_routes import sharing_bp

# Register sharing routes as a sub-blueprint
documents_bp.register_blueprint(sharing_bp)
