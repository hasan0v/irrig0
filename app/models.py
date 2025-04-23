from app.database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    """Model for the users table"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False) # Increased length for hash

    def set_password(self, password):
        """Create hashed password."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class SensorData(db.Model):
    """Model for the sensordata table"""
    __tablename__ = 'sensordata'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.TIMESTAMP(timezone=True), nullable=False, server_default=db.func.now(), index=True)
    # Fields for FR-DASH-A (Sticky Header / Overview)
    temperature = db.Column(db.Float, comment='Unit: °C. Source: Air/Soil/Water needs clarification in PRD.')
    humidity = db.Column(db.Float, comment='Unit: %')
    uv_intensity = db.Column(db.Float, comment='Unit: Index or W/m² - needs clarification')
    rainfall = db.Column(db.Float, comment='Unit: mm. Time period needs clarification (e.g., last hour/day)')    # Fields for FR-DASH-B (Soil Conditions)
    soil_moisture_level = db.Column(db.Float, comment='Unit: %')
    soil_temperature = db.Column(db.Float, comment='Unit: °C')
    ph_level = db.Column(db.Float, comment='Unit: pH scale 0-14')
    soil_ec = db.Column(db.Float, comment='Unit: µS/cm, Electrical Conductivity')
    soil_npk = db.Column(db.String(20), comment='Nitrogen, Phosphorus, Potassium levels')
    soil_sap_moisture = db.Column(db.Float, comment='Unit: %, SAP Hydrogel moisture')
    
    # Fields for FR-DASH-E (Water Tank Status)
    tank_water_volume = db.Column(db.Float, comment='Unit: Liters. Clean water tank')
    dirty_tank_volume = db.Column(db.Float, comment='Unit: Liters. Wastewater tank')
    pump_pressure = db.Column(db.Float, comment='Unit: bar. Main water pump')
    water_treatment_rate = db.Column(db.Float, comment='Unit: L/min. System treatment flow rate')
    
    # Fields for FR-DASH-C (Water Quality)
    water_temperature = db.Column(db.Float, comment='Unit: °C. Treated water')
    water_ph = db.Column(db.Float, comment='Unit: pH scale. Treated water')
    water_ec = db.Column(db.Float, comment='Unit: µS/cm. Treated water EC')
    water_tds = db.Column(db.Float, comment='Unit: mg/L. Total Dissolved Solids')
    water_flow_rate = db.Column(db.Float, comment='Unit: L/min. Current flow rate')
    water_turbidity = db.Column(db.Float, comment='Unit: NTU. Water clarity measure')
    water_orp = db.Column(db.Float, comment='Unit: mV. Oxidation-Reduction Potential')
    water_do = db.Column(db.Float, comment='Unit: mg/L. Dissolved Oxygen')
    
    # Fields for FR-DASH-D (Plant Environment)
    light_par = db.Column(db.Float, comment='Unit: µmol/m²/s. Photosynthetically Active Radiation')
    co2_concentration = db.Column(db.Float, comment='Unit: ppm. Carbon dioxide level')
    air_temperature = db.Column(db.Float, comment='Unit: °C. Ambient air temperature')
    
    # Atmospheric data
    atmospheric_pressure = db.Column(db.Float, comment='Unit: hPa. Barometric pressure')
    wind_speed = db.Column(db.Float, comment='Unit: m/s. Current wind speed')
    wind_direction = db.Column(db.String(3), comment='Cardinal direction: N, NE, E, SE, etc.')
    
    # System metrics 
    clean_water_processed = db.Column(db.Float, comment='Unit: L. Daily clean water produced')
    used_water_processed = db.Column(db.Float, comment='Unit: L. Daily used water processed')
    system_power_usage = db.Column(db.Float, comment='Unit: Wh. Current power consumption')
    battery_level = db.Column(db.Float, comment='Unit: %. System battery status')

    def __repr__(self):
        return f'<SensorData {self.id} @ {self.timestamp}>'
        
    def to_dict(self):
        """Return object data in easily serializable format"""
        # Handle timestamp conversion safely
        if self.timestamp is None:
            timestamp_str = None
        elif isinstance(self.timestamp, datetime):
            timestamp_str = self.timestamp.isoformat()
        else:
            # If it's already a string or some other format, return as is
            timestamp_str = self.timestamp
            
        return {
            'id': self.id,
            'timestamp': timestamp_str,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'uv_intensity': self.uv_intensity,
            'rainfall': self.rainfall,
            'soil_moisture_level': self.soil_moisture_level,
            'ph_level': self.ph_level,
            'tank_water_volume': self.tank_water_volume,
            'water_pressure': self.water_pressure,
            # Add other fields as needed
        }


class Device(db.Model):
    """Model for controllable devices"""
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)
    # Identifier used to control the hardware (e.g., MQTT topic, API endpoint ID)
    control_id = db.Column(db.String(100), unique=True, nullable=False)
    # User-friendly name for the device
    name = db.Column(db.String(100), nullable=False)
    # Type of device (e.g., 'PUMP', 'VALVE', 'LIGHT') - useful for UI rendering
    device_type = db.Column(db.String(50), nullable=False)
    # Current status (e.g., 'ON', 'OFF', 'OPEN', 'CLOSED', 'ERROR', 'UNKNOWN')
    # This might be better stored in a separate status table or cache (like Redis)
    # for frequent updates, but keeping it simple for now.
    status = db.Column(db.String(50), default='UNKNOWN')
    # Timestamp of the last status update
    last_status_update = db.Column(db.TIMESTAMP(timezone=True))
    # Is the device currently enabled for control via the UI?
    is_enabled = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Device {self.name} ({self.control_id})>'

    def to_dict(self):
        """Return object data in easily serializable format"""
        # Handle timestamp conversion safely
        if self.last_status_update is None:
            timestamp_str = None
        elif isinstance(self.last_status_update, datetime):
            timestamp_str = self.last_status_update.isoformat()
        else:
            # If it's already a string or some other format, return as is
            timestamp_str = self.last_status_update
            
        return {
            'id': self.id,
            'control_id': self.control_id,
            'name': self.name,
            'device_type': self.device_type,
            'status': self.status,
            'last_status_update': timestamp_str,
            'is_enabled': self.is_enabled,
        }
