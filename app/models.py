from app.database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Enum # Added ForeignKey and Enum
import enum # Added enum import

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

    # Renamed from 'temperature'
    air_temperature = db.Column(db.Float, comment='Unit: °C. Source: Air')
    humidity = db.Column(db.Float, comment='Unit: %')
    uv_intensity = db.Column(db.Float, comment='Unit: Index or W/m²')
    rainfall = db.Column(db.Float, comment='Unit: mm')
    atmospheric_pressure = db.Column(db.Float, comment='Unit: hPa')

    # Soil Conditions
    soil_moisture_level = db.Column(db.Float, comment='Unit: %')
    soil_temperature = db.Column(db.Float, comment='Unit: °C')
    # Renamed from 'ph_level'
    soil_ph = db.Column(db.Float, comment='Source: Soil')
    soil_ec = db.Column(db.Float, comment='Unit: µS/cm')
    # Replaced 'soil_npk' string
    soil_n = db.Column(db.Float, comment='Unit: mg/kg')
    soil_p = db.Column(db.Float, comment='Unit: mg/kg')
    soil_k = db.Column(db.Float, comment='Unit: mg/kg')
    # Renamed from 'soil_sap_moisture'
    sap_moisture = db.Column(db.Float, comment='Unit: %')

    # Water Tank Status
    tank_water_volume = db.Column(db.Float, comment='Unit: Liters. Clean water tank')
    # Renamed from 'dirty_tank_volume'
    dirty_water_volume = db.Column(db.Float, comment='Unit: Liters. Wastewater tank')
    # Renamed from 'pump_pressure' - Matches original schema
    water_pressure = db.Column(db.Float, comment='Unit: bar or psi')
    # Renamed from 'water_treatment_rate'
    treatment_rate = db.Column(db.Float, comment='Unit: L/min')

    # Water Quality
    water_temperature = db.Column(db.Float, comment='Unit: °C')
    water_ph = db.Column(db.Float, comment='Source: Water')
    water_ec = db.Column(db.Float, comment='Unit: µS/cm')
    water_tds = db.Column(db.Float, comment='Unit: mg/L')
    water_flow_rate = db.Column(db.Float, comment='Unit: L/min')
    # Renamed from 'water_turbidity'
    water_ntu = db.Column(db.Float, comment='Unit: NTU')
    # Added
    water_nh3 = db.Column(db.Float, comment='Unit: mg/L')
    water_no3 = db.Column(db.Float, comment='Unit: mg/L')

    # Plant Environment
    light_par = db.Column(db.Float, comment='Unit: µmol/m²/s')
    co2_concentration = db.Column(db.Float, comment='Unit: ppm')
    # Note: air_temperature already defined above

    # Removed fields not in the updated schema:
    # water_orp, water_do, wind_speed, wind_direction,
    # clean_water_processed, used_water_processed,
    # system_power_usage, battery_level

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

        # Return all fields defined in the model
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # Ensure timestamp is ISO format string
        if data.get('timestamp') and isinstance(data['timestamp'], datetime):
             data['timestamp'] = data['timestamp'].isoformat()
        elif data.get('timestamp') is None:
             data['timestamp'] = None # Explicitly set None if it was None

        return data


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


# Enum for Alarm Status
class AlarmStatus(enum.Enum):
    ACTIVE = 'active'
    ACKNOWLEDGED = 'acknowledged'
    CLEARED = 'cleared'

# Enum for Alarm Severity
class AlarmSeverity(enum.Enum):
    INFO = 'info'
    WARNING = 'warning'
    CRITICAL = 'critical'

# Enum for Alarm Rule Condition
class AlarmCondition(enum.Enum):
    GREATER_THAN = '>'
    LESS_THAN = '<'
    EQUALS = '='


class Alarm(db.Model):
    """Model for generated alarms"""
    __tablename__ = 'alarms'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.TIMESTAMP(timezone=True), nullable=False, server_default=db.func.now(), index=True)
    device_id = db.Column(db.Integer, ForeignKey('devices.id'), nullable=True) # Can be null if it's a system-wide alarm? Or link to a specific sensor? For now, link to device.
    alarm_type = db.Column(db.String(100), nullable=False, comment="e.g., 'Sensor Threshold Exceeded', 'Device Offline'")
    severity = db.Column(Enum(AlarmSeverity), nullable=False, default=AlarmSeverity.WARNING)
    status = db.Column(Enum(AlarmStatus), nullable=False, default=AlarmStatus.ACTIVE, index=True)
    details = db.Column(db.Text, nullable=True, comment="More details about the alarm, e.g., 'Temperature 35°C exceeded threshold 30°C'")
    # Optional: Link to the rule that triggered this alarm
    triggered_by_rule_id = db.Column(db.Integer, ForeignKey('alarm_rules.id'), nullable=True)

    device = relationship("Device") # Relationship to Device model
    triggered_by_rule = relationship("AlarmRule") # Relationship to AlarmRule model

    def __repr__(self):
        return f'<Alarm {self.id} ({self.alarm_type}) - {self.status.value}>'

    def to_dict(self):
        """Return object data in easily serializable format"""
        timestamp_str = self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp
        return {
            'id': self.id,
            'timestamp': timestamp_str,
            'device_id': self.device_id,
            'device_name': self.device.name if self.device else None, # Include device name
            'alarm_type': self.alarm_type,
            'severity': self.severity.value, # Return enum value
            'status': self.status.value, # Return enum value
            'details': self.details,
            'triggered_by_rule_id': self.triggered_by_rule_id,
        }


class AlarmRule(db.Model):
    """Model for user-defined alarm rules"""
    __tablename__ = 'alarm_rules'

    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False) # Link to user if rules are user-specific
    name = db.Column(db.String(100), nullable=False, comment="User-friendly name for the rule")
    # Target specific device or all devices of a type? Let's start with specific device.
    device_id = db.Column(db.Integer, ForeignKey('devices.id'), nullable=False)
    # Which sensor reading to monitor (must match a column name in SensorData)
    sensor_metric = db.Column(db.String(100), nullable=False, comment="e.g., 'air_temperature', 'soil_moisture_level'")
    condition = db.Column(Enum(AlarmCondition), nullable=False)
    threshold_value = db.Column(db.Float, nullable=False)
    severity = db.Column(Enum(AlarmSeverity), nullable=False, default=AlarmSeverity.WARNING)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    # Optional: Cooldown period in seconds to avoid spamming alarms
    cooldown_period_seconds = db.Column(db.Integer, default=300) # 5 minutes default

    # user = relationship("User") # Relationship to User model
    device = relationship("Device") # Relationship to Device model

    def __repr__(self):
        return f'<AlarmRule {self.id} ({self.name}) - Device {self.device_id}>'

    def to_dict(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            # 'user_id': self.user_id,
            'name': self.name,
            'device_id': self.device_id,
            'device_name': self.device.name if self.device else None, # Include device name
            'sensor_metric': self.sensor_metric,
            'condition': self.condition.value, # Return enum value
            'threshold_value': self.threshold_value,
            'severity': self.severity.value, # Return enum value
            'is_active': self.is_active,
            'cooldown_period_seconds': self.cooldown_period_seconds,
        }
