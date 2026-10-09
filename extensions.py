from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


# Shared database object
db = SQLAlchemy()


# Flask-Login manager
login_manager = LoginManager()