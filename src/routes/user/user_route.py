from datetime import timedelta
from flask import Blueprint
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from config import jwt_redis_blocklist, role_required

from models import User, db, UserDto, UserUpdatedDto, Post


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
                error_messages.append(f"Field '{error['loc'][0]}' is required.")
            else:
                error_messages.append(error['msg'])

        return jsonify({"errors": error_messages}), 400
    
    user_data.password = bcrypt.generate_password_hash(user_data.password).decode('utf-8')
    user = user_data.model_dump()
    new_user = User(**user)
    
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
        access_token = create_access_token(identity=str(user.id),additional_claims={"user": user.serialize()})
        return jsonify(access_token=access_token)
    
    return jsonify({"msg": "Bad password"}), 401

@user_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  
    jwt_redis_blocklist.set(jti, "", timedelta(minutes=15))  
    return jsonify(msg="Logout successful")

@user_bp.route("/profile", methods=["DELETE"])
@jwt_required()
def delete_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": "user not found with id: {user_id}"}), 404
    
    try:
        user.is_active = False
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "msg": "Error during deletion",
            "error": str(e)
        }), 500
    
    return jsonify({"msg": "User deleted"}), 200

@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": "user not found with id: {user_id}"}), 404
    
    try:
        data = request.get_json()
        if "password" in data:
            data.pop("password")
        user_data = UserUpdatedDto(**data)
    except ValidationError as e:
        error_messages = [error['msg'] for error in e.errors()]
        return jsonify({"errors": error_messages}), 400
    
    user_data.dtoToUser(user)

    try:  
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "msg": "Error during update",
            "error": str(e)
        }), 500
    return jsonify(user.serialize()), 200
    
@user_bp.route("/change-password", methods=["PATCH"])
@jwt_required()
def update_password():
    user = User.query.get(get_jwt_identity())
    if user is None:
        return jsonify({"msg": "user not found with id: {user_id}"}), 404
    user_data = request.get_json()
    
    if not bcrypt.check_password_hash(user.password, user_data["current_password"]):
        return jsonify({"msg": "Bad password"}), 401
    try:
        user_updated = UserUpdatedDto(password=user_data["new_password"])
        user_updated.password = bcrypt.generate_password_hash(user_updated.password).decode('utf-8')
        user_updated.dtoToUser(user)
    except ValidationError as e:
        error_messages = [error['msg'] for error in e.errors()]
        return jsonify({"errors": error_messages}), 400   
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "msg": "Error during update",
            "error": str(e)
        }), 500 
    return jsonify({"msg:": "password saved"}), 200

@user_bp.route("/profile/role", methods=["PATCH"])
@jwt_required()
def update_role():
    user = User.query.get(get_jwt_identity())
    if user is None:
        return jsonify({"msg": "user not found with id: {user_id}"}), 404
    data = request.get_json()
    role = data.get("role")
    if role == "admin" & user.role != "admin":
        return jsonify({"msg": "You can't change to admin role"}), 403
    
    user.role = data["role"]
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "msg": "Error during update",
            "error": str(e)
        }), 500
    return jsonify(user.serialize()), 200

@user_bp.route("/", methods=["GET"])
@jwt_required()
@role_required(["admin"])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200


@user_bp.route('/reset-password',methods=["POST"])
@jwt_required()
def reset_password():
    user_data = request.get_json()
    claims = get_jwt()
    email = claims.get("email", None)
    user = User.query.filter_by(email=email).first()
    
    if user is None:
        return jsonify({"msg":"User with email: {email} not found"}), 404
    
    if user_data['password'] == user_data['confirm_password']:
        try:
            user_updated = UserUpdatedDto(password=user_data["password"])
            user_updated.password = bcrypt.generate_password_hash(user_updated.password).decode('utf-8')
            user_updated.dtoToUser(user)
            
        except ValidationError as e:
            error_messages = [error['msg'] for error in e.errors()]
            return jsonify({"errors": error_messages}), 400   
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({
                "msg": "Error during update",
                "error": str(e)
            }), 500 
    return jsonify({"msg:": "password saved"}), 200


# peticion para obtener posts de un usuario
@user_bp.route('/<int:user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    try:
        posts = Post.query.filter_by(user_id=user_id).all()
        return jsonify([post.serialize() for post in posts]), 200
    except Exception as e:
        return jsonify({"error": "No se pudieron obtener los posts", "details": str(e)}), 500
