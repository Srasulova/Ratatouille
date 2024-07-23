from flask import Blueprint, render_template, redirect, flash, g, session
from ratatouille_app.forms.forms import UserAddForm, LoginForm
from ratatouille_app.utils.helpers import add_user_to_g, do_login, do_logout
from ratatouille_app.models.user import User
from sqlalchemy.exc import IntegrityError
from ratatouille_app.routes.home import home_bp
from ratatouille_app.models import db


@home_bp.route('/')
def homepage():
    """Show homepage and display the signup or login form based on user interaction"""  

    if not g.user:
        return render_template('home_anon.html')
    return redirect(f'/{g.user.id}')

@home_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user signup."""
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username = form.username.data.strip(), 
                password = form.password.data.strip(), 
                email= form.email.data.strip(), 
                image_url= form.image_url.data.strip() or User.image_url.default.arg
                )
            db.session.commit()
        except IntegrityError:
            flash("This username already exists! So many foodies think alike. Try another one!")
            return render_template('signup.html', form=form)
        
        do_login(user)

        return redirect(f'/{user.id}')
    return render_template('signup.html', form=form)


@home_bp.route('/login', methods = ['GET', 'POST'])
def user_login():
    """Handle logging in user."""
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

    return render_template('/login.html', form = form)


@home_bp.route('/logout')
def logout():
    """Handle logout of user."""

    session.clear()
    flash("You have been logged out")
    return redirect("/")