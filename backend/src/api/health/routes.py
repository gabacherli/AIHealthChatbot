"""
Health check routes.
This module contains the routes for health checking.
"""
from flask import Blueprint, jsonify
import os

health_bp = Blueprint("health", __name__, url_prefix="/health")

@health_bp.route("", methods=["GET"])
def health_check():
    """
    Health check route.
    
    Returns:
        A JSON response indicating the service health status.
    """
    try:
        # Basic health check - can be extended with database checks, etc.
        return jsonify({
            "status": "healthy",
            "service": "health-chatbot-backend",
            "version": "1.0.0",
            "environment": os.getenv("FLASK_ENV", "development")
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500
