from flask import Flask, render_template, request, flash, redirect, session, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
import os
import requests
from models import db, connect_db, User, Restaurant, VisitedRestaurants, WishlistRestaurants, Favorites, Review
from sqlalchemy.exc import IntegrityError
from forms import UserAddForm, UserEditForm, LoginForm, ReviewForm
from flask_bcrypt import Bcrypt
# from flask_migrate import Migrate

bcrypt = Bcrypt()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{app.root_path}/Ratatouille.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)


CURR_USER_KEY = 'curr_user'
API_KEY = "AIzaSyDQaQ4Zi8e-5YKSb_9VJvkKns3uYoq435g"

# migrate = Migrate(app, db)

with app.app_context():
   connect_db(app)

with app.app_context():
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
    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user"""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


#Homepage route

@app.route('/', methods = ['GET', 'POST'])
def homepage():
    """Show homepage and display the signup or login form based on user interaction"""  
    if not g.user:
        return render_template('home_anon.html')
    return render_template("home.html")

    
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(username = form.username.data, password = form.password.data, email= form.email.data, image_url= form.image_url.data or User.image_url.default.arg)
            db.session.commit()
        except IntegrityError:
            flash("This username already exists! So many foodies think alike. Try another one!")
            return render_template('signup.html', form=form)
        do_login(user)

        return redirect('/home')
    return render_template('signup.html', form=form)


@app.route('/login', methods = ['GET', 'POST'])
def user_login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!")
            return redirect('/home')
        else:
            flash("Invalid credentials!")
            return render_template('login.html', form = form)

    return render_template('login.html', form = form)
    


@app.route('/logout')
def logout():
    """Handle logout of user."""

    session.clear()
    flash("You have been logged out")
    return redirect("/")


@app.route('/home')
def user_home():
    return render_template('home.html')


    





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


#   if request.method == "POST":
#         place = request.form.get("place")
#         print(place)

#         url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=restaurants+in+{place}&key={API_KEY}"
#         response = requests.get(url)

#         if response.status_code == 200:
#             data = response.json()
#             restaurants = data.get("results", [])
#             # print(len(restaurants))
#             # print(data)
#         else:
#             data = None
#             print(f"Error: {response.status_code}")
        
        
#         return render_template("base.html", restaurants=restaurants)





# headers = {
# 	"X-RapidAPI-Key": "185e7691e2mshec908b70aabf7cdp11a97cjsn86e7c3c53f7f",
# 	"X-RapidAPI-Host": "restaurants-near-me-usa.p.rapidapi.com"
# }

# url = f"https://restaurants-near-me-usa.p.rapidapi.com/restaurants/location/zipcode/{zipcode}/0"
# response = requests.get(url, headers=headers)