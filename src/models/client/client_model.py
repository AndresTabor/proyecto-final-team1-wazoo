from models import db

class Client(db.Model):
    __tablename__ = 'clients'

    fullname = db.Column(db.String(120), nullable = False)
    
    id = db.Column(db.Interger, primary_key = True)
    id_user = db.Colum(db.Interger, db.ForeingKey("user.id"), nullable = False)

    favorites = db.relationship('Favorites', back_populates='client')