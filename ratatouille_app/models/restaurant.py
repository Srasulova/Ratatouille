# from ratatouille_app import db
from ratatouille_app.models import db

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

    photos = db.Column(
        db.Text,
    )

    reviews = db.relationship('Review', backref='restaurant')
    favorited_by_users = db.relationship('User', secondary='favorites', back_populates='favorites_restaurants')
    wishlisted_by_users = db.relationship('User', secondary='wishlist_restaurants', back_populates='wishlist_restaurants')
    visited_by_users = db.relationship('User', secondary='visited_restaurants', back_populates='visited_restaurants')

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

    restaurant = db.relationship('Restaurant', backref='favorites')
    user = db.relationship('User', backref='favorites')



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

    restaurant = db.relationship('Restaurant', backref='wishlisted')
    user = db.relationship('User', backref='wishlist')



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

    restaurant = db.relationship('Restaurant', backref='visited')
    user = db.relationship('User', backref='visited')
