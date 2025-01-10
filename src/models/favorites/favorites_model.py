from sqlalchemy import PrimaryKeyConstraint
from models import db

class Favorites(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)

    # user_from_id = 
    # user_to_id = 

    # __table_args__ = (
    #     PrimaryKeyConstraint('client_id', 'professional_id'),
    #     {}
    # )

    def serialize(self):
        return {
                 
        }
    