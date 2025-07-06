from flask import Blueprint
from .auth import auth_bp
from .boards import boards_bp
from .lists import lists_bp
from .cards import cards_bp

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Register route blueprints
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(boards_bp, url_prefix='/boards')
api_bp.register_blueprint(lists_bp)  # Lists routes are nested under boards
api_bp.register_blueprint(cards_bp)  # Cards routes are nested under lists
