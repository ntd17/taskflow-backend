from flask import current_app, Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, get_jwt
from ..models import db, Board, User, UserBoard

boards_bp = Blueprint('boards', __name__)

def check_token_revoked():
    verify_jwt_in_request()
    jti = get_jwt()['jti']
    current_app.logger.info(f"Checking token revocation for jti: {jti}")
    # Here you can implement token revocation check if needed
    # For now, just log and return False
    return False

@boards_bp.route('', methods=['POST'])
@jwt_required()
def create_board():
    """
    @api {post} /api/boards Create a new board
    @apiName CreateBoard
    @apiGroup Boards
    @apiHeader {String} Authorization Bearer <access_token>
    @apiParam {String} title Board title
    @apiSuccess {Object} board Created board object
    """
    # Log the token from the request
    auth_header = request.headers.get('Authorization')
    current_app.logger.info(f"Authorization header: {auth_header}")

    if check_token_revoked():
        return jsonify({'message': 'Token has been revoked'}), 401

    current_user_id = int(get_jwt_identity())
    current_app.logger.info(f"Current user ID from token: {current_user_id}")
    data = request.get_json()

    if not data or 'title' not in data:
        return jsonify({'message': 'Title is required'}), 400

    board = Board(title=data['title'])
    user = User.query.get(current_user_id)
    board.members.append(user)

    db.session.add(board)
    db.session.commit()

    return jsonify(board.to_dict()), 201

@boards_bp.route('', methods=['GET'])
@jwt_required()
def get_user_boards():
    """
    @api {get} /api/boards Get user's boards
    @apiName GetUserBoards
    @apiGroup Boards
    @apiHeader {String} Authorization Bearer <access_token>
    @apiSuccess {Array} boards List of board objects
    """
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    return jsonify([board.to_dict() for board in user.boards]), 200

@boards_bp.route('/<int:board_id>', methods=['GET'])
@jwt_required()
def get_board(board_id):
    """
    @api {get} /api/boards/:id Get board details
    @apiName GetBoard
    @apiGroup Boards
    @apiHeader {String} Authorization Bearer <access_token>
    @apiParam {Number} id Board ID
    @apiSuccess {Object} board Board object
    """
    current_user_id = int(get_jwt_identity())
    board = Board.query.get_or_404(board_id)

    if not any(member.id == current_user_id for member in board.members):
        return jsonify({'message': 'Access denied'}), 403

    return jsonify(board.to_dict()), 200

@boards_bp.route('/<int:board_id>', methods=['PUT'])
@jwt_required()
def update_board(board_id):
    """
    @api {put} /api/boards/:id Update board
    @apiName UpdateBoard
    @apiGroup Boards
    @apiHeader {String} Authorization Bearer <access_token>
    @apiParam {Number} id Board ID
    @apiParam {String} title New board title
    @apiSuccess {Object} board Updated board object
    """
    current_user_id = int(get_jwt_identity())
    board = Board.query.get_or_404(board_id)

    if not any(member.id == current_user_id for member in board.members):
        return jsonify({'message': 'Access denied'}), 403

    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'message': 'Title is required'}), 400

    board.title = data['title']
    db.session.commit()

    return jsonify(board.to_dict()), 200

@boards_bp.route('/<int:board_id>', methods=['DELETE'])
@jwt_required()
def delete_board(board_id):
    """
    @api {delete} /api/boards/:id Delete board
    @apiName DeleteBoard
    @apiGroup Boards
    @apiHeader {String} Authorization Bearer <access_token>
    @apiParam {Number} id Board ID
    @apiSuccess {String} message Success message
    """
    current_user_id = int(get_jwt_identity())
    board = Board.query.get_or_404(board_id)

    if not any(member.id == current_user_id for member in board.members):
        return jsonify({'message': 'Access denied'}), 403

    db.session.delete(board)
    db.session.commit()

    return jsonify({'message': 'Board deleted successfully'}), 200

@boards_bp.route('/<int:board_id>/members', methods=['POST'])
@jwt_required()
def add_member(board_id):
    """
    @api {post} /api/boards/:id/members Add member to board
    @apiName AddBoardMember
    @apiGroup Boards
    @apiHeader {String} Authorization Bearer <access_token>
    @apiParam {Number} id Board ID
    @apiParam {String} email User email to add
    @apiSuccess {Object} board Updated board object
    """
    current_user_id = int(get_jwt_identity())
    board = Board.query.get_or_404(board_id)

    if not any(member.id == current_user_id for member in board.members):
        return jsonify({'message': 'Access denied'}), 403

    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({'message': 'Email is required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if user in board.members:
        return jsonify({'message': 'User is already a member'}), 400

    board.members.append(user)
    db.session.commit()

    return jsonify(board.to_dict()), 200

@boards_bp.route('/<int:board_id>/members/<int:user_id>', methods=['DELETE'])
@jwt_required()
def remove_member(board_id, user_id):
    """
    @api {delete} /api/boards/:id/members/:user_id Remove member from board
    @apiName RemoveBoardMember
    @apiGroup Boards
    @apiHeader {String} Authorization Bearer <access_token>
    @apiParam {Number} id Board ID
    @apiParam {Number} user_id User ID to remove
    @apiSuccess {Object} board Updated board object
    """
    current_user_id = int(get_jwt_identity())
    board = Board.query.get_or_404(board_id)

    if not any(member.id == current_user_id for member in board.members):
        return jsonify({'message': 'Access denied'}), 403

    user = User.query.get_or_404(user_id)
    if user not in board.members:
        return jsonify({'message': 'User is not a member'}), 400

    if len(board.members) == 1:
        return jsonify({'message': 'Cannot remove last member'}), 400

    board.members.remove(user)
    db.session.commit()

    return jsonify(board.to_dict()), 200
