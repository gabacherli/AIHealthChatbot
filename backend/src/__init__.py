from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config.config import Config
from .routes.chat_routes import chat_bp

def create_app():
    app = Flask(__name__)
    config = Config()
    app.env = config.ENV
    app.config.from_object(Config)
    app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
    CORS(app)
    JWTManager(app)

    # Register route blueprints
    app.register_blueprint(chat_bp, url_prefix="/api")

    return app