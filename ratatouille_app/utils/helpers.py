from flask import session, g, flash, redirect
from ratatouille_app.models import User, Restaurant, db
from ratatouille_app.models.restaurant import Favorites, WishlistRestaurants, VisitedRestaurants
from ratatouille_app.models.review import Review
import requests
from ..config import Config

config = Config()



def add_user_to_g():
    """If a user is logged in, add them to Flask global"""
    if config.CURR_USER_KEY in session:
        g.user = User.query.get(session[config.CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    """Log in user"""
    session.clear()
    session[config.CURR_USER_KEY] = user.id

def do_logout():
    """Logout user"""
    if config.CURR_USER_KEY in session:
        del session[config.CURR_USER_KEY]



def fetch_restaurants(place, api_key):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=restaurants+in+{place}&key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        restaurants = data.get("results", [])
    else:
        print(f"Error: {response.status_code}")
        restaurants = []

    return restaurants



def get_photo_url(photo_reference, api_key):
    url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_reference}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.url
    else:
        return None


def save_restaurant_to_db(name, address, photos, api_key):
    """Save restaurant to the database if it doesn't already exist."""
    restaurant = Restaurant.query.filter_by(name=name, address=address).first()
    if not restaurant:
        # Get the first photo URL
        photo_url = None
        if photos:
            photo_reference = photos[0].get("photo_reference")
            photo_url = get_photo_url(photo_reference, api_key)
        
        restaurant = Restaurant(name=name, address=address, photos=photo_url)
        db.session.add(restaurant)
        db.session.commit()
    return restaurant


def get_user_lists(user_id):
    """Fetch user's lists of favorite, wishlisted, and visited restaurants, including reviews for visited restaurants."""
    favorites = Favorites.query.filter_by(user_id=user_id).all()
    wishlisted = WishlistRestaurants.query.filter_by(user_id=user_id).all()
    visited = VisitedRestaurants.query.filter_by(user_id=user_id).all()
    visited_with_reviews = [(visit, Review.query.filter_by(user_id=user_id, restaurant_id=visit.restaurant_id).all()) for visit in visited]

    return favorites, wishlisted, visited, visited_with_reviews


def toggle_list(model, user_id, restaurant_id, action):
    """Toggle restaurant in user's corresponding list"""
    entry = model.query.filter_by(user_id = user_id, restaurant_id = restaurant_id).first()

    if entry:
        db.session.delete(entry)
        db.session.commit()
        flash(f"Removed from {action}.")
    else:
        new_entry = model(user_id=user_id, restaurant_id=restaurant_id)
        db.session.add(new_entry)
        db.session.commit()
        flash(f"Added restaurant to {action}")



def delete_from_list(model, user_id, restaurant_id, action):
    """Delete restaurant from user's list."""
    entry = model.query.filter_by(user_id = user_id, restaurant_id = restaurant_id)

    if entry:
        db.session.delete(entry)
        db.session.commit()
        flash(f"Removed from {action}.")

    return redirect(f"/my_lists/{user_id}")


def get_user(user_id):
    """Get user by ID or return 404 if not found."""
    return User.query.get_or_404(user_id)


def get_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    if not restaurant:
        flash("Restaurant not found.")
        return redirect(f'/{g.user.id}')
    return restaurant


def check_user_authentication():
    """Check if the user is authenticated, flash a message, and redirect if not."""
    if not g.user:
        flash("Access unauthorized.")
        return redirect("/")
    return None


def get_review_or_redirect(review_id, action):
    """Check if the review exists and if it belongs to the current user, otherwise redirect."""
    review = Review.query.filter_by(id=review_id, user_id=g.user.id).first()
    if not review:
        flash("Review not found.")
        return redirect(f'/my_lists/{g.user.id}')
    
    if review.user_id != g.user.id:
        flash(f"You are not authorized to {action} this review.")
        return redirect("/")

    return review



# To be called with after request
def add_header(req):
    """Add non-caching headers on every request."""
    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req