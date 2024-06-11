"""User model tests."""

# run these tests like:
#
#python -m unittest test_user_model.py

import os
from unittest import TestCase

from models import db, User, Review, Restaurant, VisitedRestaurants, WishlistRestaurants, Favorites

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = f"sqlite:///Ratatouille-test.db"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables 

with app.app_context():
   db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():

            User.query.delete()

            self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        with app.app_context():

            u = User(
                email="aliya@test.com",
                username="Aliya",
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
            user = User.signup("testuser1", "testuser1@test.com", "testpassword", "testimageurl")
            db.session.commit()
    
            authenticated_user = User.authenticate("testuser1", "testpassword")
    
            self.assertEqual(authenticated_user, user)

    def test_user_authenticate_invalid_username(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""
        with app.app_context():
            authenticated_user = User.authenticate("invalidusername1", "testpassword")

            self.assertFalse(authenticated_user)


    def test_user_authenticate_invalid_password(self):
        """Does User.authenticate fail to return a user when the password is invalid?"""
        with app.app_context():
            authenticated_user = User.authenticate("testuser1", "invalidpassword")
    
            self.assertFalse(authenticated_user)