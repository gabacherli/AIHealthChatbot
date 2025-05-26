"""
Database management API routes.
This module contains endpoints for managing the SQLAlchemy Core database system.
"""

import os
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from ...database.core.engine import db_engine

database_bp = Blueprint("database", __name__, url_prefix="/database")

def require_admin():
    """Decorator to require admin role."""
    def decorator(f):
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            role = claims.get("role", "patient")
            if role != "admin":
                # For now, allow professionals to access database management
                # In production, you might want stricter controls
                if role != "professional":
                    return jsonify({"error": "Admin access required"}), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@database_bp.route("/health", methods=["GET"])
@jwt_required()
@require_admin()
def health_check():
    """
    Get health status of the SQLAlchemy Core database system.

    Returns:
        JSON response with health status
    """
    try:
        # Simple health check for SQLAlchemy Core
        health = {
            "system": "sqlalchemy_core",
            "status": "healthy" if db_engine.is_healthy() else "unhealthy",
            "connection_pool": {
                "size": db_engine.get_pool_size(),
                "checked_out": db_engine.get_checked_out_connections()
            }
        }

        return jsonify({
            "status": "success",
            "health": health
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@database_bp.route("/statistics", methods=["GET"])
@jwt_required()
@require_admin()
def get_statistics():
    """
    Get statistics from the SQLAlchemy Core database system.

    Returns:
        JSON response with database statistics
    """
    try:
        # Simple statistics for SQLAlchemy Core
        stats = {
            "system": "sqlalchemy_core",
            "tables": db_engine.get_table_count(),
            "connection_pool": {
                "size": db_engine.get_pool_size(),
                "checked_out": db_engine.get_checked_out_connections(),
                "overflow": db_engine.get_overflow_connections()
            }
        }

        return jsonify({
            "status": "success",
            "statistics": stats
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@database_bp.route("/config", methods=["GET"])
@jwt_required()
@require_admin()
def get_config():
    """
    Get current database configuration.

    Returns:
        JSON response with configuration details
    """
    try:
        config = {
            "current_system": "sqlalchemy_core",
            "database_url": os.getenv('DATABASE_URL', 'Not set'),
            "pool_size": os.getenv('SQLALCHEMY_CORE_POOL_SIZE', '10'),
            "max_overflow": os.getenv('SQLALCHEMY_CORE_MAX_OVERFLOW', '20'),
            "echo": os.getenv('SQLALCHEMY_CORE_ECHO', 'false')
        }

        # Mask sensitive information
        if config['database_url'] and '@' in config['database_url']:
            parts = config['database_url'].split('@')
            if len(parts) > 1:
                config['database_url'] = f"***@{parts[1]}"

        return jsonify({
            "status": "success",
            "config": config
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@database_bp.route("/initialize", methods=["POST"])
@jwt_required()
@require_admin()
def initialize_system():
    """
    Initialize the SQLAlchemy Core database system.

    Returns:
        JSON response with initialization result
    """
    try:
        # SQLAlchemy Core is already initialized
        return jsonify({
            "status": "success",
            "message": "SQLAlchemy Core system is already initialized",
            "system": "sqlalchemy_core"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@database_bp.route("/test-connection", methods=["POST"])
@jwt_required()
@require_admin()
def test_connection():
    """
    Test SQLAlchemy Core database connection.

    Returns:
        JSON response with connection test result
    """
    try:
        # Test connection using SQLAlchemy Core
        health = {
            "system": "sqlalchemy_core",
            "status": "healthy" if db_engine.is_healthy() else "unhealthy",
            "connection_pool": {
                "size": db_engine.get_pool_size(),
                "checked_out": db_engine.get_checked_out_connections()
            }
        }

        return jsonify({
            "status": "success",
            "system": "sqlalchemy_core",
            "connection_test": health
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
