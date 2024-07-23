from flask import render_template, redirect, flash, g, request, url_for
from ratatouille_app.forms.forms import ReviewForm
from ratatouille_app.utils.helpers import fetch_restaurants, save_restaurant_to_db, toggle_list, delete_from_list, get_restaurant, check_user_authentication, get_user
from ratatouille_app.models.user import User
from ratatouille_app.models.restaurant import Restaurant, VisitedRestaurants, WishlistRestaurants, Favorites
from ratatouille_app.routes.restaurants import restaurants_bp
from ...config import Config
# from ...config import API_KEY



config = Config()


@restaurants_bp.route('/search_restaurant', methods = ['GET', 'POST'])
def show_search_restaurants():
    """Show a search bar and the search result"""
    user = get_user(g.user.id)
    restaurants = []
    place = request.args.get("place") or request.form.get("place")

    if request.method == "POST":
        # If the form is submitted via POST, update the place variable
        place = request.form.get("place")

    if place:
        # Fetch restaurants only if place is not empty
        restaurants_data = fetch_restaurants(place, config.API_KEY)

        wishlisted_ids = {r.id for r in user.wishlist_restaurants}
        visited_ids = {r.id for r in user.visited_restaurants}
        favorite_ids = {r.id for r in user.favorites_restaurants}

        for restaurant_data in restaurants_data:
            name = restaurant_data.get("name")
            address = restaurant_data.get("formatted_address")
            photos = restaurant_data.get("photos")
            restaurant = save_restaurant_to_db(name, address, photos, config.API_KEY)

            # Add custom attributes to the restaurant object
            restaurant.is_wishlisted = restaurant.id in wishlisted_ids
            restaurant.is_visited = restaurant.id in visited_ids
            restaurant.is_favorite = restaurant.id in favorite_ids

            restaurants.append(restaurant)

    return render_template("page_search_restaurant.html", user=user, restaurants=restaurants, place=place)


@restaurants_bp.route('/add_favorite/<int:restaurant_id>', methods = ['POST'])
def toggle_favorite(restaurant_id):
    """Add or remove a restaurant from user's favorites list"""
    auth_check = check_user_authentication()
    if auth_check:
        return auth_check
    
    restaurant = get_restaurant(restaurant_id)
    if not restaurant:
        return restaurant #This will return the redirect response
    
    toggle_list(Favorites, g.user.id, restaurant_id, 'Favorites')

    # Redirect back to the search page with the search term
    place = request.form.get('place')
    return redirect(url_for('restaurants_bp.show_search_restaurants', place=place))


@restaurants_bp.route('/add_wishlist/<int:restaurant_id>', methods=["POST"])
def toggle_wishlist(restaurant_id):
    """Add or remove a restaurant from user's wish list"""
    auth_check = check_user_authentication()
    if auth_check:
        return auth_check

    restaurant = get_restaurant(restaurant_id)
    if not restaurant:
        return restaurant #This will return the redirect response

    toggle_list(WishlistRestaurants, g.user.id, restaurant_id, 'Wishlists')

    # Redirect back to the search page with the search term
    place = request.form.get("place")
    return redirect(url_for('restaurants_bp.show_search_restaurants', place=place))




@restaurants_bp.route('/add_visited/<int:restaurant_id>', methods=["POST"])
def toggle_visited(restaurant_id):
    """Add or remove a restaurant from user's visited list"""
    auth_check = check_user_authentication()
    if auth_check:
        return auth_check

    restaurant = get_restaurant(restaurant_id)
    if not restaurant:
        return restaurant #This will return the redirect response

    toggle_list(VisitedRestaurants, g.user.id, restaurant_id, 'Visited restaurants')

    # Redirect back to the search page with the search term
    place = request.form.get("place")
    return redirect(url_for('restaurants_bp.show_search_restaurants', place=place))


@restaurants_bp.route('/delete_visited/<int:restaurant_id>', methods=["POST"])
def delete_visited(restaurant_id):
    """Remove a restaurant from user's visited list"""
    auth_check = check_user_authentication()
    if auth_check:
        return auth_check

    restaurant = get_restaurant(restaurant_id)
    if not restaurant:
        return restaurant #This will return the redirect response

    return delete_from_list(VisitedRestaurants, g.user.id, restaurant_id, 'visited')

@restaurants_bp.route('/delete_wishlist/<int:restaurant_id>', methods=["POST"])
def delete_wishlist(restaurant_id):
    """Remove a restaurant from user's wish list"""
    auth_check = check_user_authentication()
    if auth_check:
        return auth_check

    restaurant = get_restaurant(restaurant_id)
    if not restaurant:
        return restaurant #This will return the redirect response

    return delete_from_list(WishlistRestaurants, g.user.id, restaurant_id, 'wishlist')

@restaurants_bp.route('/delete_favorite/<int:restaurant_id>', methods=["POST"])
def delete_favorite(restaurant_id):
    """Remove a restaurant from user's favorites list"""
    if not g.user:
        flash("Access unauthorized.")
        return redirect("/")

    restaurant = get_restaurant(restaurant_id)
    if not restaurant:
        return restaurant #This will return the redirect response

    return delete_from_list(Favorites, g.user.id, restaurant_id, 'favorites')