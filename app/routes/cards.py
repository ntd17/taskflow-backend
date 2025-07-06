from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Card, List, Board

cards_bp = Blueprint('cards', __name__)

@cards_bp.route('/lists/<int:list_id>/cards', methods=['POST'])
@jwt_required()
def create_card(list_id):
    """
    @api {post} /api/lists/:list_id/cards Create a new card
    @apiName CreateCard
    @apiGroup Cards
    @apiHeader {String} Authorization Bearer <access_token>
    @apiParam {Number} list_id List ID
    @apiParam {String} title Card title
    @apiParam {String} description Card description (optional)
    @apiParam {Number} position Card position (optional)
    @apiSuccess {Object} card Created card object
    """
    current_user_id = get_jwt_identity()
    list = List.query.get_or_404(list_id)
    board = Board.query.get(list.board_id)

    if not any(member.id == current_user_id for member in board.members):
        return jsonify({'message': 'Access denied'}), 403

    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'message': 'Title is required'}), 400

    # Get the maximum position value for the current list's cards
    max_position = db.session.query(db.func.max(Card.position)).filter_by(list_id=list_id).scalar() or -1
    position = data.get('position', max_position + 1)

    card = Card(
        title=data['title'],
        description=data.get('description', ''),
        list_id=list_id,
        position=position
    )

    db.session.add(card)
    db.session.commit()

    return jsonify(card.to_dict()), 201

@cards_bp.route('/lists/<int:list_id>/cards', methods=['GET'])
@jwt_required()
def get_cards(list_id):
    """
    @api {get} /api/lists/:list_id/cards Get list cards
    @apiName GetCards
    @apiGroup Cards
    @apiHeader {String} Authorization Bearer <access_token>
    @apiParam {Number} list_id List ID
    @apiSuccess {Array} cards List of card objects
    """
    current_user_id = get_jwt_identity()
    list = List.query.get_or_404(list_id)
    board = Board.query.get(list.board_id)

    if not any(member.id == current_user_id for member in board.members):
        return jsonify({'message': 'Access denied'}), 403

    cards = Card.query.filter_by(list_id=list_id).order_by(Card.position).all()
    return jsonify([card.to_dict() for card in cards]), 200

@cards_bp.route('/cards/<int:card_id>', methods=['GET'])
@jwt_required()
def get_card(card_id):
    """
    @api {get} /api/cards/:id Get card details
    @apiName GetCard
    @apiGroup Cards
    @apiHeader {String} Authorization Bearer <access_token>
    @apiParam {Number} id Card ID
    @apiSuccess {Object} card Card object
    """
    current_user_id = get_jwt_identity()
    card = Card.query.get_or_404(card_id)
    list = List.query.get(card.list_id)
    board = Board.query.get(list.board_id)

    if not any(member.id == current_user_id for member in board.members):
        return jsonify({'message': 'Access denied'}), 403

    return jsonify(card.to_dict()), 200

@cards_bp.route('/cards/<int:card_id>', methods=['PUT'])
@jwt_required()
def update_card(card_id):
    """
    @api {put} /api/cards/:id Update card
    @apiName UpdateCard
    @apiGroup Cards
    @apiHeader {String} Authorization Bearer <access_token>
    @apiParam {Number} id Card ID
    @apiParam {String} title New card title (optional)
    @apiParam {String} description New card description (optional)
    @apiParam {Number} list_id New list ID (optional)
    @apiParam {Number} position New position (optional)
    @apiSuccess {Object} card Updated card object
    """
    current_user_id = get_jwt_identity()
    card = Card.query.get_or_404(card_id)
    list = List.query.get(card.list_id)
    board = Board.query.get(list.board_id)

    if not any(member.id == current_user_id for member in board.members):
        return jsonify({'message': 'Access denied'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    if 'title' in data:
        card.title = data['title']
    if 'description' in data:
        card.description = data['description']
    if 'position' in data:
        card.position = data['position']
    if 'list_id' in data:
        # Verify the new list belongs to the same board
        new_list = List.query.get_or_404(data['list_id'])
        if new_list.board_id != board.id:
            return jsonify({'message': 'Invalid list ID'}), 400
        card.list_id = data['list_id']

    db.session.commit()

    return jsonify(card.to_dict()), 200

@cards_bp.route('/cards/<int:card_id>', methods=['DELETE'])
@jwt_required()
def delete_card(card_id):
    """
    @api {delete} /api/cards/:id Delete card
    @apiName DeleteCard
    @apiGroup Cards
    @apiHeader {String} Authorization Bearer <access_token>
    @apiParam {Number} id Card ID
    @apiSuccess {String} message Success message
    """
    current_user_id = get_jwt_identity()
    card = Card.query.get_or_404(card_id)
    list = List.query.get(card.list_id)
    board = Board.query.get(list.board_id)

    if not any(member.id == current_user_id for member in board.members):
        return jsonify({'message': 'Access denied'}), 403

    db.session.delete(card)
    db.session.commit()

    return jsonify({'message': 'Card deleted successfully'}), 200

@cards_bp.route('/cards/reorder', methods=['POST'])
@jwt_required()
def reorder_cards():
    """
    @api {post} /api/cards/reorder Reorder cards
    @apiName ReorderCards
    @apiGroup Cards
    @apiHeader {String} Authorization Bearer <access_token>
    @apiParam {Array} orders Array of {id, position, list_id} objects
    @apiSuccess {String} message Success message
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'orders' not in data:
        return jsonify({'message': 'Orders array is required'}), 400

    # Verify access to the board
    first_card = Card.query.get_or_404(data['orders'][0]['id'])
    list = List.query.get(first_card.list_id)
    board = Board.query.get(list.board_id)

    if not any(member.id == current_user_id for member in board.members):
        return jsonify({'message': 'Access denied'}), 403

    for order in data['orders']:
        card = Card.query.get(order['id'])
        if card:
            # If moving to a different list, verify it belongs to the same board
            if 'list_id' in order and order['list_id'] != card.list_id:
                new_list = List.query.get_or_404(order['list_id'])
                if new_list.board_id != board.id:
                    continue
                card.list_id = order['list_id']
            card.position = order['position']

    db.session.commit()

    return jsonify({'message': 'Cards reordered successfully'}), 200
