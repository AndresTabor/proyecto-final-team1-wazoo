from datetime import timedelta
from flask import Blueprint
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from config import jwt_redis_blocklist

from models import User, db, UserDto


user_bp = Blueprint('user_bp', __name__)
bcrypt = Bcrypt()

@user_bp.route('/register', methods=['POST'])
def register():
    try:
        user_data = UserDto(**request.get_json())
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            if error['type'] == 'missing':
                # Campo faltante
                error_messages.append(f"Field '{error['loc'][0]}' is required.")
            else:
                # Otro tipo de error, usa el mensaje personalizado
                error_messages.append(error['msg'])

        return jsonify({"errors": error_messages}), 400
    
    user_data["password"] = bcrypt.generate_password_hash(user_data["password"]).decode('utf-8')
    new_user = User(**user_data)
    db.session.add(new_user)

    try:
        db.session.add(new_user)
        db.session.flush()  
        db.session.commit()
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "msg": "Error during registration",
            "error": str(e)
        }), 500
    
    return jsonify(new_user.serialize()), 201

@user_bp.route('/login', methods=['POST'])
def login():
    user_data = request.get_json()
    user = User.query.filter_by(email=user_data["email"]).first()
    if user is None:
        return jsonify({"msg": "Bad email"}), 401
    
    if bcrypt.check_password_hash(user.password, user_data["password"]):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token)
    
    return jsonify({"msg": "Bad password"}), 401

@user_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  
    jwt_redis_blocklist.set(jti, "", timedelta(minutes=15))  
    return jsonify(msg="Logout successful")

@user_bp.route("/profile", methods=["POST"])
@jwt_required()
def update_profile(id):
    user_data = request.get_json()
    user = User.query.get(id)
    if user is None:
        return jsonify({"msg": "user not found with id: {id}"}), 404
    
    db.session.commit()
    return jsonify(user.serialize()), 200
    
