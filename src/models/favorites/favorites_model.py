from sqlalchemy import PrimaryKeyConstraint
from models import db

class Favorites(db.Model):
    __tablename__ = 'favorites'
    # id = db.Column(db.Integer, primary_key=True)

    user_from_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user_to_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('user_from_id', 'user_to_id'),
        {}
    )

    def serialize(self):
        return {
                       
        }
    