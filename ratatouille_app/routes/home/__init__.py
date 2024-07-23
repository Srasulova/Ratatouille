from flask import Blueprint

# Define the blueprint object for the home package
home_bp = Blueprint('home_bp', __name__)

# Import routes to ensure they are registered with the blueprint
from ratatouille_app.routes.home import routes
