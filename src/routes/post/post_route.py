from flask import Blueprint, request, jsonify
from models import Post, db
# importamos la funcion geodesic 
from geopy.distance import geodesic

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
            location=data['location'],
            user_id=data['user_id']
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

# ruta para los post filtrados
@post_bp.route('/filter_posts', methods=['GET'])
def get_filtered_posts():
    try:
        
        profession_title = request.args.get('profession_title', type=str)
        location = request.args.get('location', type=str)
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        page = request.args.get('page', 1, type=int)  # numero de página (por defecto 1)
        limit = request.args.get('limit', 10, type=int)  # numero de resultados por página (por defecto 10)

        query = Post.query

        if profession_title:
            query = query.filter(Post.profession_title.ilike(f"%{profession_title}%"))
        
        if location:
            query = query.filter(Post.location.ilike(f"%{location}%"))

        if min_price:
            query = query.filter(Post.price_per_hour >= min_price)
        if max_price:
            query = query.filter(Post.price_per_hour <= max_price)

        # si se introduce la latitud y longitud, filtramos por proximidad
        if latitude and longitude:
            posts = query.all()
            nearby_posts = []
            for post in posts:
                post_location = post.location.split(',')
                post_lat = float(post_location[0])
                post_lon = float(post_location[1])
                # geodesic calcula la distancia entre dos puntos
                distance = geodesic((latitude, longitude), (post_lat, post_lon)).km
                if distance <= 50:
                    nearby_posts.append(post)
            
            #paginacion de los resultados a menos de 50km
            total_posts = len(nearby_posts)
            total_pages = (total_posts // limit) + (1 if total_posts % limit > 0 else 0)
            start = (page - 1) * limit
            end = start + limit
            paginated_posts = nearby_posts[start:end]
            
            return jsonify({
                "status": "success",
                "data": [post.serialize() for post in paginated_posts],
                "pagination": {
                    "current_page": page,
                    "total_pages": total_pages,
                    "total_posts": total_posts,
                    "per_page": limit
                }
            }), 200
        else:
            #paginacion sin proximidad
            total_posts = query.count()
            total_pages = (total_posts // limit) + (1 if total_posts % limit > 0 else 0)
            start = (page - 1) * limit
            end = start + limit
            filtered_posts = query.offset(start).limit(limit).all()
            
            return jsonify({
                "status": "success",
                "data": [post.serialize() for post in filtered_posts],
                "pagination": {
                    "current_page": page,
                    "total_pages": total_pages,
                    "total_posts": total_posts,
                    "per_page": limit
                }
            }), 200

    except Exception as e:
        return jsonify({"error": "Ocurrió un error al obtener las publicaciones filtradas", "details": str(e)}), 500




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
