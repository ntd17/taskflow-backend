from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token
from ..models import db, User
from werkzeug.security import generate_password_hash
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    @api {post} /api/auth/register Register a new user
    @apiName RegisterUser
    @apiGroup Authentication
    @apiParam {String} username User's username
    @apiParam {String} email User's email
    @apiParam {String} password User's password
    @apiSuccess {String} message Success message
    @apiSuccess {Object} user User object
    """
    data = request.get_json()
    logger.info(f"Register request data: {data}")

    if not data or not all(k in data for k in ('username', 'email', 'password')):
        logger.warning("Missing required fields in registration")
        return jsonify({'message': 'Missing required fields'}), 400

    if User.query.filter_by(username=data['username']).first():
        logger.warning("Username already exists")
        return jsonify({'message': 'Username already exists'}), 400

    if User.query.filter_by(email=data['email']).first():
        logger.warning("Email already exists")
        return jsonify({'message': 'Email already exists'}), 400

    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()
    logger.info(f"User registered successfully: {user.username}")

    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    @api {post} /api/auth/login Login user
    @apiName LoginUser
    @apiGroup Authentication
    @apiParam {String} username User's username
    @apiParam {String} password User's password
    @apiSuccess {String} access_token JWT access token
    @apiSuccess {Object} user User object
    """
    data = request.get_json()
    logger.info(f"Login request data: {data}")

    if not data or not all(k in data for k in ('username', 'password')):
        logger.warning("Missing username or password")
        return jsonify({'message': 'Missing username or password'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        logger.warning("Invalid username or password")
        return jsonify({'message': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=user.id)
    logger.info(f"User logged in successfully: {user.username}")
    logger.info(f"Access token created: {access_token}")

    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/reset-test-user', methods=['POST'])
def reset_test_user():
    if not current_app.config.get('TESTING', False):
        return jsonify({'message': 'Endpoint not available'}), 403

    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({'message': 'Username is required'}), 400

    try:
        user_deleted = User.delete_by_username(username)
        if user_deleted:
            return jsonify({'message': 'User reset successfully'}), 200
        else:
            return jsonify({'message': 'User does not exist'}), 200
    except Exception as e:
        current_app.logger.error(f"Error while resetting user: {str(e)}")
        return jsonify({'message': 'Error resetting user'}), 500
