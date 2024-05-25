"""SQLAlchemy models for Ratatouille."""

# from csv import DictReader
from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

bcrypt = Bcrypt()
db = SQLAlchemy()


class MyDateTime(db.TypeDecorator):
    impl = db.DateTime

    def process_bind_param(self, value, dialect):
        if type(value) is str:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
        return value

class Follows(db.Model):
    """Connection of a follower <-> followed_user."""

    __tablename__ = 'follows'

    user_being_followed_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    user_following_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )


class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )


    location = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    bio = db.Column(
        db.Text,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.jpg",
    )

    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_being_followed_id == id),
        secondaryjoin=(Follows.user_following_id == id)
    )

    following = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_being_followed_id == id)
    )

    reviews = db.relationship('Review', backref = "user" )

    favorites_restaurants = db.relationship('Restaurant', secondary = "favorites", backref = "favorited_by_users")

    wishlist_restaurants = db.relationship('Restaurant', secondary = "wishlist_restaurants", backref = "wishlisted_by_users")

    visited_restaurants = db.relationship('Restaurant', secondary = "visited_restaurants", backref = "visited_by_users")

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def is_followed_by(self, other_user):
        """Is this user followed by `other_user`?"""

        found_user_list = [user for user in self.followers if user == other_user]
        return len(found_user_list) == 1

    def is_following(self, other_user):
        """Is this user following `other_use`?"""

        found_user_list = [user for user in self.following if user == other_user]
        return len(found_user_list) == 1

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """
        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Restaurant(db.Model):
    """Restaurants"""

    __tablename__ = 'restaurants' 

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    address = db.Column(
        db.Text,
    )

    reviews = db.relationship('Review', backref= 'restaurant')

    __table_args__ = (db.UniqueConstraint('name', 'address', name='_name_address_uc'),)


class Favorites(db.Model):
    """User's favorite restaurants"""

    __tablename__ = 'favorites' 

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    restaurant_id = db.Column(
        db.Integer,
        db.ForeignKey('restaurants.id', ondelete='cascade'),
 
    )

    restaurant = db.relationship('Restaurant', backref='favorited_by')


class WishlistRestaurants(db.Model):
    """User's wishlist restaurants"""

    __tablename__ = 'wishlist_restaurants' 

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    restaurant_id = db.Column(
        db.Integer,
        db.ForeignKey('restaurants.id', ondelete='cascade')
    )

    restaurant = db.relationship('Restaurant', backref='wishlisted_by')


class VisitedRestaurants(db.Model):
    """User's visited restaurants"""

    __tablename__ = "visited_restaurants"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    restaurant_id = db.Column(
        db.Integer,
        db.ForeignKey('restaurants.id', ondelete='cascade')
    )

    restaurant = db.relationship('Restaurant', backref='visited_by')


class Review(db.Model):
    """User's reviews about restaurants"""

    __tablename__ = 'reviews' 

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade'),
        nullable = False
    )

    restaurant_id = db.Column(
        db.Integer,
        db.ForeignKey('restaurants.id', ondelete='cascade')
    )

    content = db.Column(
        db.Text,
        nullable = False
    )

    timestamp = db.Column(
        MyDateTime,
        nullable=False,
        default=datetime.now(),
    )

    # user = db.relationship('User', backref='user_reviews')



def connect_db(app):
    """Connect this db to provide Flask app"""

    db.app = app
    db.init_app(app)

    #Seed database if no records are present in the User, Restaurant or Review table

    # if len(User.query.all()) == 0 or len(Restaurant.query.all()) == 0 or len(Review.query.all()) == 0 or len(WishlistRestaurants.query.all()) == 0 or len(VisitedRestaurants.query.all()) == 0 or len(Favorites.query.all()) == 0:
    #     db.drop_all()
    #     db.create_all()

    
