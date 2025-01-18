from flask import Blueprint, request, jsonify
from models import Post, db

post_bp = Blueprint('post_bp', __name__)

@post_bp.route('/', methods=['POST'])
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
    except Exception as e:
        return jsonify({"error": "Ocurrió un error al crear la publicación", "details": str(e)}), 500

@post_bp.route('/', methods=['GET'])
def get_all_post():
    try:
        # consultar todas las publicaciones en la db
        publications = Post.query.all()
        return jsonify({
            "status": "success",
            "data": [pub.serialize() for pub in publications]
        }), 200
    except Exception as e:
        return jsonify({"error": "Ocurrió un error al obtener las publicaciones", "details": str(e)}), 500

# GET SINGLE POST
@post_bp.route('/<int:id>', methods=['GET'])
def get_post_by_id(id):
    post = Post.query.get(id)
    if post is None:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(post.serialize()), 200

#EDIT POST
@post_bp.route('/<int:id>', methods=['PUT'])
def update_post(id):
    try:
        post = Post.query.get(id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        data = request.json
        # actualiza solo lo enviado en la solicitud
        if 'profession_title' in data:
            post.profession_title = data['profession_title']
        if 'description' in data:
            post.description = data['description']
        if 'price_per_hour' in data:
            post.price_per_hour = data['price_per_hour']
        if 'experience' in data:
            post.experience = data['experience']
        if 'image_url' in data:
            post.image_url = data['image_url']
        if 'location' in data:
            post.location = data['location']
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Post actualizado exitosamente",
            "data": post.serialize()
        }), 200
    except Exception as e:
        return jsonify({"error": "Ocurrió un error al actualizar el post", "details": str(e)}), 500
    
#
