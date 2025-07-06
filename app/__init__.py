from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from flasgger import Swagger
import logging
from .models import db
from .routes import api_bp

def create_app(config_name='default'):
    """
    Application factory function that creates and configures the Flask app
    """
    app = Flask(__name__)

    # Set logging level
    app.logger.setLevel(logging.INFO)

    # Load config
    from config import config
    app.config.from_object(config[config_name])
    app.logger.info(f"Using config: {config_name}")

    # Initialize extensions
    db.init_app(app)
    
    # Log JWT configuration
    app.logger.info(f"JWT_SECRET_KEY: {app.config.get('JWT_SECRET_KEY')}")
    app.logger.info(f"JWT_ACCESS_TOKEN_EXPIRES: {app.config.get('JWT_ACCESS_TOKEN_EXPIRES')}")
    app.logger.info(f"TESTING: {app.config.get('TESTING')}")
    
    jwt = JWTManager(app)

    # Set JWT algorithm explicitly
    app.config['JWT_ALGORITHM'] = app.config.get('JWT_ALGORITHM', 'HS256')

    migrate = Migrate(app, db)
    CORS(app)
    
    # Configure Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/"
    }
    
    swagger = Swagger(app, config=swagger_config)

    # Register blueprints
    app.register_blueprint(api_bp)

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'message': 'The token has expired',
            'error': 'token_expired'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'message': 'Signature verification failed',
            'error': 'invalid_token'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'message': 'Request does not contain an access token',
            'error': 'authorization_required'
        }), 401

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
