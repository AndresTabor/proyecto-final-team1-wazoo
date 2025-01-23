from models import db

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profession_title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(100), nullable=False)

    # relación con User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Post {self.profession_title}>'

    def serialize(self):
        return {
            "id": self.id,
            "profession_title": self.profession_title,
            "description": self.description,
            "price_per_hour": self.price_per_hour,
            "experience": self.experience,
            "image_url": self.image_url,
            "location": self.location,
            "user": self.user.serialize_basic()  # incluye datos basicos del usuario
        }
