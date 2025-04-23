"""
Database initialization script for İrrigo project.
This script creates all the necessary tables in the database based on the models.
Run this script once to set up the database structure.
"""
import os
import sys
from dotenv import load_dotenv
from flask import Flask
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables from .env file
load_dotenv()

def init_database():
    """Initialize the database by creating all tables defined in the models."""
    try:
        # Print the database URL (with password masked)
        db_url = os.environ.get('DATABASE_URL', '')
        masked_url = db_url.replace(db_url.split('@')[0].split('://')[-1], 'username:****')
        print(f"Connecting to database: {masked_url}")
        
        # Create a minimal Flask application
        app = Flask(__name__)
        
        # Configure the database
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Import the database and models here to avoid circular imports
        from app.database import db
        from app.models import User, SensorData, Device
        
        # Initialize the database with the app
        db.init_app(app)
        
        # Create the database tables within the application context
        with app.app_context():
            print("Creating database tables...")
            
            # Create the database if it doesn't exist
            try:
                db.engine.connect()
                print("Connected to database successfully")
            except SQLAlchemyError as e:
                print(f"Error connecting to database: {str(e)}")
                # Check if the error is about database not existing
                if "Unknown database" in str(e):
                    print("Database does not exist. Please create it first using MySQL commands:")
                    print("CREATE DATABASE irrigodb;")
                return
            
            # Create all tables
            db.create_all()
            print("Database tables created successfully!")
            
            # Print out the created tables for verification
            tables = db.engine.table_names()
            print("Created tables:", tables)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_database()
