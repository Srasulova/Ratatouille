# from ratatouille_app import db
from datetime import datetime
from ratatouille_app.models import db

class MyDateTime(db.TypeDecorator):
    impl = db.DateTime

    def process_bind_param(self, value, dialect):
        if type(value) is str:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
        return value
    

class Review(db.Model):
    """User's reviews about restaurants"""

    __tablename__ = 'reviews' 

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade'),
        nullable = False
    )

    restaurant_id = db.Column(
        db.Integer,
        db.ForeignKey('restaurants.id', ondelete='cascade')
    )

    content = db.Column(
        db.Text,
        nullable = False
    )

    timestamp = db.Column(
        MyDateTime,
        nullable=False,
        default=datetime.now,
    )