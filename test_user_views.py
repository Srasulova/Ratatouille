"""User View tests."""

# run these tests like:
#python -m unittest test_user_views.py

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

# We don't have WTForms use CSRF at all

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""
    def setUp(self):
        with app.app_context():
            User.query.delete()

            self.testuser = User.signup(username="testuser",email="test@test.com", password="testuser", image_url=None)
            self.user1 = User.signup("user1", "user1@test.com", "password", None)
            self.user2 = User.signup("user2", "user2@test.com", "password", None)
            self.user3 = User.signup("user3", "user3@test.com", "password", None)
            self.user4 = User.signup("user4", "user4@test.com", "password", None)

            db.session.add(self.testuser)
            db.session.add(self.user1)
            db.session.add(self.user2)
            db.session.add(self.user3)
            db.session.add(self.user4)
            db.session.commit()

            self.client = app.test_client()

    
    def tearDown(self):

        with app.app_context():
            db.session.rollback()

    def test_user_profile_route(self):
        """Test if user profile route responds with the code status 200"""

        with app.app_context():
            testuser = User.query.filter_by(username="testuser").first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id

            resp = c.get(f'/{testuser.id}')
            self.assertEqual(resp.status_code, 200)

    
    def test_delete_user_route(self):
        """Test if delete user route responds with the code status 302"""

        with app.app_context():
            testuser = User.query.filter_by(username="testuser").first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser.id
            
            resp = c.post(f"/delete")
            self.assertEqual(resp.status_code, 302)
