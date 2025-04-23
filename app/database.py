from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy extension
# This object will be used to interact with the database
db = SQLAlchemy()

def init_app(app):
    """Initialize the database extension with the Flask app."""
    db.init_app(app)
