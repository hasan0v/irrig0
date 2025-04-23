import pymysql
import sys

# Direct connection parameters
HOST = 'mysql-39fcea5a-c3mc3f-85cc.f.aivencloud.com'
PORT = 26927
USER = 'avnadmin'
PASSWORD = 'AVNS_z46AZhlgazLrqlk0f83'
DATABASE = 'irrigodb'

try:
    # Connect to the database
    sys.stdout.write("Connecting to database...\n")
    sys.stdout.flush()
    
    conn = pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        port=PORT,
        database=DATABASE
    )
    
    sys.stdout.write("Connected successfully\n")
    sys.stdout.flush()
    
    with conn.cursor() as cursor:
        # Create users table
        sys.stdout.write("Creating users table...\n")
        sys.stdout.flush()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(256) NOT NULL
        )
        """)
        
        # Create sensordata table
        sys.stdout.write("Creating sensordata table...\n")
        sys.stdout.flush()
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
        sys.stdout.write("Creating devices table...\n")
        sys.stdout.flush()
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
        
        conn.commit()
        sys.stdout.write("All tables created successfully!\n")
        sys.stdout.flush()
        
        # Verify tables exist
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        sys.stdout.write(f"Tables in database: {[t[0] for t in tables]}\n")
        sys.stdout.flush()
    
    conn.close()
    
except Exception as e:
    sys.stdout.write(f"Error: {e}\n")
    sys.stdout.flush()
    sys.exit(1)
