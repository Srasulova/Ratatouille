from flask import Blueprint

user_bp = Blueprint('user_bp', __name__)

# Import routes to ensure they are registered with the blueprint
from ratatouille_app.routes.user import routes