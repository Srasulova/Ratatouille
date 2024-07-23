from flask import Blueprint

restaurants_bp = Blueprint('restaurants_bp', __name__)

# Import routes to ensure they are registered with the blueprint
from ratatouille_app.routes.restaurants import routes