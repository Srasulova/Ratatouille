from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


bcrypt = Bcrypt()
db = SQLAlchemy()
migrate = Migrate()

# Importing models to make sure they are registered correctly
from .user import User, UserRestaurants
from .restaurant import Restaurant, Favorites, WishlistRestaurants, VisitedRestaurants
from .review  import Review


def connect_db(app): 
    """Connect the db to the Flask app"""
    db.app = app
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    with app.app_context():
       db.create_all()