from flask import render_template, redirect, flash, g, request
from ratatouille_app.utils.helpers import get_user, get_restaurant, check_user_authentication, get_review_or_redirect
from ratatouille_app.models.user import User
from ratatouille_app.models.review import Review
from ratatouille_app.models.restaurant import Restaurant, VisitedRestaurants
from ratatouille_app.routes.reviews import reviews_bp
from ratatouille_app.forms.forms import ReviewForm
from ratatouille_app.models import db


@reviews_bp.route('/my_reviews/<int:user_id>')
def show_my_reviews(user_id):
    """Show user's reviews on restaurants"""

    if g.user.id != user_id:
        flash("You are not authorized to view this page.")
        return redirect("/")
    
    user = get_user(user_id)

    reviews = Review.query.filter_by(user_id=user_id).all()

    review_form = ReviewForm()

    return render_template('page_my_reviews.html', user = user, reviews = reviews, review_form = review_form)


@reviews_bp.route('/add_review/<int:restaurant_id>', methods=["GET", "POST"])
def add_review(restaurant_id):
    """Add a review if a restaurant is in the visited restaurants list"""
    auth_check = check_user_authentication()
    if auth_check:
        return auth_check

    restaurant = get_restaurant(restaurant_id)
    if not restaurant:
        return restaurant  # This will return the redirect response

    # Check if the restaurant has been visited by the user
    visited = VisitedRestaurants.query.filter_by(user_id=g.user.id, restaurant_id=restaurant_id).first()
    review_form = ReviewForm()

    if visited:
        if review_form.validate_on_submit():
            content = review_form.text.data.strip()
            review = Review(
                user_id=g.user.id,
                restaurant_id=restaurant_id,
                content=content
            )
            db.session.add(review)
            db.session.commit()
            flash("Review added successfully!")
            return redirect(f'/my_lists/{g.user.id}')

    return render_template("page_user_profile.html", visited=visited, review_form=review_form)


@reviews_bp.route('/edit_review/<int:review_id>', methods=["GET", "POST"])
def edit_review(review_id):
    auth_check = check_user_authentication()
    if auth_check:
        return auth_check

    review = get_review_or_redirect(review_id, "edit")

    review_form = ReviewForm(obj=review)

    if review_form.validate_on_submit():
        review.content = review_form.text.data.strip()
        db.session.commit()
        flash("Review updated successfully!")
        return redirect(f'/my_lists/{g.user.id}')

    return render_template("page_my_lists.html", review_form=review_form)

@reviews_bp.route('/delete_review/<int:review_id>', methods=["POST"])
def delete_review(review_id):
    """Delete a review if a restaurant is in the visited restaurants list"""
    auth_check = check_user_authentication()
    if auth_check:
        return auth_check

    review = get_review_or_redirect(review_id, "delete")

    db.session.delete(review)
    db.session.commit()
    flash("Removed the review.")
    return redirect(f'/my_lists/{g.user.id}')