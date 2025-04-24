import os
from dotenv import load_dotenv
from flask import Flask
from app.database import db, init_app as init_db_app
# Import all models to ensure they are registered with SQLAlchemy metadata
from app.models import User, SensorData, Device, Alarm, AlarmRule

# Load environment variables from .env file
load_dotenv()

# Create a minimal Flask app instance for context
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///instance/irrigodb.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
init_db_app(app)

def initialize_database():
    """Creates all database tables based on the models."""
    with app.app_context():
        print("Attempting to create database tables...")
        try:
            # Ensure the instance folder exists for SQLite
            if 'sqlite:///' in DATABASE_URL:
                 instance_path = os.path.join(app.instance_path)
                 if not os.path.exists(instance_path):
                    os.makedirs(instance_path)
                    print(f"Created instance folder at {instance_path}")
            
            db.create_all()
            print("Database tables created successfully (or already exist).")
            # Optionally, check if tables exist now
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Tables found: {tables}")
            if 'alarms' in tables and 'alarm_rules' in tables:
                 print("Verified: 'alarms' and 'alarm_rules' tables exist.")
            else:
                 print("Warning: Could not verify creation of 'alarms' or 'alarm_rules' tables.")

        except Exception as e:
            print(f"An error occurred during table creation: {e}")

if __name__ == '__main__':
    initialize_database()
