#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Add demonstration sensor data to the İrrigo database.
This script populates the database with realistic sample data
for testing and demonstration purposes.
"""

import os
import sys
import random
from datetime import datetime, timedelta
from app import app
from app.database import db
from app.models import SensorData

def create_demo_data(num_days=3, readings_per_day=48):
    """
    Create demonstration sensor data for the past few days.
    Generates realistic variations in sensor values over time.
    
    Args:
        num_days: Number of days of data to generate
        readings_per_day: Number of readings per day (default: 48, one every 30 min)
    """
    # Base values for various sensors
    base_values = {
        # Weather conditions
        'temperature': 24.5,         # °C
        'humidity': 65.0,            # %
        'uv_intensity': 5.5,         # UV Index
        'rainfall': 0.0,             # mm
        'atmospheric_pressure': 1013.0,  # hPa
        'wind_speed': 2.5,           # m/s
        'wind_direction': 'NW',      # compass direction
        
        # Soil conditions
        'soil_moisture_level': 42.0,  # %
        'soil_temperature': 22.5,    # °C
        'ph_level': 6.8,             # pH scale
        'soil_ec': 750.0,            # µS/cm
        'soil_npk': '15-10-12',      # N-P-K ratio
        'soil_sap_moisture': 72.0,   # %
        
        # Water tank status
        'tank_water_volume': 850.0,  # Liters
        'dirty_tank_volume': 220.0,  # Liters
        'pump_pressure': 2.8,        # bar
        'water_treatment_rate': 12.5, # L/min
        
        # Water quality
        'water_temperature': 23.0,   # °C
        'water_ph': 7.2,             # pH scale
        'water_ec': 320.0,           # µS/cm
        'water_tds': 160.0,          # mg/L
        'water_flow_rate': 15.2,     # L/min
        'water_turbidity': 1.2,      # NTU
        'water_orp': 650.0,          # mV
        'water_do': 8.5,             # mg/L
        
        # Plant environment
        'light_par': 1100.0,         # µmol/m²/s
        'co2_concentration': 410.0,  # ppm
        'air_temperature': 25.2,     # °C
        
        # System metrics
        'clean_water_processed': 450.0,  # L daily
        'used_water_processed': 320.0,   # L daily
        'system_power_usage': 85.0,      # Wh
        'battery_level': 92.0            # %
    }
    
    # Variable fluctuation ranges (how much each reading can vary from the previous one)
    fluctuation = {
        'temperature': 0.8,
        'humidity': 2.5,
        'uv_intensity': 0.5,
        'rainfall': 0.5,
        'atmospheric_pressure': 0.8,
        'wind_speed': 0.7,
        'soil_moisture_level': 1.2,
        'soil_temperature': 0.4,
        'ph_level': 0.1,
        'soil_ec': 25.0,
        'tank_water_volume': 30.0,
        'dirty_tank_volume': 20.0,
        'pump_pressure': 0.2,
        'water_treatment_rate': 0.5,
        'water_temperature': 0.3,
        'water_ph': 0.1,
        'water_ec': 10.0,
        'water_tds': 8.0,
        'water_flow_rate': 0.8,
        'water_turbidity': 0.2,
        'water_orp': 15.0,
        'water_do': 0.3,
        'light_par': 50.0,
        'co2_concentration': 15.0,
        'air_temperature': 0.5,
        'clean_water_processed': 25.0,
        'used_water_processed': 18.0,
        'system_power_usage': 5.0,
        'battery_level': 2.0
    }
    
    # Special handling for cyclic parameters (day/night cycle)
    cyclic_params = {
        'temperature': {'amplitude': 8.0, 'peak_time': 14},  # Peak at 2 PM
        'uv_intensity': {'amplitude': 7.0, 'peak_time': 13},  # Peak at 1 PM
        'light_par': {'amplitude': 1200, 'peak_time': 13},   # Peak at 1 PM
        'air_temperature': {'amplitude': 7.0, 'peak_time': 14}  # Peak at 2 PM
    }
    
    # Wind directions to cycle through
    wind_directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    
    # Generate data for each day
    now = datetime.now()
    start_date = now - timedelta(days=num_days)
    total_readings = num_days * readings_per_day
    
    print(f"Generating {total_readings} sensor readings across {num_days} days...")
    
    # Dictionary to hold current values as they fluctuate
    current = base_values.copy()
    
    # Create sensor readings
    readings = []
    for i in range(total_readings):
        # Calculate timestamp for this reading
        minutes_offset = i * (24 * 60 // readings_per_day)
        timestamp = start_date + timedelta(minutes=minutes_offset)
        
        # Hour of the day (0-23), useful for cyclic variations
        hour = timestamp.hour + timestamp.minute / 60.0
        
        # Create a new sensor reading
        reading = SensorData(timestamp=timestamp)
        
        # Apply cyclic variations (day/night, etc.)
        for param, cycle in cyclic_params.items():
            # Calculate time distance from peak (in hours, considering 24-hour cycle)
            time_diff = min(abs(hour - cycle['peak_time']), 24 - abs(hour - cycle['peak_time']))
            # Convert to a 0-1 factor (0 at peak, 1 at furthest from peak)
            factor = time_diff / 12.0  
            # Apply to create a sine-like curve
            cycle_value = current[param] - cycle['amplitude'] * factor
            # Apply some randomness
            cycle_value += random.uniform(-fluctuation[param], fluctuation[param])
            
            # Special case for UV and light: should be near zero at night
            if param in ['uv_intensity', 'light_par'] and (hour < 6 or hour > 20):
                cycle_value = max(0, cycle_value * 0.05)  # 95% reduction at night
                
            # Update the current value
            current[param] = cycle_value
            # Set the attribute in the reading
            setattr(reading, param, cycle_value)
        
        # Handle special case for rainfall (sporadic and accumulative)
        if random.random() < 0.05:  # 5% chance of rain in any reading
            rain_amount = random.uniform(0.2, 5.0)  # Random rainfall between 0.2 and 5mm
            current['rainfall'] = rain_amount
        else:
            current['rainfall'] = 0
        
        # Handle wind direction
        if random.random() < 0.3:  # 30% chance of wind direction change
            current['wind_direction'] = random.choice(wind_directions)
        
        # Handle soil_npk (changes less frequently)
        if i % 24 == 0 or random.random() < 0.05:  # Once a day or 5% chance
            n = random.randint(10, 20)
            p = random.randint(8, 15)
            k = random.randint(10, 18)
            current['soil_npk'] = f"{n}-{p}-{k}"
        
        # Update all other parameters with random fluctuations
        for param, value in current.items():
            # Skip parameters already handled by cyclic logic
            if param in cyclic_params or param in ['rainfall', 'wind_direction', 'soil_npk']:
                continue
                
            # Apply random fluctuation to current value
            if param in fluctuation:
                new_value = value + random.uniform(-fluctuation[param], fluctuation[param])
                # Ensure logical constraints (non-negative values, etc.)
                if param in ['humidity', 'soil_moisture_level', 'battery_level']:
                    new_value = max(0, min(100, new_value))  # 0-100% range
                elif param in ['ph_level', 'water_ph']:
                    new_value = max(0, min(14, new_value))   # 0-14 pH range
                elif param.endswith('_volume') or param.endswith('_rate') or param.endswith('_processed'):
                    new_value = max(0, new_value)  # Non-negative volumes and rates
                    
                current[param] = new_value
                
            # Set the attribute in the reading
            if hasattr(reading, param):
                setattr(reading, param, current[param])
        
        # Add to the readings list
        readings.append(reading)
        
        # Progress indication for longer generations
        if i % 50 == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
    
    print("\nSaving sensor readings to database...")
    # Save all readings to the database
    db.session.add_all(readings)
    db.session.commit()
    
    print(f"Added {len(readings)} sensor readings to the database.")

if __name__ == "__main__":
    # Properly set up the application context
    with app.app_context():
        # Check if we should clear existing data first
        if len(sys.argv) > 1 and sys.argv[1] == '--clear':
            print("Clearing existing sensor data...")
            db.session.query(SensorData).delete()
            db.session.commit()
            print("Database cleared.")
        
        # Create the demo data
        create_demo_data()
        print("Demo data generation complete!")
