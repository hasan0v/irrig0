"""
Direct MySQL Table Creation Script for İrrigo Project
"""
import pymysql
import sys

print("Starting MySQL table creation...")

# Database connection parameters
HOST = 'mysql-39fcea5a-c3mc3f-85cc.f.aivencloud.com'
PORT = 26927
USER = 'avnadmin'
PASSWORD = 'AVNS_z46AZhlgazLrqlk0f83'
DATABASE = 'irrigodb'

print(f"Connecting to MySQL database: {DATABASE} on {HOST}:{PORT}")

try:
    # Connect to the database
    connection = pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        port=PORT,
        database=DATABASE
    )
    print(f"Connected to database successfully!")
    
    # Create tables
    with connection.cursor() as cursor:
        # Check existing tables
        cursor.execute("SHOW TABLES")
        existing_tables = [table[0] for table in cursor.fetchall()]
        print(f"Existing tables: {existing_tables}")
        
        # Users table
        print("\nCreating 'users' table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(256) NOT NULL
        )
        """)
        
        # SensorData table
        print("Creating 'sensordata' table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensordata (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            temperature FLOAT COMMENT 'Unit: °C. Source: Air/Soil/Water',
            humidity FLOAT COMMENT 'Unit: %',
            uv_intensity FLOAT COMMENT 'Unit: Index or W/m²',
            rainfall FLOAT COMMENT 'Unit: mm',
            soil_moisture_level FLOAT COMMENT 'Unit: %',
            ph_level FLOAT COMMENT 'Source: Soil/Water',
            tank_water_volume FLOAT COMMENT 'Unit: Liters',
            water_pressure FLOAT COMMENT 'Unit: bar or psi',
            INDEX (timestamp)
        )
        """)
        
        # Devices table
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
        
        connection.commit()
        print("All tables created successfully!")
        
        # Check tables after creation
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        print("\nTables in the database after creation:")
        for table in tables:
            print(f"- {table}")
            
            # Show table structure
            cursor.execute(f"DESCRIBE `{table}`")
            columns = cursor.fetchall()
            print(f"  Structure of '{table}':")
            for column in columns:
                print(f"    - {column[0]}: {column[1]}")
    
    connection.close()
    print("\nDatabase setup completed successfully!")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
