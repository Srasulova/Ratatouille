from flask import render_template, redirect, flash, g, url_for
import ratatouille_app.config
from ratatouille_app.forms.forms import UserAddForm, LoginForm, UserEditForm, ReviewForm
from ratatouille_app.utils.helpers import fetch_restaurants, save_restaurant_to_db, do_logout, get_user_lists, get_user, check_user_authentication
from ratatouille_app.models.user import User, UserRestaurants
from ratatouille_app.models.restaurant import Restaurant, VisitedRestaurants, WishlistRestaurants, Favorites
from ratatouille_app.models.review import Review
from sqlalchemy.exc import IntegrityError
import ratatouille_app
from ...config import Config
from ratatouille_app.routes.user import user_bp
from ratatouille_app.models import db, bcrypt

config = Config()

@user_bp.route('/<int:user_id>', methods=['GET', 'POST'])
def users_show(user_id):
    """Show user profile."""

    # Check if user is logged in
    if g.user is None:
        flash("You must be logged in to view this page.")
        return redirect(url_for('home_bp.user_login'))  # Redirect to login page if not authenticated
    
    if g.user.id != user_id:
        flash("You are not authorized to view this page.")
        return redirect("/")

    user = get_user(user_id)
    review_form = ReviewForm()
    user_edit_form = UserEditForm(obj=user)

    if user_edit_form.validate_on_submit():
        user.location = user_edit_form.location.data.strip()
        try:
            db.session.commit()
            flash("Location submitted successfully!")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating location: {str(e)}")

        return redirect("/")

    favorites, wishlisted, visited, visited_with_reviews = get_user_lists(user.id)

    return render_template("page_user_profile.html", user=user, favorites=favorites, wishlisted=wishlisted, visited=visited, review_form=review_form,
                           visited_with_reviews=visited_with_reviews, user_edit_form=user_edit_form)


@user_bp.route('/my_lists/<int:user_id>')
def show_my_lists(user_id):
    """Show user's lists of favorite, wishlisted and visited restaurants"""
    if g.user.id != user_id:
        flash("You are not authorized to view this page.")
        return redirect("/")
    
    user = get_user(user_id)

    favorites, wishlisted, visited, visited_with_reviews = get_user_lists(user.id)

    review_form = ReviewForm()

    return render_template("page_my_lists.html", user=user, favorites=favorites, visited=visited, wishlisted=wishlisted, visited_with_reviews=visited_with_reviews, review_form=review_form)


@user_bp.route('/my_restaurants/<int:user_id>')
def show_my_restaurants(user_id):
    """Show the list of the restaurants close to the user based on their location"""
    if g.user.id != user_id:
        flash("You are not authorized to view this page.")
        return redirect("/")
    

    user = get_user(user_id)

    place = user.location
    suggested_restaurants = fetch_restaurants(place, config.API_KEY)

    suggested_restaurants_list = []

    for restaurant in suggested_restaurants:
        name = restaurant.get("name")
        address = restaurant.get("formatted_address")
        photos = restaurant.get("photos")
        restaurant = save_restaurant_to_db(name, address, photos, config.API_KEY)

    names = [restaurant.get("name") for restaurant in suggested_restaurants]

    suggestions = Restaurant.query.filter(Restaurant.name.in_(names)).all()

    for restaurant in suggestions:
        sugg_restaurant = UserRestaurants.query.filter_by(restaurant_id=restaurant.id).first()

        if not sugg_restaurant:
            new_suggestion = UserRestaurants(user_id=user.id, restaurant_id=restaurant.id)
            db.session.add(new_suggestion)
            try:
                db.session.commit()
                suggested_restaurants_list.append(new_suggestion)
            except Exception as e:
                db.session.rollback()
                flash(f"Error saving restaurant: {str(e)}")
        else:
            suggested_restaurants_list.append(sugg_restaurant)

    my_places = suggested_restaurants_list

    return render_template("page_my_restaurants.html", user=user, my_places=my_places)


@user_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user_profile(user_id):
    """Update profile for current user."""

    if not g.user or g.user.id != user_id:
        flash("Access unauthorized.")
        return redirect("/")

    user = get_user(user_id)

    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        if not bcrypt.check_password_hash(user.password, form.password.data):
            flash("Incorrect password. Profile update failed")
            return redirect("/")

        try:
            user.username = form.username.data.strip()
            user.email = form.email.data.strip()
            user.image_url = form.image_url.data.strip()
            user.bio = form.bio.data.strip()
            user.location = form.location.data.strip()
            db.session.commit()
            flash("Profile updated successfully!")
            return redirect(f'/{g.user.id}')
        except IntegrityError:
            db.session.rollback()
            flash("This username already exists! So many foodies think alike. Try another one!")
            return render_template('page_edit_user_profile.html', form=form)
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {str(e)}")

    return render_template('page_edit_user_profile.html', user=user, user_id=user.id, form=form)


@user_bp.route('/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    auth_check = check_user_authentication()
    if auth_check:
        return auth_check

    do_logout()

    try:
        db.session.delete(g.user)
        db.session.commit()
        flash("Profile deleted successfully.")
    except Exception as e:
            db.session.rollback()
            flash(f"Error deleting profile: {str(e)}")

    return redirect("/signup")
