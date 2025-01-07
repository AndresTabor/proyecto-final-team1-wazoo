from models import db

class Client(db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key = True)
    fullname = db.Column(db.String(120), nullable = False)
    
    id_user = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)

    favorites = db.relationship('Favorites', back_populates='client', cascade="all, delete-orphan")