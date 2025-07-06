from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, List, Board

lists_bp = Blueprint('lists', __name__)

@lists_bp.route('/boards/<int:board_id>/lists', methods=['POST'])
@jwt_required()
def create_list(board_id):
    """
    @api {post} /api/boards/:board_id/lists Create a new list
    @apiName CreateList
    @apiGroup Lists
    @apiHeader {String} Authorization Bearer <access_token>
    @apiParam {Number} board_id Board ID
    @apiParam {String} title List title
    @apiParam {Number} position List position (optional)
    @apiSuccess {Object} list Created list object
    """
    current_user_id = get_jwt_identity()
    board = Board.query.get_or_404(board_id)

    if not any(member.id == current_user_id for member in board.members):
        return jsonify({'message': 'Access denied'}), 403

    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'message': 'Title is required'}), 400

    # Get the maximum position value for the current board's lists
    max_position = db.session.query(db.func.max(List.position)).filter_by(board_id=board_id).scalar() or -1
    position = data.get('position', max_position + 1)

    list = List(
        title=data['title'],
        board_id=board_id,
        position=position
    )

    db.session.add(list)
    db.session.commit()

    return jsonify(list.to_dict()), 201

@lists_bp.route('/boards/<int:board_id>/lists', methods=['GET'])
@jwt_required()
def get_lists(board_id):
    """
    @api {get} /api/boards/:board_id/lists Get board lists
    @apiName GetLists
    @apiGroup Lists
    @apiHeader {String} Authorization Bearer <access_token>
    @apiParam {Number} board_id Board ID
    @apiSuccess {Array} lists List of list objects
    """
    current_user_id = get_jwt_identity()
    board = Board.query.get_or_404(board_id)

    if not any(member.id == current_user_id for member in board.members):
        return jsonify({'message': 'Access denied'}), 403

    lists = List.query.filter_by(board_id=board_id).order_by(List.position).all()
    return jsonify([list.to_dict() for list in lists]), 200

@lists_bp.route('/lists/<int:list_id>', methods=['PUT'])
@jwt_required()
def update_list(list_id):
    """
    @api {put} /api/lists/:id Update list
    @apiName UpdateList
    @apiGroup Lists
    @apiHeader {String} Authorization Bearer <access_token>
    @apiParam {Number} id List ID
    @apiParam {String} title New list title
    @apiParam {Number} position New position (optional)
    @apiSuccess {Object} list Updated list object
    """
    current_user_id = get_jwt_identity()
    list = List.query.get_or_404(list_id)
    board = Board.query.get(list.board_id)

    if not any(member.id == current_user_id for member in board.members):
        return jsonify({'message': 'Access denied'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    if 'title' in data:
        list.title = data['title']
    
    if 'position' in data:
        list.position = data['position']

    db.session.commit()

    return jsonify(list.to_dict()), 200

@lists_bp.route('/lists/<int:list_id>', methods=['DELETE'])
@jwt_required()
def delete_list(list_id):
    """
    @api {delete} /api/lists/:id Delete list
    @apiName DeleteList
    @apiGroup Lists
    @apiHeader {String} Authorization Bearer <access_token>
    @apiParam {Number} id List ID
    @apiSuccess {String} message Success message
    """
    current_user_id = get_jwt_identity()
    list = List.query.get_or_404(list_id)
    board = Board.query.get(list.board_id)

    if not any(member.id == current_user_id for member in board.members):
        return jsonify({'message': 'Access denied'}), 403

    db.session.delete(list)
    db.session.commit()

    return jsonify({'message': 'List deleted successfully'}), 200

@lists_bp.route('/lists/reorder', methods=['POST'])
@jwt_required()
def reorder_lists():
    """
    @api {post} /api/lists/reorder Reorder lists
    @apiName ReorderLists
    @apiGroup Lists
    @apiHeader {String} Authorization Bearer <access_token>
    @apiParam {Array} orders Array of {id, position} objects
    @apiSuccess {String} message Success message
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'orders' not in data:
        return jsonify({'message': 'Orders array is required'}), 400

    # Verify access to the board
    first_list = List.query.get_or_404(data['orders'][0]['id'])
    board = Board.query.get(first_list.board_id)

    if not any(member.id == current_user_id for member in board.members):
        return jsonify({'message': 'Access denied'}), 403

    for order in data['orders']:
        list = List.query.get(order['id'])
        if list and list.board_id == board.id:
            list.position = order['position']

    db.session.commit()

    return jsonify({'message': 'Lists reordered successfully'}), 200
