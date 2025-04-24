# update_sensordata_schema.py
import pymysql
import sys
import os
from dotenv import load_dotenv

print("Starting SensorData table schema update...")

# Load environment variables from .env file
load_dotenv()

# Database connection parameters from environment variables or defaults
HOST = os.getenv('DB_HOST', 'mysql-39fcea5a-c3mc3f-85cc.f.aivencloud.com')
PORT = int(os.getenv('DB_PORT', 26927))
USER = os.getenv('DB_USER', 'avnadmin')
PASSWORD = os.getenv('DB_PASSWORD', 'AVNS_z46AZhlgazLrqlk0f83') # Be cautious with hardcoding passwords
DATABASE = os.getenv('DB_NAME', 'irrigodb')

print(f"Connecting to MySQL database: {DATABASE} on {HOST}:{PORT}")

try:
    # Connect to the database
    connection = pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        port=PORT,
        database=DATABASE,
        cursorclass=pymysql.cursors.DictCursor # Use DictCursor for easier column checking
    )
    print("Connected to database successfully!")

    with connection.cursor() as cursor:
        print("\nChecking current SensorData table structure...")
        cursor.execute("DESCRIBE sensordata;")
        columns_info = cursor.fetchall()
        existing_columns = {col['Field']: col for col in columns_info}
        print(f"Found {len(existing_columns)} existing columns.")

        # --- Rename Columns ---
        if 'temperature' in existing_columns and 'air_temperature' not in existing_columns:
            print("Renaming 'temperature' to 'air_temperature'...")
            cursor.execute("ALTER TABLE sensordata CHANGE COLUMN temperature air_temperature FLOAT COMMENT 'Unit: °C. Source: Air';")
            print("'temperature' renamed to 'air_temperature'.")
        elif 'temperature' in existing_columns:
             print("'temperature' column found, but 'air_temperature' already exists. Skipping rename.")
        elif 'air_temperature' not in existing_columns:
            print("Neither 'temperature' nor 'air_temperature' found. Adding 'air_temperature'.")
            cursor.execute("ALTER TABLE sensordata ADD COLUMN air_temperature FLOAT NULL COMMENT 'Unit: °C. Source: Air';")
            print("Added 'air_temperature' column.")
        else:
            print("'air_temperature' column already exists.")


        if 'ph_level' in existing_columns and 'soil_ph' not in existing_columns:
            print("Renaming 'ph_level' to 'soil_ph'...")
            cursor.execute("ALTER TABLE sensordata CHANGE COLUMN ph_level soil_ph FLOAT COMMENT 'Source: Soil';")
            print("'ph_level' renamed to 'soil_ph'.")
        elif 'ph_level' in existing_columns:
             print("'ph_level' column found, but 'soil_ph' already exists. Skipping rename.")
        elif 'soil_ph' not in existing_columns:
            print("Neither 'ph_level' nor 'soil_ph' found. Adding 'soil_ph'.")
            cursor.execute("ALTER TABLE sensordata ADD COLUMN soil_ph FLOAT NULL COMMENT 'Source: Soil';")
            print("Added 'soil_ph' column.")
        else:
            print("'soil_ph' column already exists.")

        # --- Add New Columns ---
        new_columns = {
            'atmospheric_pressure': "FLOAT NULL COMMENT 'Unit: hPa'",
            'soil_temperature': "FLOAT NULL COMMENT 'Unit: °C'",
            'soil_ec': "FLOAT NULL COMMENT 'Unit: µS/cm'",
            'soil_n': "FLOAT NULL COMMENT 'Unit: mg/kg'",
            'soil_p': "FLOAT NULL COMMENT 'Unit: mg/kg'",
            'soil_k': "FLOAT NULL COMMENT 'Unit: mg/kg'",
            'sap_moisture': "FLOAT NULL COMMENT 'Unit: %'",
            'dirty_water_volume': "FLOAT NULL COMMENT 'Unit: Liters'",
            'treatment_rate': "FLOAT NULL COMMENT 'Unit: L/min'",
            'water_temperature': "FLOAT NULL COMMENT 'Unit: °C'",
            'water_ph': "FLOAT NULL COMMENT 'Source: Water'",
            'water_ec': "FLOAT NULL COMMENT 'Unit: µS/cm'",
            'water_tds': "FLOAT NULL COMMENT 'Unit: mg/L'",
            'water_flow_rate': "FLOAT NULL COMMENT 'Unit: L/min'",
            'water_ntu': "FLOAT NULL COMMENT 'Unit: NTU'",
            'water_nh3': "FLOAT NULL COMMENT 'Unit: mg/L'",
            'water_no3': "FLOAT NULL COMMENT 'Unit: mg/L'",
            'light_par': "FLOAT NULL COMMENT 'Unit: µmol/m²/s'",
            'co2_concentration': "FLOAT NULL COMMENT 'Unit: ppm'"
        }

        # Refresh column list after potential renames
        cursor.execute("DESCRIBE sensordata;")
        columns_info_after_rename = cursor.fetchall()
        existing_columns_after_rename = {col['Field']: col for col in columns_info_after_rename}


        print("\nAdding missing columns...")
        added_count = 0
        for col_name, col_definition in new_columns.items():
            if col_name not in existing_columns_after_rename:
                print(f"Adding column: {col_name}")
                sql = f"ALTER TABLE sensordata ADD COLUMN {col_name} {col_definition};"
                cursor.execute(sql)
                added_count += 1
            else:
                print(f"Column '{col_name}' already exists. Skipping.")

        if added_count > 0:
             print(f"Added {added_count} new columns.")
        else:
             print("No new columns needed to be added.")

        connection.commit()
        print("\nSchema update committed successfully!")

        # Verify final structure
        print("\nFinal SensorData table structure:")
        cursor.execute("DESCRIBE sensordata;")
        final_columns = cursor.fetchall()
        for column in final_columns:
            print(f"  - {column['Field']}: {column['Type']} {'NULL' if column['Null'] == 'YES' else 'NOT NULL'} {column['Extra']} {column.get('Comment', '')}")

    connection.close()
    print("\nDatabase connection closed.")
    print("Schema update script completed successfully!")

except pymysql.Error as e:
    print(f"\nDatabase Error: {e}")
    # Attempt to rollback if connection is still open
    try:
        if connection.open:
            connection.rollback()
            print("Transaction rolled back.")
    except Exception as rollback_e:
        print(f"Error during rollback: {rollback_e}")
    sys.exit(f"Script failed with database error: {e.code} - {e}")
except Exception as e:
    print(f"\nGeneral Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(f"Script failed with general error: {e}")
