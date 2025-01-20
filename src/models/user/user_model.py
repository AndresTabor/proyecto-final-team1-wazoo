from datetime import datetime, timezone
from models import db
from sqlalchemy import Enum

from enum import Enum as PyEnum 

class User_Role(str, PyEnum):
    ADMIN = "admin"
    CLIENT = "client"
    PROFESSIONAL = "professional"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    location = db.Column(db.String(80), unique=False, nullable=True)
    image = db.Column(db.String(200), unique=False, nullable=True)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False, default=True)
    date_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    role = db.Column(db.Enum(User_Role, name="use_role_enum"), nullable=False, default=User_Role.CLIENT)

    followers = db.relationship(
        "User", secondary="favorites", 
        primaryjoin="User.id==favorites.c.user_to_id", 
        secondaryjoin="User.id==favorites.c.user_from_id", 
        back_populates="following"
    )

    following = db.relationship(
        "User", 
        secondary="favorites", 
        primaryjoin="User.id==favorites.c.user_from_id", 
        secondaryjoin="User.id==favorites.c.user_to_id", 
        back_populates="followers"
    )


    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "fullname": self.fullname,
            "email": self.email,
            "location": self.location,
            "image": self.image,
            "is_active": self.is_active,
            "date_at": self.date_at.isoformat(),
            "role": self.role.value,
            "followers": [follower.serialize_basic() for follower in self.followers],
            "following": [followed.serialize_basic() for followed in self.following],
        }

    def serialize_basic(self):
        return {
            "id": self.id,
            "fullname": self.fullname,
            "email": self.email,
            "image": self.image
        }