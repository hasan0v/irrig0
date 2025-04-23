"""
Database setup and verification script for İrrigo project
"""
import os
import sys
import pymysql
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get database connection parameters from .env
db_url = os.environ.get('DATABASE_URL')
if not db_url or not db_url.startswith('mysql+pymysql://'):
    print("Error: DATABASE_URL not found in .env file or not in correct format.")
    print("Expected format: mysql+pymysql://username:password@localhost:3306/irrigodb")
    sys.exit(1)

# Parse the database URL
parts = db_url.replace('mysql+pymysql://', '').split('@')
if len(parts) != 2:
    print("Error: Invalid DATABASE_URL format.")
    sys.exit(1)

auth = parts[0].split(':')
if len(auth) != 2:
    print("Error: Invalid username/password format in DATABASE_URL.")
    sys.exit(1)

username = auth[0]
password = auth[1]

host_parts = parts[1].split('/')
if len(host_parts) != 2:
    print("Error: Invalid host/database format in DATABASE_URL.")
    sys.exit(1)

host_port = host_parts[0].split(':')
host = host_port[0]
port = int(host_port[1]) if len(host_port) > 1 else 3306
database = host_parts[1]

print(f"Database configuration:")
print(f"Host: {host}")
print(f"Port: {port}")
print(f"Username: {username}")
print(f"Database: {database}")
print(f"Password: {'*' * len(password)}")

# Try to connect to MySQL server (without specifying a database first)
try:
    print("\nStep 1: Connecting to MySQL server...")
    conn = pymysql.connect(
        host=host,
        port=port,
        user=username,
        password=password
    )
    print("✓ Connected to MySQL server successfully.")
    
    # Check if database exists, create it if not
    with conn.cursor() as cursor:
        print(f"\nStep 2: Checking if database '{database}' exists...")
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        
        if database in databases:
            print(f"✓ Database '{database}' already exists.")
        else:
            print(f"Database '{database}' not found, creating it...")
            cursor.execute(f"CREATE DATABASE `{database}`")
            conn.commit()
            print(f"✓ Database '{database}' created successfully.")
    
    # Close the connection
    conn.close()
    
    # Connect to the specific database
    print(f"\nStep 3: Connecting to '{database}' database...")
    conn = pymysql.connect(
        host=host,
        port=port,
        user=username,
        password=password,
        database=database
    )
    print(f"✓ Connected to '{database}' database successfully.")
    
    # Create tables
    print("\nStep 4: Creating tables...")
    with conn.cursor() as cursor:
        # Create users table
        print("Creating 'users' table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(256) NOT NULL
        )
        """)
        
        # Create sensordata table
        print("Creating 'sensordata' table...")
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
        
        # Create devices table
        print("Creating 'devices' table...")
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
        
        # Commit the changes
        conn.commit()
        print("✓ All tables created successfully.")
        
        # Show tables in the database
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\nTables in the database:")
        for table in tables:
            print(f"- {table[0]}")
    
    # Close the connection
    conn.close()
    print("\nDatabase setup completed successfully!")
    
except pymysql.MySQLError as e:
    print(f"\nError: {e}")
    error_str = str(e)
    
    if "Access denied" in error_str:
        print("\nAccess denied. Please check your username and password.")
        print("Make sure the MySQL user exists and has the correct privileges.")
    elif "Can't connect to MySQL server" in error_str:
        print("\nCannot connect to MySQL server. Please check:")
        print("1. MySQL server is running")
        print("2. Host and port are correct")
        print("3. Network connectivity between this app and the database")
    elif "Unknown database" in error_str:
        print(f"\nDatabase '{database}' does not exist.")
        print("The script will attempt to create it.")
    else:
        print("\nUnknown error. Please check your MySQL configuration.")
except Exception as e:
    print(f"\nUnexpected error: {e}")
    import traceback
    traceback.print_exc()
