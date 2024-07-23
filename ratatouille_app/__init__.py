from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from ratatouille_app.utils.helpers import add_header, add_user_to_g
from ratatouille_app.routes.home import home_bp
from ratatouille_app.routes.restaurants import restaurants_bp
from ratatouille_app.routes.reviews import reviews_bp
from ratatouille_app.routes.user import user_bp
from ratatouille_app.models import connect_db


# Initialize extensions

toolbar = DebugToolbarExtension()



def create_app(config_class='ratatouille_app.config.Config'):
    app = Flask(__name__)
    # app.config.from_object('ratatouille_app.config.Config')
    app.config.from_object(config_class)

    toolbar.init_app(app)

    connect_db(app)

    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(restaurants_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(user_bp)

    app.before_request(add_user_to_g)
    app.after_request(add_header)


    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html'), 500

    return app

