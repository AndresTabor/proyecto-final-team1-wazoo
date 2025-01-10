from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user.user_model import User
from models.favorites.favorites_model import Favorites
