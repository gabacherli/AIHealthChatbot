"""
Main application entry point.
This module creates and runs the Flask application.
"""
import os
from src import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.environ.get("FLASK_ENV") != "production"
    )
