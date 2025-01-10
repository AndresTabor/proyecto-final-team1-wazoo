from datetime import datetime, timezone
from models import db
from sqlalchemy import Enum

from enum import Enum as PyEnum 

class User_Role(str, PyEnum):
    ADMIN = "admin"
    CLIENT = "client",
    PROFESSIONAL = "professional"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False, default=True)
    date_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    role = db.Column(db.Enum(User_Role, name="myenum"), nullable=False)

    # favorites =db.relationship('Favorites', back_populates='user', cascade="all, delete-orphan") 


    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "date_at": self.date_at,
            "role": self.role
            # do not serialize the password, its a security breach
        }