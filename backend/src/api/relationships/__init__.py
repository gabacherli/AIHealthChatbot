"""
Relationships API module.
This module contains the API routes for patient-professional relationship management.
"""
from flask import Blueprint

relationships_bp = Blueprint("relationships", __name__, url_prefix="/relationships")

from .routes import *
