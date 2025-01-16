from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import SQLAlchemyError

from models import User, Favorites, db


favorites_bp = Blueprint("favorites_bp", __name__)


@favorites_bp.route("/add", methods=["POST"])
@jwt_required()
def add_favorite():
    request_data = request.get_json()
    user_from_id = get_jwt_identity()
    user_to_id = request_data.get("user_to_id")
    if not user_to_id:
        return jsonify({"msg": "Field 'user_to_id' is required"}), 400
    if user_from_id == user_to_id:
        return jsonify({"msg": "You cannot add yourself as a favorite"}), 400
    user_to = User.query.get(user_to_id)
    if not user_to:
        return jsonify({"msg": f"User with ID {user_to_id} does not exist"}), 404
    
    existing_favorite = Favorites.query.filter_by(user_from_id=user_from_id, user_to_id=user_to_id).first()
    if existing_favorite:
        return jsonify({"msg": "The favorite already exists"}), 400
    
    try:
        new_favorite = Favorites(user_from_id=user_from_id, user_to_id=user_to_id)
        db.session.add(new_favorite)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "msg": "Error during update",
            "error": str(e)
        }), 500
    return jsonify({"msg": "Favorito creado exitosamente"}), 201

@favorites_bp.route('/remove/<int:user_to_id>', methods=["DELETE"])
@jwt_required()
def delete_favorite(user_to_id):
    try:
        user_from_id = get_jwt_identity()
        favorite = Favorites.query.filter_by(user_from_id=user_from_id, user_to_id=user_to_id).first()
        if not favorite:
            return jsonify({"msg": "Favorite does not exist"}), 404
        db.session.delete(favorite)
        db.session.commit()

        return jsonify({"msg": "Favorite removed"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"msg": "Failed to delete favorite", "error": str(e)}), 500
    

@favorites_bp.route('/my-favorites', methods=["GET"])
@jwt_required()
def get_favorites():
    try:
        user_from_id = get_jwt_identity()
        user = User.query.get(user_from_id)
        if user is None:
            return jsonify({"msg": "User not found"}), 404

        favorites = user.following
        favorites_list = [
            {
                "id": favorite.id,
                "fullname": favorite.fullname,
                "email": favorite.email
            }
            for favorite in favorites
        ]

        return jsonify(favorites_list), 200

    except SQLAlchemyError as e:
        return jsonify({"msg": "Error getting favorites", "error": str(e)}), 500

    

