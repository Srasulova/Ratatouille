from flask import Flask, render_template, request, flash, redirect, session, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
import os
import requests
from models import db, connect_db, User, Restaurant, VisitedRestaurants, WishlistRestaurants, Favorites, Review, UserRestaurants
from sqlalchemy.exc import IntegrityError
from forms import UserAddForm, UserEditForm, LoginForm, ReviewForm
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import json


bcrypt = Bcrypt()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{app.root_path}/Ratatouille.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
# app.config['DEBUG'] = True
toolbar = DebugToolbarExtension(app)


CURR_USER_KEY = 'curr_user'
API_KEY = "AIzaSyDQaQ4Zi8e-5YKSb_9VJvkKns3uYoq435g"


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



migrate = Migrate(app, db)

with app.app_context():
   connect_db(app)
   db.create_all()

@app.before_request
def add_user_to_g():
    """If a user is logged in, add them to Flask global"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    """Log in user"""
    session.clear()
    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user"""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


#Homepage route

@app.route('/')
def homepage():
    """Show homepage and display the signup or login form based on user interaction"""  

    if not g.user:
        return render_template('home_anon.html')
    return redirect(f'/{g.user.id}')

    
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(username = form.username.data.strip(), password = form.password.data.strip(), email= form.email.data.strip(), image_url= form.image_url.data.strip() or User.image_url.default.arg)
            db.session.commit()
        except IntegrityError:
            flash("This username already exists! So many foodies think alike. Try another one!")
            return render_template('signup.html', form=form)
        do_login(user)

        return redirect(f'/{user.id}')
    return render_template('signup.html', form=form)


@app.route('/login', methods = ['GET', 'POST'])
def user_login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data.strip()

        user = User.authenticate(username, password)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!")
            return redirect(f'/{user.id}')
        else:
            return render_template('login.html', form=form)

    return render_template('login.html', form = form)
    

@app.route('/logout')
def logout():
    """Handle logout of user."""

    session.clear()
    flash("You have been logged out")
    return redirect("/")


@app.route('/<int:user_id>', methods=['GET', 'POST'])
def users_show(user_id):
    """Show user profile."""
    user = User.query.get_or_404(user_id)

    review_form = ReviewForm()
    user_edit_form = UserEditForm(obj=user)

    if user_edit_form.validate_on_submit():
        user.location = user_edit_form.location.data
        db.session.commit()
        flash("Location submitted successfully!")
        return redirect(f'/{g.user.id}')

    favorites = Favorites.query.filter_by(user_id=user.id).all()
    wishlisted = WishlistRestaurants.query.filter_by(user_id=user.id).all()
    visited = VisitedRestaurants.query.filter_by(user_id=user.id).all()

    visited_with_reviews = [(visit, Review.query.filter_by(user_id=user.id, restaurant_id=visit.restaurant_id).all()) for visit in visited]
            
    return render_template("page_user_profile.html", user=user, favorites = favorites, wishlisted = wishlisted, visited = visited, review_form = review_form, 
    visited_with_reviews = visited_with_reviews, user_edit_form = user_edit_form)


# Add restaurants to wishlist, favorites and visited:

@app.route('/add_favorite/<int:restaurant_id>', methods=["GET", "POST"])
def toggle_favorite(restaurant_id):
    if not g.user:
        flash("Access unauthorized.")
        return redirect("/")

    restaurant = Restaurant.query.get(restaurant_id)

    if not restaurant:
        flash("Restaurant not found.")
        return redirect(f'/{g.user.id}')

    favorite = Favorites.query.filter_by(user_id=g.user.id, restaurant_id=restaurant_id).first()

    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        flash("Removed from favorites.")
    else:
        new_favorite = Favorites(user_id=g.user.id, restaurant_id=restaurant_id)
        db.session.add(new_favorite)
        db.session.commit()
        flash("Added to favorites.")

    # Redirect back to the search page with the search term
    place = request.form.get("place")
    return redirect(url_for('show_search_restaurants', user_id=g.user.id, place=place))


@app.route('/add_wishlist/<int:restaurant_id>', methods=["POST"])
def toggle_wishlist(restaurant_id):
    if not g.user:
        flash("Access unauthorized.")
        return redirect("/")

    restaurant = Restaurant.query.get(restaurant_id)

    if not restaurant:
        flash("Restaurant not found.")
        return redirect(f'/{g.user.id}')

    wishlist = WishlistRestaurants.query.filter_by(user_id=g.user.id, restaurant_id=restaurant_id).first()

    if wishlist:
        db.session.delete(wishlist)
        db.session.commit()
        flash("Removed from wishlist.")
    else:
        new_wishlist = WishlistRestaurants(user_id=g.user.id, restaurant_id=restaurant_id)
        db.session.add(new_wishlist)
        db.session.commit()
        flash("Added to wishlists.")

    # Redirect back to the search page with the search term
    place = request.form.get("place")
    return redirect(url_for('show_search_restaurants', user_id=g.user.id, place=place))


@app.route('/add_visited/<int:restaurant_id>', methods=["POST"])
def toggle_visited(restaurant_id):
    if not g.user:
        flash("Access unauthorized.")
        return redirect("/")

    restaurant = Restaurant.query.get(restaurant_id)

    if not restaurant:
        flash("Restaurant not found.")
        return redirect(f'/{g.user.id}')

    visited = VisitedRestaurants.query.filter_by(user_id=g.user.id, restaurant_id=restaurant_id).first()

    if visited:
        db.session.delete(visited)
        db.session.commit()
        flash("Removed from visited.")
    else:
        new_visited = VisitedRestaurants(user_id=g.user.id, restaurant_id=restaurant_id)
        db.session.add(new_visited)
        db.session.commit()
        flash("Added to wishlists.")

    # Redirect back to the search page with the search term
    place = request.form.get("place")
    return redirect(url_for('show_search_restaurants', user_id=g.user.id, place=place))


# Delete from wishlist, favorites and visited restaurants

@app.route('/delete_visited/<int:restaurant_id>', methods=["POST"])
def delete_visited(restaurant_id):
    if not g.user:
        flash("Access unauthorized.")
        return redirect("/")

    restaurant = Restaurant.query.get(restaurant_id)

    if not restaurant:
        flash("Restaurant not found.")
        return redirect(f'/{g.user.id}')

    visited = VisitedRestaurants.query.filter_by(user_id=g.user.id, restaurant_id=restaurant_id).first()

    if visited:
        db.session.delete(visited)
        db.session.commit()
        flash("Removed from visited.")
    return redirect(f'/my_lists/{g.user.id}')


@app.route('/delete_wishlist/<int:restaurant_id>', methods=["POST"])
def delete_wishlist(restaurant_id):
    if not g.user:
        flash("Access unauthorized.")
        return redirect("/")

    restaurant = Restaurant.query.get(restaurant_id)

    if not restaurant:
        flash("Restaurant not found.")
        return redirect(f'/{g.user.id}')

    wishlist = WishlistRestaurants.query.filter_by(user_id=g.user.id, restaurant_id=restaurant_id).first()

    if wishlist:
        db.session.delete(wishlist)
        db.session.commit()
        flash("Removed from wishlist.")
    return redirect(f'/my_lists/{g.user.id}')


@app.route('/delete_favorite/<int:restaurant_id>', methods=["POST"])
def delete_favorite(restaurant_id):
    if not g.user:
        flash("Access unauthorized.")
        return redirect("/")

    restaurant = Restaurant.query.get(restaurant_id)

    if not restaurant:
        flash("Restaurant not found.")
        return redirect(f'/{g.user.id}')

    favorite = Favorites.query.filter_by(user_id=g.user.id, restaurant_id=restaurant_id).first()

    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        flash("Removed from favorites.")
    return redirect(f'/my_lists/{g.user.id}')



# Show all user's lists
@app.route('/my_lists/<int:user_id>')
def show_my_lists(user_id):
    """Show user's lists of favorite, wishlisted and visited restaurants"""
    user = User.query.get_or_404(user_id)

    favorites = Favorites.query.filter_by(user_id=user.id).all()
    wishlisted = WishlistRestaurants.query.filter_by(user_id=user.id).all()
    visited = VisitedRestaurants.query.filter_by(user_id=user.id).all()

    review_form = ReviewForm()

    visited_with_reviews = [(visit, Review.query.filter_by(user_id=user.id, restaurant_id=visit.restaurant_id).all()) for visit in visited]
    
    return render_template("page_my_lists.html", user = user, favorites = favorites, visited = visited, wishlisted = wishlisted, visited_with_reviews=visited_with_reviews, review_form = review_form)


# Show all the restaurants suggested to user
@app.route('/my_restaurants/<int:user_id>')
def show_my_restaurants(user_id):
    """Show the list of the restaurants close to the user based on their location"""

    user = User.query.get_or_404(user_id)

    place = user.location
    suggested_restaurants = fetch_restaurants(place, API_KEY)

    suggested_restaurants_list = []

    for restaurant in suggested_restaurants:
        name = restaurant.get("name")
        address = restaurant.get("formatted_address")
        photos = restaurant.get("photos")
        restaurant = save_restaurant_to_db(name, address, photos, API_KEY)

    names = [restaurant.get("name") for restaurant in suggested_restaurants]

    suggestions = Restaurant.query.filter(Restaurant.name.in_(names)).all()

    for restaurant in suggestions:
        sugg_restaurant = UserRestaurants.query.filter_by(restaurant_id = restaurant.id).first()

        if not sugg_restaurant:
            new_suggestion = UserRestaurants(user_id = user.id, restaurant_id = restaurant.id)
            db.session.add(new_suggestion)
            db.session.commit()
            suggested_restaurants_list.append(new_suggestion)
        else:
            suggested_restaurants_list.append(sugg_restaurant)

    my_places = suggested_restaurants_list

    return render_template("page_my_restaurants.html", user = user, my_places = my_places)    


@app.route('/search_restaurant/<int:user_id>', methods=["GET", "POST"])
def show_search_restaurants(user_id):
    """Show a search bar and the search result"""
    user = User.query.get_or_404(user_id)
    restaurants = []
    place = request.args.get("place") or request.form.get("place")

    if request.method == "POST":
        # If the form is submitted via POST, update the place variable
        place = request.form.get("place")

    if place:
        # Fetch restaurants only if place is not empty
        restaurants_data = fetch_restaurants(place, API_KEY)

        wishlisted_ids = {r.id for r in user.wishlist_restaurants}
        visited_ids = {r.id for r in user.visited_restaurants}
        favorite_ids = {r.id for r in user.favorites_restaurants}

        for restaurant_data in restaurants_data:
            name = restaurant_data.get("name")
            address = restaurant_data.get("formatted_address")
            photos = restaurant_data.get("photos")
            restaurant = save_restaurant_to_db(name, address, photos, API_KEY)

            # Add custom attributes to the restaurant object
            restaurant.is_wishlisted = restaurant.id in wishlisted_ids
            restaurant.is_visited = restaurant.id in visited_ids
            restaurant.is_favorite = restaurant.id in favorite_ids

            restaurants.append(restaurant)

    return render_template("page_search_restaurant.html", user=user, restaurants=restaurants, place=place)



# Review routes
@app.route('/my_reviews/<int:user_id>')
def show_my_reviews(user_id):
    """Show user's reviews on restaurants"""
    user = User.query.get_or_404(user_id)

    reviews = Review.query.filter_by(user_id=g.user.id).all()

    review_form = ReviewForm()

    return render_template('page_my_reviews.html', user = user, reviews = reviews, review_form = review_form)


@app.route('/add_review/<int:restaurant_id>', methods=["GET", "POST"])
def add_review(restaurant_id): 
    """Add a review if a restaurant is in the visited restaurants list"""
    if not g.user:
        flash("Access unauthorized.")
        return redirect("/")
    
    restaurant = Restaurant.query.get_or_404(restaurant_id)

    if not restaurant:
        flash("Restaurant not found.")
        return redirect(f'/{g.user.id}')

    # Check if the restaurant has been visited by the user
    visited = VisitedRestaurants.query.filter_by(user_id=g.user.id, restaurant_id=restaurant_id).first()

    review_form = ReviewForm()

    if visited:
        if review_form.validate_on_submit():
            content = review_form.text.data
            review = Review(
                user_id=g.user.id,
                restaurant_id=restaurant_id,
                content=content
            )
            db.session.add(review)
            db.session.commit()
            flash("Review added successfully!")
            return redirect(f'/my_lists/{g.user.id}')

    return render_template("page_user_profile.html",  visited=visited, review_form=review_form)


@app.route('/edit_review/<int:review_id>', methods=["GET", "POST"])
def edit_review(review_id):
    if not g.user:
        flash("Access unauthorized.")
        return redirect("/")
    
   # Check if the review exists and if it belongs to the current user
    review = Review.query.filter_by(id=review_id, user_id=g.user.id).first()

    review_form = ReviewForm(obj=review)

    if not review:
        flash("Review not found.")
        return redirect(f'/my_lists/{g.user.id}')
    

    if review_form.validate_on_submit():
        review.content = review_form.text.data
        db.session.commit()
        flash("Review updated successfully!")
        return redirect(f'/my_lists/{g.user.id}')
    
    return render_template("page_my_lists.html", review_form=review_form)


@app.route('/delete_review/<int:review_id>', methods=["GET", "POST"])
def delete_review(review_id):
    """Delete a review if a restaurant is in the visited restaurants list"""
    if not g.user:
        flash("Access unauthorized.")
        return redirect("/")

    # Check if the restaurant has a review
    review = Review.query.filter_by(id = review_id).first()

    if not review:
        flash("Review not found.")
        return redirect(f'/my_lists/{g.user.id}')

    if review:
        db.session.delete(review)
        db.session.commit()
        flash("Removed the review.")
        return redirect(f'/my_lists/{g.user.id}')


# Edit/update user profile
@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user_profile(user_id):
    """Update profile for current user."""

    if not g.user or g.user.id != user_id :
        flash("Access unauthorized.")
        return redirect("/")
    
    user = User.query.get_or_404(user_id)

    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        if not bcrypt.check_password_hash(user.password, form.password.data):
            flash("Incorrect password. Profile update failed")
            return redirect("/")
        
        user.username=form.username.data
        user.email=form.email.data
        user.image_url=form.image_url.data
        user.bio = form.bio.data
        user.location = form.location.data
        db.session.commit()
        flash("Profile updated successfully!")
        return redirect(f'/{g.user.id}')

    return render_template('page_edit_user_profile.html', user=user, user_id=user.id, form=form)

# Completely delete user's profile
@app.route('/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()
    flash("Profile deleted successfully.")

    return redirect("/signup")

##############################################################################
# Turn off all caching in Flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req




