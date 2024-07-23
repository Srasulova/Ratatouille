import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', "it's a secret")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.dirname(os.path.abspath(__file__))}/Ratatouille.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    API_KEY = os.getenv("API_KEY")
    DEFAULT_IMAGE_URL = "/static/images/default-pic.jpg"
    CURR_USER_KEY = "curr_user"


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.dirname(os.path.abspath(__file__))}/Ratatouille-test.db"
    WTF_CSRF_ENABLED = False