from flask import Blueprint, request, jsonify
from models import Post, db

post_bp = Blueprint('post_bp', __name__)

@post_bp.route('/post', methods=['POST'])
def create_new_post():
    try:
        data = request.json
        # validar campos necesarios
        required_fields = ['profession_title', 'description', 'price_per_hour', 'experience', 'image_url', 'location']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"'{field}' es un campo requerido"}), 400
        
        new_post = Post(
            profession_title=data['profession_title'],
            description=data['description'],
            price_per_hour=data['price_per_hour'],
            experience=data['experience'],
            image_url=data['image_url'],
            location=data['location']
        )

        # guarda nuevo post en la db
        db.session.add(new_post)
        db.session.commit()
        
        # respuesta correcta
        return jsonify({
            "status": "success",
            "message": "Publicación creada exitosamente",
            "data": new_post.serialize()
        }), 201
    except Exception as error:
        return jsonify({"error": "Ocurrió un error al crear la publicación", "details": str(error)}), 500

@post_bp.route('/post', methods=['GET'])
def get_all_post():
    try:
        # consultar todas las publicaciones en la db
        publications = Post.query.all()
        return jsonify({
            "status": "success",
            "data": [pub.serialize() for pub in publications]
        }), 200
    except Exception as error:
        return jsonify({"error": "Ocurrió un error al obtener las publicaciones", "details": str(error)}), 500
