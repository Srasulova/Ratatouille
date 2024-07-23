from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, InputRequired


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[InputRequired('Username required!')])
    email = StringField('E-mail', validators=[DataRequired('Email required!'), Email()])
    password = PasswordField('Password', validators=[InputRequired('Password required!'), Length(min=6)])
    image_url = StringField('(Optional) Image URL')
 


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[InputRequired('Username required!')])
    password = PasswordField('Password', validators=[InputRequired('Password required!'), Length(min=6)])


class UserEditForm(FlaskForm):
    """Form for editing users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('Image URL')
    bio = TextAreaField('Bio')
    location = StringField('Enter your address or zipcode')


class ReviewForm(FlaskForm):
    """Form for adding/editing a review"""
    text = TextAreaField('Add review', validators=[DataRequired()])