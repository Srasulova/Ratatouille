"""User model tests."""

# run these tests like:
#python -m unittest test_user_model.py

import os
from unittest import TestCase


from ratatouille_app.models.restaurant import Restaurant, WishlistRestaurants, Favorites, VisitedRestaurants
from ratatouille_app.models.user import User, UserRestaurants
from ratatouille_app.models.review import Review
from ratatouille_app.models import db



# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database


# Now we can import app

# from ratatouille_app.app import app
from ratatouille_app.config import TestConfig
from ratatouille_app import create_app

config = TestConfig()

app = create_app(TestConfig)

# Create our tables 

with app.app_context():
   db.create_all()


app.config['WTF_CSRF_ENABLED'] = False

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            print("Test database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
            db.drop_all()  # Drop all tables to ensure a clean state
            db.create_all()  # Create tables before each test
            self.client = app.test_client()
            print("Database setup complete.")

    
    def tearDown(self):
        """Clean up after each test."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
            print("Database cleanup complete.")

    def test_user_model(self):
        """Does basic model work?"""

        with app.app_context():

            u = User(
                email="test123@test.com",
                username="test123",
                password="HASHED_PASSWORD"
        )

            db.session.add(u)
            db.session.commit()

            # User should have no messages & no followers
            self.assertEqual(len(u.reviews), 0)
            self.assertEqual(len(u.visited_restaurants), 0)

            #Does the repr method work as expected?
            expected_repr = f"<User #{u.id}: {u.username}, {u.email}>"
            self.assertEqual(repr(u), expected_repr)

    
    def test_user_authenticate_valid_credentials(self):
        """Does User.authenticate successfully return a user when given valid credentials?"""
        with app.app_context():
            # Create a user with valid credentials
            user = User.signup("testuser12", "testuser12@test.com", "testpassword", "testimageurl")
            db.session.commit()
    
            authenticated_user = User.authenticate("testuser12", "testpassword")
    
            self.assertEqual(authenticated_user, user)

    def test_user_authenticate_invalid_username(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""
        with app.app_context():
            authenticated_user = User.authenticate("invalidusername1", "testpassword")

            self.assertFalse(authenticated_user)


    def test_user_authenticate_invalid_password(self):
        """Does User.authenticate fail to return a user when the password is invalid?"""
        with app.app_context():
            authenticated_user = User.authenticate("testuser12", "invalidpassword")
    
            self.assertFalse(authenticated_user)