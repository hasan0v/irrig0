"""
Add demonstration device data to the database
"""
from app.app import app
from app.database import db
from app.models import Device
from datetime import datetime, timedelta
import random

# Sample devices to add to the database
sample_devices = [
    # Pumps
    {
        "control_id": "pump_main_water",
        "name": "Ana Su Pompası",
        "device_type": "PUMP",
        "status": "OFF"
    },
    {
        "control_id": "pump_irrigation_zone1",
        "name": "Sulama Pompası Bölge 1",
        "device_type": "PUMP",
        "status": "OFF"
    },
    {
        "control_id": "pump_irrigation_zone2",
        "name": "Sulama Pompası Bölge 2",
        "device_type": "PUMP",
        "status": "OFF"
    },
    {
        "control_id": "pump_fertilizer",
        "name": "Gübre Dozaj Pompası",
        "device_type": "PUMP",
        "status": "OFF"
    },
    
    # Valves
    {
        "control_id": "valve_zone1",
        "name": "Sulama Vanası Bölge 1",
        "device_type": "VALVE",
        "status": "CLOSED"
    },
    {
        "control_id": "valve_zone2",
        "name": "Sulama Vanası Bölge 2",
        "device_type": "VALVE",
        "status": "CLOSED"
    },
    {
        "control_id": "valve_tank_fill",
        "name": "Tank Doldurma Vanası",
        "device_type": "VALVE",
        "status": "CLOSED"
    },
    {
        "control_id": "valve_tank_drain",
        "name": "Tank Boşaltma Vanası",
        "device_type": "VALVE",
        "status": "CLOSED"
    },
    
    # Lights
    {
        "control_id": "light_greenhouse_main",
        "name": "Sera Ana Aydınlatma",
        "device_type": "LIGHT",
        "status": "OFF"
    },
    {
        "control_id": "light_greenhouse_suppl",
        "name": "Sera Destekleyici Aydınlatma",
        "device_type": "LIGHT",
        "status": "OFF"
    },
    
    # Fans/Ventilation
    {
        "control_id": "fan_greenhouse_1",
        "name": "Sera Fanı 1",
        "device_type": "FAN",
        "status": "OFF"
    },
    {
        "control_id": "fan_greenhouse_2",
        "name": "Sera Fanı 2",
        "device_type": "FAN",
        "status": "OFF"
    },
    
    # Heater
    {
        "control_id": "heater_greenhouse",
        "name": "Sera Isıtıcı",
        "device_type": "HEATER",
        "status": "OFF"
    },
    
    # Disabled device (for testing)
    {
        "control_id": "pump_backup",
        "name": "Yedek Pompa (Bakımda)",
        "device_type": "PUMP",
        "status": "UNKNOWN",
        "is_enabled": False
    }
]

def add_demo_devices():
    with app.app_context():
        # Check if devices already exist
        existing_count = Device.query.count()
        if existing_count > 0:
            print(f"Found {existing_count} existing devices in database.")
            confirmation = input("Do you want to add more demo devices anyway? (y/n): ")
            if confirmation.lower() != 'y':
                print("Aborted. No changes made to database.")
                return
        
        # Generate random update timestamps within last 24 hours
        now = datetime.now()
        
        # Add each device to the database
        for device_data in sample_devices:
            # Create a random timestamp within the last 24 hours
            random_minutes = random.randint(0, 1440)  # Up to 24 hours
            last_update = now - timedelta(minutes=random_minutes)
            
            # Add the timestamp to the device data
            device_data['last_status_update'] = last_update
            
            # Create the device object
            device = Device(**device_data)
            
            # Add to database
            db.session.add(device)
        
        # Commit all changes
        db.session.commit()
        print(f"Successfully added {len(sample_devices)} demo devices to the database.")

if __name__ == "__main__":
    add_demo_devices()
