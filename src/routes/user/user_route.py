from datetime import timedelta
from flask import Blueprint
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from sqlalchemy.exc import SQLAlchemyError
from config import jwt_redis_blocklist

from models import User, db, Client

user_bp = Blueprint('user_bp', __name__)
bcrypt = Bcrypt()

@user_bp.route('/register', methods=['POST'])
def register():
    user_data = request.get_json()
    user_data["password"] = bcrypt.generate_password_hash(user_data["password"]).decode('utf-8')
    new_user = User(**user_data)
    db.session.add(new_user)
    try:
        db.session.add(new_user)
        db.session.flush()  
        new_client = Client(id_user=new_user.id, fullname=user_data["fullname"])
        db.session.add(new_client)
        db.session.commit()
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "msg": "Error during registration",
            "error": str(e)
        }), 400
    
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
