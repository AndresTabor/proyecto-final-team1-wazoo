import redis
from routes.user.user_route import user_bp
from routes.post.post_route import post_bp

jwt_redis_blocklist = redis.StrictRedis(
    host="redis", 
    port=6379, 
    db=0, 
    decode_responses=True
)