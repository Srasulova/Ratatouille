import os
from unittest import TestCase
from ratatouille_app import create_app
from ratatouille_app.models import db
from ratatouille_app.models.user import User
from ratatouille_app.config import TestConfig

class UserRoutesIntegrationTestCase(TestCase):
    """Integration tests for user routes."""

    def setUp(self):
        """Set up test client, add sample data."""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self.setup_test_data()

    def tearDown(self):
        """Clean up any fouled transaction."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def setup_test_data(self):
        """Create test data."""
        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.add(self.testuser)
        db.session.commit()  # Ensure the user is committed to the session

        # Refresh the testuser to ensure it's bound to the session
        db.session.refresh(self.testuser)

    def test_user_profile_route(self):
        """Test user profile route responds correctly and renders the profile."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[TestConfig.CURR_USER_KEY] = self.testuser.id

            resp = c.get(f'/{self.testuser.id}')
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'testuser', resp.data)

    def test_delete_user_route(self):
        """Test user deletion route and verify the user is deleted."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[TestConfig.CURR_USER_KEY] = self.testuser.id

            resp = c.post('/delete')
            self.assertEqual(resp.status_code, 302)

            with self.app.app_context():
                user = User.query.get(self.testuser.id)
                self.assertIsNone(user)
