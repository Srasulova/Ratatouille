from flask import Flask, render_template, request, flash, redirect, session, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
import os
import requests

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{app.root_path}/TwitterClone.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)


# headers = {
# 	"X-RapidAPI-Key": "185e7691e2mshec908b70aabf7cdp11a97cjsn86e7c3c53f7f",
# 	"X-RapidAPI-Host": "restaurants-near-me-usa.p.rapidapi.com"
# }

# url = f"https://restaurants-near-me-usa.p.rapidapi.com/restaurants/location/zipcode/{zipcode}/0"
# response = requests.get(url, headers=headers)

API_KEY = "AIzaSyDQaQ4Zi8e-5YKSb_9VJvkKns3uYoq435g"

@app.route('/', methods=["GET", "POST"])
def homepage():
    """Show homepage"""
    if request.method == "POST":
        place = request.form.get("place")
        print(place)

        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=restaurants+in+{place}&key={API_KEY}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            restaurants = data.get("results", [])
            # print(len(restaurants))
            # print(data)
        else:
            data = None
            print(f"Error: {response.status_code}")
        
        
        return render_template("base.html", restaurants=restaurants)
    
    return render_template("base.html")