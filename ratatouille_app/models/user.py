# from ratatouille_app import db, bcrypt
from ratatouille_app.models import db, bcrypt

default_pic = "/static/images/default-pic.jpg"

from flask import current_app

class User(db.Model):
    """User model"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    location = db.Column(db.Text)
    password = db.Column(db.Text, nullable=False)
    bio = db.Column(db.Text)
    image_url = db.Column(db.Text, default = default_pic)

    reviews = db.relationship('Review', backref='user', cascade='all, delete-orphan')
    favorites_restaurants = db.relationship('Restaurant', secondary = "favorites", back_populates = "favorited_by_users")
    wishlist_restaurants = db.relationship('Restaurant', secondary = "wishlist_restaurants", back_populates = "wishlisted_by_users")
    visited_restaurants = db.relationship('Restaurant', secondary = "visited_restaurants", back_populates = "visited_by_users")

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"
    
    @classmethod
    def signup(cls, username, email, password, image_url = None):
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        if not image_url:
            image_url = current_app.config['DEFAULT_IMAGE_URL']
        
        user = User(username=username, email=email, password=hashed_pwd, image_url=image_url)

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Find user with 'username' and 'password' """
        user = cls.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        return False


class UserRestaurants(db.Model):
    """Mapping of a user's restaurants based on their saved location"""

    __tablename__ = "user_restaurants"

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id', ondelete='cascade'), primary_key=True)
    restaurant = db.relationship('Restaurant', backref = 'my_places')