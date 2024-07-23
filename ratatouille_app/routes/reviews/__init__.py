from flask import Blueprint

reviews_bp = Blueprint('reviews_bp', __name__)

# Import routes to ensure they are registered with the blueprint
from ratatouille_app.routes.reviews import routes
