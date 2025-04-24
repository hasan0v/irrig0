#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add demonstration sensor data to the İrrigo database (Updated Schema).
This script populates the database with realistic sample data
for testing and demonstration purposes, reflecting the latest sensordata table structure.
"""

import os
import sys
import random
import math
from datetime import datetime, timedelta, timezone
import pymysql
from dotenv import load_dotenv

# --- Configuration ---
NUM_DAYS = 1 # Number of days to generate data for
READINGS_PER_HOUR = 2 # Changed from per day to per hour for clarity
BATCH_SIZE = 100 # Insert data in batches

# --- Database Connection ---
load_dotenv()
HOST = os.getenv('DB_HOST', 'mysql-39fcea5a-c3mc3f-85cc.f.aivencloud.com')
PORT = int(os.getenv('DB_PORT', 26927))
USER = os.getenv('DB_USER', 'avnadmin')
PASSWORD = os.getenv('DB_PASSWORD', 'AVNS_z46AZhlgazLrqlk0f83')
DATABASE = os.getenv('DB_NAME', 'irrigodb')

# --- Sensor Simulation Parameters ---

# Base values (starting point for simulation)
base_values = {
    'air_temperature': 22.0,         # °C (Renamed from temperature)
    'humidity': 60.0,            # %
    'uv_intensity': 4.0,         # UV Index
    'rainfall': 0.0,             # mm
    'atmospheric_pressure': 1015.0, # hPa (Added)
    'soil_moisture_level': 55.0,  # %
    'soil_temperature': 20.0,    # °C (Added)
    'soil_ph': 6.5,             # pH scale (Renamed from ph_level)
    'soil_ec': 800.0,            # µS/cm (Added)
    'soil_n': 15.0,              # mg/kg (Added)
    'soil_p': 10.0,              # mg/kg (Added)
    'soil_k': 12.0,              # mg/kg (Added)
    'sap_moisture': 70.0,        # % (Added, was soil_sap_moisture)
    'tank_water_volume': 750.0,  # Liters
    'dirty_water_volume': 150.0, # Liters (Added, was dirty_tank_volume)
    'water_pressure': 2.5,       # bar (Renamed from pump_pressure)
    'treatment_rate': 10.0,      # L/min (Added, was water_treatment_rate)
    'water_temperature': 18.0,   # °C (Added)
    'water_ph': 7.0,             # pH scale (Added)
    'water_ec': 300.0,           # µS/cm (Added)
    'water_tds': 150.0,          # mg/L (Added)
    'water_flow_rate': 12.0,     # L/min (Added)
    'water_ntu': 1.0,            # NTU (Added, was water_turbidity)
    'water_nh3': 0.5,            # mg/L (Added)
    'water_no3': 5.0,            # mg/L (Added)
    'light_par': 800.0,          # µmol/m²/s (Added)
    'co2_concentration': 415.0,  # ppm (Added)
}

# Max fluctuation per step (hour)
fluctuation = {
    'air_temperature': 0.6,
    'humidity': 2.0,
    'uv_intensity': 0.4,
    'rainfall': 0.3, # Chance of starting/stopping rain handled separately
    'atmospheric_pressure': 0.5,
    'soil_moisture_level': 1.0,
    'soil_temperature': 0.3,
    'soil_ph': 0.05,
    'soil_ec': 20.0,
    'soil_n': 0.5,
    'soil_p': 0.3,
    'soil_k': 0.4,
    'sap_moisture': 1.5,
    'tank_water_volume': 20.0, # Can decrease due to usage, increase due to rain/treatment
    'dirty_water_volume': 15.0, # Increases with usage, decreases with treatment
    'water_pressure': 0.1,
    'treatment_rate': 0.3,
    'water_temperature': 0.2,
    'water_ph': 0.05,
    'water_ec': 8.0,
    'water_tds': 5.0,
    'water_flow_rate': 0.5,
    'water_ntu': 0.1,
    'water_nh3': 0.05,
    'water_no3': 0.2,
    'light_par': 40.0,
    'co2_concentration': 10.0,
}

# Realistic Min/Max bounds
bounds = {
    'air_temperature': (0, 45),
    'humidity': (10, 100),
    'uv_intensity': (0, 12),
    'rainfall': (0, 20), # Max rain per hour
    'atmospheric_pressure': (980, 1050),
    'soil_moisture_level': (5, 95),
    'soil_temperature': (0, 40),
    'soil_ph': (4.0, 9.0),
    'soil_ec': (100, 2000),
    'soil_n': (1, 50),
    'soil_p': (1, 40),
    'soil_k': (1, 40),
    'sap_moisture': (20, 98),
    'tank_water_volume': (0, 1000), # Assuming 1000L max tank
    'dirty_water_volume': (0, 500), # Assuming 500L max dirty tank
    'water_pressure': (0, 6),
    'treatment_rate': (0, 20),
    'water_temperature': (5, 35),
    'water_ph': (6.0, 8.5),
    'water_ec': (50, 1000),
    'water_tds': (25, 500),
    'water_flow_rate': (0, 30),
    'water_ntu': (0, 10),
    'water_nh3': (0, 2),
    'water_no3': (0, 20),
    'light_par': (0, 2000),
    'co2_concentration': (380, 1000),
}

# Parameters influenced by time of day (amplitude relative to base, peak hour)
cyclic_params = {
    'air_temperature': {'amplitude': 7.0, 'peak_time': 15},
    'soil_temperature': {'amplitude': 4.0, 'peak_time': 16}, # Lags air temp
    'uv_intensity': {'amplitude': 5.0, 'peak_time': 13},
    'light_par': {'amplitude': 1000.0, 'peak_time': 13},
    'humidity': {'amplitude': -15.0, 'peak_time': 15}, # Inverse relationship with temp
}

# --- Helper Functions ---

def apply_bounds(value, param):
    """Clamps the value within the defined bounds for the parameter."""
    if param in bounds:
        min_val, max_val = bounds[param]
        return max(min_val, min(max_val, value))
    return value

def generate_value(current_val, param, hour):
    """Generates the next value for a sensor, applying fluctuations and cycles."""
    new_val = current_val

    # Apply cyclic variation if applicable
    if param in cyclic_params:
        cycle = cyclic_params[param]
        # Calculate time distance from peak (0-12 hours)
        time_diff = min(abs(hour - cycle['peak_time']), 24 - abs(hour - cycle['peak_time']))
        # Cosine curve for smooth transition (1 at peak, -1 at furthest)
        cycle_factor = math.cos(math.pi * time_diff / 12.0)
        # Apply amplitude relative to the base value
        base = base_values[param]
        target_val = base + cycle['amplitude'] * cycle_factor
        # Move towards the target value, but also add random fluctuation
        # Weight moving towards target vs random walk
        new_val = (new_val * 0.6 + target_val * 0.4) + random.uniform(-fluctuation[param], fluctuation[param])

        # Special handling for light/UV at night
        if param in ['uv_intensity', 'light_par'] and (hour < 5 or hour > 19):
             new_val = base_values[param] * random.uniform(0, 0.05) # Near zero at night

    else:
        # Apply simple random fluctuation for non-cyclic params
        new_val += random.uniform(-fluctuation[param], fluctuation[param])

    # Apply bounds
    new_val = apply_bounds(new_val, param)

    return new_val

# --- Main Data Generation Logic ---

def create_demo_data(connection):
    """Generates and inserts demonstration sensor data."""

    total_hours = NUM_DAYS * 24 * READINGS_PER_HOUR
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(days=NUM_DAYS)

    print(f"Generating {total_hours} hourly sensor readings for the past {NUM_DAYS} days...")

    current_values = base_values.copy()
    all_readings_data = []
    is_raining = False
    rain_intensity = 0.0

    for i in range(total_hours):
        timestamp = start_time + timedelta(hours=i / READINGS_PER_HOUR)
        hour_of_day = timestamp.hour + timestamp.minute / 60.0

        reading_data = {'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')}

        # Simulate rain starting/stopping
        if not is_raining and random.random() < 0.03: # 3% chance to start raining
            is_raining = True
            rain_intensity = random.uniform(0.5, 5.0) # mm/hour
            print(f"\nRain started at {timestamp} ({rain_intensity:.1f} mm/hr)")
        elif is_raining and random.random() < 0.15: # 15% chance to stop raining
            is_raining = False
            rain_intensity = 0.0
            print(f"\nRain stopped at {timestamp}")

        current_values['rainfall'] = rain_intensity if is_raining else 0.0
        # Rainfall affects soil moisture and tank volume
        if is_raining:
            current_values['soil_moisture_level'] += rain_intensity * 0.5 # Increase moisture
            current_values['tank_water_volume'] += rain_intensity * 10 # Assume collection area factor

        # Simulate water usage (affects tank volumes)
        water_used = 0
        if 6 <= hour_of_day <= 22 and random.random() < 0.4: # 40% chance of usage during day
            water_used = random.uniform(5, 15)
            current_values['tank_water_volume'] -= water_used
            current_values['dirty_water_volume'] += water_used * 0.8 # Some loss

        # Simulate water treatment (affects tank volumes)
        water_treated = 0
        if current_values['dirty_water_volume'] > 20 and random.random() < 0.6: # 60% chance if dirty water available
             water_treated = min(current_values['dirty_water_volume'], current_values['treatment_rate'] / (60/READINGS_PER_HOUR)) # Treat based on rate
             current_values['dirty_water_volume'] -= water_treated
             current_values['tank_water_volume'] += water_treated * 0.95 # Some loss in treatment


        # Generate values for all other sensors
        for param in base_values.keys():
            if param == 'rainfall': # Handled above
                 reading_data[param] = current_values[param]
                 continue

            current_values[param] = generate_value(current_values[param], param, hour_of_day)
            # Use None for ~5% of readings for some sensors to simulate missing data
            if param not in ['air_temperature', 'soil_moisture_level', 'tank_water_volume'] and random.random() < 0.05:
                 reading_data[param] = None
            else:
                 # Format floats to reasonable precision
                 reading_data[param] = round(current_values[param], 2) if isinstance(current_values[param], float) else current_values[param]


        all_readings_data.append(reading_data)

        # Progress indication
        if (i + 1) % 50 == 0:
            sys.stdout.write('.')
            sys.stdout.flush()

    print(f"\nGenerated {len(all_readings_data)} data points.")

    # --- Insert Data into Database ---
    print("Inserting data into database (in batches)...")
    inserted_count = 0
    try:
        with connection.cursor() as cursor:
            # Get column names from the table to ensure order and existence
            cursor.execute("DESCRIBE sensordata;")
            db_columns = [col['Field'] for col in cursor.fetchall() if col['Field'] != 'id'] # Exclude auto-increment id

            sql_template = f"""
                INSERT INTO sensordata ({', '.join(db_columns)})
                VALUES ({', '.join(['%s'] * len(db_columns))})
            """

            batch_data = []
            for reading in all_readings_data:
                row_values = []
                for col_name in db_columns:
                    row_values.append(reading.get(col_name)) # Use get() to handle potentially missing keys gracefully (though shouldn't happen here)
                batch_data.append(tuple(row_values))

                if len(batch_data) >= BATCH_SIZE:
                    cursor.executemany(sql_template, batch_data)
                    inserted_count += len(batch_data)
                    batch_data = []
                    sys.stdout.write('+') # Progress marker for batch insert
                    sys.stdout.flush()

            # Insert any remaining data
            if batch_data:
                cursor.executemany(sql_template, batch_data)
                inserted_count += len(batch_data)
                sys.stdout.write('+')
                sys.stdout.flush()

            connection.commit()
            print(f"\nSuccessfully inserted {inserted_count} records.")

    except pymysql.Error as e:
        print(f"\nDatabase Error during insert: {e}")
        print("Attempting to rollback...")
        connection.rollback()
        print("Rollback successful.")
    except Exception as e:
        print(f"\nAn unexpected error occurred during insert: {e}")
        import traceback
        traceback.print_exc()
        print("Attempting to rollback...")
        connection.rollback()
        print("Rollback successful.")


# --- Main Execution ---
if __name__ == "__main__":
    connection = None
    try:
        print(f"Connecting to database: {DATABASE} on {HOST}:{PORT}")
        connection = pymysql.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            port=PORT,
            database=DATABASE,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False # Ensure we control commits
        )
        print("Connected successfully.")

        # Check if --clear flag is provided
        if len(sys.argv) > 1 and sys.argv[1] == '--clear':
            print("Clearing existing sensor data from 'sensordata' table...")
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM sensordata;")
            connection.commit()
            print("Table cleared.")

        # Create and insert the demo data
        create_demo_data(connection)
        print("\nDemo data generation complete!")

    except pymysql.Error as e:
        print(f"\nDatabase Connection Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if connection and connection.open:
            connection.close()
            print("Database connection closed.")
