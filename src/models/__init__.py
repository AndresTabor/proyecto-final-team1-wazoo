from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user.user_model import User
from models.professional.professional_model import Professional
from models.client.client_model import Client
from models.favorites.favorites_model import Favorites
from models.post import post_model
