"""
MySQL Direct Connection Test and Table Creation
"""
import os
import sys
from dotenv import load_dotenv
import pymysql

print("Starting database connection test and setup...")

# Load environment variables
load_dotenv()
print("Loaded environment variables from .env file")

# Get database connection info
db_url = os.environ.get('DATABASE_URL')
print(f"Database URL from .env: {db_url}")

if not db_url:
    print("Error: DATABASE_URL not found in .env file")
    sys.exit(1)

# Parse connection string
# Example: mysql+pymysql://root:password@localhost:3306/irrigodb
try:
    db_url = db_url.replace('mysql+pymysql://', '')
    user_pass, host_db = db_url.split('@')
    user, password = user_pass.split(':')
    
    if ':' in host_db:
        host_port, db = host_db.split('/')
        host, port = host_port.split(':')
        port = int(port)
    else:
        host, db = host_db.split('/')
        port = 3306
        
    print(f"Parsed connection info:")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"User: {user}")
    print(f"Database: {db}")
    print(f"Password: {'*' * len(password)}")
except Exception as e:
    print(f"Error parsing DATABASE_URL: {e}")
    print("Expected format: mysql+pymysql://username:password@hostname:port/database")
    sys.exit(1)

# Test connection to MySQL server
try:
    print("\nConnecting to MySQL server...")
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        port=port
    )
    print("Connection successful!")
    
    # Create database if it doesn't exist
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db}`")
        connection.commit()
        print(f"Database '{db}' created or already exists")
    
    connection.close()
    
    # Connect to the specific database
    print(f"\nConnecting to '{db}' database...")
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        database=db
    )
    print(f"Connected to '{db}' database successfully!")
    
    # Create tables
    with connection.cursor() as cursor:
        # Users table
        print("\nCreating users table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(256) NOT NULL
        )
        """)
        
        # SensorData table
        print("Creating sensordata table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensordata (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            temperature FLOAT,
            humidity FLOAT,
            uv_intensity FLOAT,
            rainfall FLOAT,
            soil_moisture_level FLOAT,
            ph_level FLOAT,
            tank_water_volume FLOAT,
            water_pressure FLOAT,
            INDEX (timestamp)
        )
        """)
        
        # Devices table
        print("Creating devices table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            control_id VARCHAR(100) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            device_type VARCHAR(50) NOT NULL,
            status VARCHAR(50) DEFAULT 'UNKNOWN',
            last_status_update TIMESTAMP NULL,
            is_enabled BOOLEAN DEFAULT TRUE
        )
        """)
        
        connection.commit()
        print("All tables created successfully!")
        
        # Show tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\nTables in the database:")
        for table in tables:
            print(f"- {table[0]}")
    
    connection.close()
    print("\nDatabase setup completed successfully!")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
