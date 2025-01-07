from models import db

class Professional(db.Model):
    __tablename__ = 'professionals'

    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(120), unique=False, nullable=False)

    favorites = db.relationship('Favorites', back_populates='professional',cascade="all, delete-orphan")
    