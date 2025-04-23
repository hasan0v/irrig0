"""
Simple database initialization script for İrrigo project.
This script connects directly to the MySQL database and creates all necessary tables.
"""
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the database URL from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')
print(f"Database URL (masked): {DATABASE_URL.split('@')[0].split('://')[0]}://*****@{DATABASE_URL.split('@')[1]}")

# Create engine and session
engine = create_engine(DATABASE_URL)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

# Define the models directly here to avoid import issues
class User(Base):
    """Model for the users table"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class SensorData(Base):
    """Model for the sensordata table"""
    __tablename__ = 'sensordata'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.TIMESTAMP(timezone=True), nullable=False, server_default=db.func.now(), index=True)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    uv_intensity = db.Column(db.Float)
    rainfall = db.Column(db.Float)
    soil_moisture_level = db.Column(db.Float)
    ph_level = db.Column(db.Float)
    tank_water_volume = db.Column(db.Float)
    water_pressure = db.Column(db.Float)

class Device(Base):
    """Model for controllable devices"""
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)
    control_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='UNKNOWN')
    last_status_update = db.Column(db.TIMESTAMP(timezone=True))
    is_enabled = db.Column(db.Boolean, default=True)

def init_db():
    """Initialize the database"""
    try:
        # Try to connect to the database
        connection = engine.connect()
        print("Connected to database successfully!")
        connection.close()
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
        
        # Check tables
        inspector = inspect(engine)
        print(f"Created tables: {inspector.get_table_names()}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        
        # Handle case where database doesn't exist
        if "Unknown database" in str(e):
            print("\nThe database does not exist. You need to create it first.")
            print("Run these commands in MySQL:")
            print(f"CREATE DATABASE {DATABASE_URL.split('/')[-1]};")
            print(f"USE {DATABASE_URL.split('/')[-1]};")
            
        elif "Access denied" in str(e):
            print("\nAccess denied. Check your username and password in the .env file.")
            
        elif "Can't connect to MySQL server" in str(e):
            print("\nCannot connect to MySQL server. Make sure the server is running and accessible.")
        
        else:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # Import db here to avoid circular imports
    from sqlalchemy import Column, Integer, String, Float, Boolean, TIMESTAMP, func
    db = Base.metadata
    
    print("Initializing database...")
    init_db()
