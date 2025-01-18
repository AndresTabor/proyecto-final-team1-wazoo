"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import base64
from datetime import timedelta
import os
import bcrypt
from flask import Flask, request, jsonify, url_for
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from pydantic import ValidationError
import redis


from admin import setup_admin
from config import jwt_redis_blocklist
from models import db, User
from routes import user_bp, post_bp, favorites_bp

from flask_jwt_extended import JWTManager, create_access_token, get_jwt, get_jwt_identity, jwt_required

from utils import APIException, generate_sitemap
#from models import Person

ACCESS_EXPIRES = timedelta(minutes=15)

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


secret = os.getenv("JWT_SECRET_KEY")
app.config["JWT_SECRET_KEY"] = secret
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
jwt = JWTManager(app)


app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='wazooapp2025@gmail.com',
    MAIL_PASSWORD='ucjqqkofmtnkwgmj'
)
mail = Mail(app)




@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None



@jwt.additional_claims_loader
def add_claims_to_access_token(identity):
    user = User.query.get(identity)
    if user:
        return {
            'role': user.role,
            'is_active': user.is_active
        }

app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(post_bp, url_prefix='/posts')
app.register_blueprint(favorites_bp, url_prefix='/favorites')

@app.route('/request-reset-password', methods=["POST"])
def request_reset_password():
    email = request.json.get("email")
    if email is None:
        raise APIException("Email is required", status_code=400)
    
    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"message":"User not found"}), 404
    
    token = create_access_token(identity=str(user.id), expires_delta=timedelta(minutes=3), additional_claims={"email": email}) 
    token_byte = token.encode('utf-8')
    token = base64.b64encode(token_byte)
    
    reset_link = f"http://localhost:3000/reset-password/{token}"
    msg = Message(
        'Recover your password',
        sender=app.config["MAIL_USERNAME"],
        recipients=[email]
    )

    with open("src/config/recover_pass.htm", "r", encoding="utf-8") as file:
        msg.html = file.read().replace("[Nombre del Usuario]", user.fullname).replace("[ENLACE_PERSONALIZADO]", reset_link)

    mail.send(msg)

    return jsonify({"message":"Email enviado"})





# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
