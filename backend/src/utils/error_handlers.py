"""
Error handlers utility.
This module contains functions for handling errors.
"""
from flask import jsonify

def register_error_handlers(app):
    """
    Register error handlers for the application.
    
    Args:
        app: The Flask application.
    """
    @app.errorhandler(400)
    def bad_request(error):
        """
        Handle 400 Bad Request errors.
        
        Args:
            error: The error.
            
        Returns:
            A JSON response with the error message.
        """
        return jsonify({
            "error": "Bad Request",
            "message": str(error)
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """
        Handle 401 Unauthorized errors.
        
        Args:
            error: The error.
            
        Returns:
            A JSON response with the error message.
        """
        return jsonify({
            "error": "Unauthorized",
            "message": "Authentication is required to access this resource."
        }), 401
    
    @app.errorhandler(404)
    def not_found(error):
        """
        Handle 404 Not Found errors.
        
        Args:
            error: The error.
            
        Returns:
            A JSON response with the error message.
        """
        return jsonify({
            "error": "Not Found",
            "message": "The requested resource was not found."
        }), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """
        Handle 500 Internal Server Error errors.
        
        Args:
            error: The error.
            
        Returns:
            A JSON response with the error message.
        """
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred."
        }), 500
