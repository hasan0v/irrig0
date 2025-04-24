import os
import click # Import click for CLI commands
from dotenv import load_dotenv # Import dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session, g, jsonify
from app.database import db, init_app as init_db_app # Use alias to avoid name clash
from app.models import User, SensorData, Device # Import the User, SensorData, and Device models
from app.auth import login_required # Import the decorator
from app.alarms_api import alarms_bp # Import the alarms blueprint
from datetime import datetime, timedelta  # Add datetime and timedelta import for historical data

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Generate a secret key for session management
# In a real app, use a more secure method like os.urandom(24)
# and store it securely, not hardcoded.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key') # Use environment variable or default
# Configure the database URI (replace with your actual connection string)
# Example for PostgreSQL: 'postgresql://user:password@host:port/database'
# Example for MySQL: 'mysql+pymysql://user:password@host:port/database'
# Example for SQLite: 'sqlite:///instance/irrigodb.sqlite'
# Read database URI from environment variable, with a default fallback to SQLite
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///instance/irrigodb.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable modification tracking

# Initialize the database with the app
init_db_app(app)

# Function to create a default admin user if none exists
def create_default_user():
    """Create a default admin user if no users exist in the database."""
    with app.app_context():
        if User.query.count() == 0:
            print("No users found. Creating default admin user...")
            admin = User(username="admin")
            admin.set_password("irrigoadmin")  # You should change this to a more secure password
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created. Username: admin, Password: irrigoadmin")

# Create default user if none exists
create_default_user()

# --- Hooks ---

@app.before_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into flask.g.user."""
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)
        # Store username in session for easy access in templates (like base.html navbar)
        session['username'] = g.user.username if g.user else None


# --- Routes ---

@app.route('/')
@login_required # Apply the decorator
def index():
    # User is guaranteed to be logged in by the decorator
    # g.user is available from the before_request hook
    # Later, this will render the main dashboard template
    return render_template('dashboard.html', user=g.user) # Pass user to template


# --- API Endpoints ---

@app.route('/api/overview_status')
@login_required
def api_overview_status():
    """API endpoint to get the latest sensor data for the overview header."""
    latest_data = SensorData.query.order_by(SensorData.timestamp.desc()).first()
    if latest_data:
        return jsonify(latest_data.to_dict())
    else:
        # Return empty object or default values if no data exists
        # Use updated field names for consistency
        return jsonify({
            'timestamp': None,
            'air_temperature': None, # Changed
            'humidity': None,
            'uv_intensity': None,
            'rainfall': None,
            'atmospheric_pressure': None, # Added
            'soil_moisture_level': None,
            'soil_ph': None,            # Changed
            # Add others as needed for a complete null response if desired
        })

@app.route('/api/soil_status')
@login_required
def api_soil_status():
    """API endpoint to get the latest soil condition data."""
    latest_data = SensorData.query.order_by(SensorData.timestamp.desc()).first()
    if latest_data:
        # Safe timestamp handling
        timestamp = None
        if latest_data.timestamp:
            if hasattr(latest_data.timestamp, 'isoformat'):
                timestamp = latest_data.timestamp.isoformat()
            else:
                timestamp = latest_data.timestamp
                
        # Return only relevant fields for soil status
        return jsonify({
            'timestamp': timestamp,
            'soil_temperature': latest_data.soil_temperature, # Use specific soil_temperature (FR-DASH-B01)
            'soil_moisture_level': latest_data.soil_moisture_level, # FR-DASH-B02
            'ph_level': latest_data.soil_ph, # Use specific soil_ph (FR-DASH-B03)
            # Use actual fields from model if available
            'soil_ec': latest_data.soil_ec, # FR-DASH-B04
            'soil_n': latest_data.soil_n,   # Part of FR-DASH-B05
            'soil_p': latest_data.soil_p,   # Part of FR-DASH-B05
            'soil_k': latest_data.soil_k,   # Part of FR-DASH-B05
            'sap_moisture': latest_data.sap_moisture, # FR-DASH-B06
        })
    else:
        # Return empty object or default values if no data exists
        return jsonify({
            'timestamp': None,
            'soil_temperature': None,
            'soil_moisture_level': None,
            # 'ph_level': None, # Remove old name
            'soil_ph': None, # Keep updated name
            'soil_ec': None,
            'soil_n': None,
            'soil_p': None, # Changed from soil_npk
            'soil_k': None, # Changed from soil_npk
            'sap_moisture': None,
        })

@app.route('/api/tank_status')
@login_required
def api_tank_status():
    """API endpoint to get the latest water tank status data."""
    latest_data = SensorData.query.order_by(SensorData.timestamp.desc()).first()
    if latest_data:
        # Safe timestamp handling
        timestamp = None
        if latest_data.timestamp:
            if hasattr(latest_data.timestamp, 'isoformat'):
                timestamp = latest_data.timestamp.isoformat()
            else:
                timestamp = latest_data.timestamp
                
        # Return only relevant fields for tank status
        return jsonify({
            'timestamp': timestamp,
            'tank_water_volume': latest_data.tank_water_volume, # FR-DASH-E01
            'pump_pressure': latest_data.water_pressure, # FR-DASH-E03 - Corrected model name is water_pressure
            # Populate actual data for fields previously placeholders
            'dirty_tank_volume': latest_data.dirty_water_volume, # FR-DASH-E02 - Use actual data
            'system_water_treatment_rate': latest_data.treatment_rate, # FR-DASH-E04 - Use actual data (treatment_rate)
        })
    else:
        # Return empty object or default values if no data exists
        return jsonify({
            'timestamp': None,
            'tank_water_volume': None,
            'pump_pressure': None, # Corresponds to water_pressure
            'dirty_tank_volume': None,
            'system_water_treatment_rate': None, # Corresponds to treatment_rate
        })

@app.route('/api/water_quality')
@login_required
def api_water_quality():
    """API endpoint to get latest water quality data (Post-Treatment)."""
    # Placeholder implementation as most sensors are TBD (FR-DASH-C)
    latest_data = SensorData.query.order_by(SensorData.timestamp.desc()).first()
    
    # Safe timestamp handling
    timestamp = None
    if latest_data and latest_data.timestamp:
        if hasattr(latest_data.timestamp, 'isoformat'):
            timestamp = latest_data.timestamp.isoformat()
        else:
            timestamp = latest_data.timestamp
            
    # Use specific water quality fields from the updated model
    water_temp = latest_data.water_temperature if latest_data else None
    water_ph = latest_data.water_ph if latest_data else None

    return jsonify({
        'timestamp': timestamp,
        # Core items from STORY-007 / FR-DASH-C - Populate with actual data
        'water_temperature': water_temp, # FR-DASH-C01
        'ph': water_ph,                  # FR-DASH-C02 - Use water_ph
        'ec': latest_data.water_ec if latest_data else None, # FR-DASH-C03 - Use actual data
        'tds': latest_data.water_tds if latest_data else None, # FR-DASH-C04 - Use actual data
        'flow_rate': latest_data.water_flow_rate if latest_data else None, # FR-DASH-C13 - Use actual data
        # Other placeholders from FR-DASH-C - Populate with actual data
        'ntu': latest_data.water_ntu if latest_data else None, # Use actual data
        'ammonia': latest_data.water_nh3 if latest_data else None, # Use actual data (nh3)
        'nitrate': latest_data.water_no3 if latest_data else None, # Use actual data (no3)
        # 'phosphate': None, # Not in current model
        # 'potassium': None, # Not in current model
        'sulfate': None,
        # etc.
    })

@app.route('/api/plant_env')
@login_required
def api_plant_env():
    """API endpoint to get latest plant environmental factors."""
    # Placeholder implementation as sensors are TBD (FR-DASH-D)
    latest_data = SensorData.query.order_by(SensorData.timestamp.desc()).first()
    
    # Safe timestamp handling
    timestamp = None
    if latest_data and latest_data.timestamp:
        if hasattr(latest_data.timestamp, 'isoformat'):
            timestamp = latest_data.timestamp.isoformat()
        else:
            timestamp = latest_data.timestamp
            
    # Use specific fields from the updated model
    air_temp = latest_data.air_temperature if latest_data else None # FR-DASH-D03
    soil_moisture = latest_data.soil_moisture_level if latest_data else None # FR-DASH-D04
    soil_temp = latest_data.soil_temperature if latest_data else None # FR-DASH-D05

    return jsonify({
        'timestamp': timestamp,
        # Items from STORY-008 / FR-DASH-D - Populate with actual data
        'light_par': latest_data.light_par if latest_data else None, # FR-DASH-D01 - Use actual data
        'co2_concentration': latest_data.co2_concentration if latest_data else None, # FR-DASH-D02 - Use actual data
        'air_temperature': air_temp,    # Already corrected
        'soil_moisture': soil_moisture, # Already correct
        'soil_temperature': soil_temp,  # Already corrected
    })

@app.route('/api/devices')
@login_required
def api_devices():
    """API endpoint to list controllable devices and their status."""
    # In a real system, fetching status might involve querying hardware/cache.
    # Here, we just return the status stored in the DB.
    devices = Device.query.all()
    
    # TASK-057: Include interlock status in the response
    device_data = []
    for device in devices:
        # Get device data including interlock status
        device_dict = device.to_dict()
        
        # Check ON and OPEN actions for interlocks
        if device.device_type and 'VALVE' in device.device_type.upper():
            action_to_check = 'OPEN'
        else:
            action_to_check = 'ON'
            
        # Add interlock information
        interlock = check_safety_interlocks(device, action_to_check)
        device_dict['interlock'] = interlock
        
        device_data.append(device_dict)
    
    return jsonify(device_data)

# Control Device API Endpoint (TASK-051)
@app.route('/api/control_device/<control_id>', methods=['POST'])
@login_required
def api_control_device(control_id):
    """API endpoint to control a device by its control_id."""
    # Validate the request payload
    if not request.is_json:
        return jsonify({'error': 'Invalid request format. JSON required.'}), 400
    
    data = request.json
    action = data.get('action')
    
    if not action:
        return jsonify({'error': 'Missing required parameter: action'}), 400
    
    # Find the device in the database
    device = Device.query.filter_by(control_id=control_id).first()
    if not device:
        return jsonify({'error': f'Device not found with control_id: {control_id}'}), 404
    
    # Check if device is enabled
    if not device.is_enabled:
        return jsonify({'error': 'Device is disabled and cannot be controlled'}), 403
    
    # TASK-056: Check safety interlocks before executing commands
    interlock_status = check_safety_interlocks(device, action)
    if interlock_status['blocked']:
        return jsonify({
            'error': 'Safety interlock active',
            'message': interlock_status['reason'],
            'device': device.to_dict(),
            'interlock': interlock_status
        }), 403
    
    # Implement basic safety checks (would be expanded in STORY-013)
    # For now, just check basic device type compatibility with action
    valid_actions = {
        'PUMP': ['ON', 'OFF'],
        'VALVE': ['OPEN', 'CLOSE'],
        'LIGHT': ['ON', 'OFF'],
        'FAN': ['ON', 'OFF'],
        'HEATER': ['ON', 'OFF'],
        'GENERIC': ['ON', 'OFF']
    }
    
    device_type = device.device_type.upper()
    standard_type = next((k for k in valid_actions.keys() if k in device_type), 'GENERIC')
    
    if action.upper() not in valid_actions.get(standard_type, ['ON', 'OFF']):
        return jsonify({
            'error': f'Invalid action {action} for device type {device.device_type}. '
                     f'Valid actions are: {", ".join(valid_actions.get(standard_type, ["ON", "OFF"]))}'
        }), 400
    
    # Here we would connect to the actual hardware interface
    # For now, we'll simulate success and update the database
    
    # Map actions to standard status values
    action_to_status = {
        'ON': 'ON',
        'OFF': 'OFF',
        'OPEN': 'OPEN',
        'CLOSE': 'CLOSED',
        'START': 'RUNNING',
        'STOP': 'IDLE'
    }
    
    # Update device status in database
    device.status = action_to_status.get(action.upper(), action.upper())
    device.last_status_update = db.func.now()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Device {device.name} ({control_id}) {action} command sent successfully',
        'device': device.to_dict()
    })

# Historical Data API Endpoint (TASK-059)
@app.route('/api/historical_data')
@login_required
def api_historical_data():
    """API endpoint to retrieve historical sensor data for charting."""
    # Parse request parameters
    sensors = request.args.get('sensors', '').split(',')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    # Validate parameters
    if not sensors or sensors == ['']:
        return jsonify({'error': 'No sensors specified'}), 400
        
    valid_fields = [c.name for c in SensorData.__table__.columns 
                   if c.name not in ['id']]
    
    # Filter out invalid sensor names
    valid_sensors = [s for s in sensors if s in valid_fields]
    if not valid_sensors:
        return jsonify({
            'error': 'No valid sensors specified',
            'valid_fields': valid_fields
        }), 400
    
    # Build query
    query = db.session.query(SensorData.timestamp, *[getattr(SensorData, field) for field in valid_sensors])
    
    # Apply time filters if provided
    if start_time:
        try:
            # Parse ISO format or timestamp
            start_datetime = datetime.fromisoformat(start_time)
            query = query.filter(SensorData.timestamp >= start_datetime)
        except (ValueError, TypeError):
            return jsonify({'error': f'Invalid start_time format: {start_time}. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
    
    if end_time:
        try:
            # Parse ISO format or timestamp
            end_datetime = datetime.fromisoformat(end_time)
            query = query.filter(SensorData.timestamp <= end_datetime)
        except (ValueError, TypeError):
            return jsonify({'error': f'Invalid end_time format: {end_time}. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
    
    # Get the number of data points
    count = query.count()
    
    # TASK-060: Handle potentially large datasets with aggregation
    # For large datasets, automatically apply aggregation
    aggregation = request.args.get('aggregation', 'auto')
    max_points = int(request.args.get('max_points', 1000))
    
    if aggregation == 'auto' and count > max_points:
        # Calculate time interval for aggregation
        if start_time and end_time:
            # Simple downsampling by limiting the query with order_by and limit
            query = query.order_by(SensorData.timestamp)
            # Get approximately max_points evenly distributed records
            step = count // max_points
            if step < 1:
                step = 1
                
            # Use SQLAlchemy pagination to get evenly distributed samples
            result = []
            for i in range(0, count, step):
                page_items = query.offset(i).limit(1).all()
                if page_items:
                    result.extend(page_items)
        else:
            # If no time range, just limit to the latest max_points
            query = query.order_by(SensorData.timestamp.desc()).limit(max_points)
            result = query.all()
            result.reverse()  # Reverse to get chronological order
    else:
        # No aggregation needed, return all points in time order
        result = query.order_by(SensorData.timestamp).all()
    
    # Format the result for the frontend
    data = {
        'timestamps': [],
        'sensors': {field: [] for field in valid_sensors}
    }
    
    for row in result:
        # Format timestamp consistently
        timestamp = row[0].isoformat() if hasattr(row[0], 'isoformat') else str(row[0])
        data['timestamps'].append(timestamp)
        
        # Add sensor values
        for i, field in enumerate(valid_sensors):
            # Row[0] is timestamp, data starts at index 1
            data['sensors'][field].append(row[i+1])
    
    # Add metadata
    data['metadata'] = {
        'count': len(result),
        'original_count': count,
        'aggregated': count > len(result),
        'sensors_requested': sensors,
        'valid_sensors': valid_sensors,
        'start_time': start_time,
        'end_time': end_time
    }
    
    return jsonify(data)

# --- Page Routes ---

@app.route('/control')
@login_required
def control():
    """Renders the device control page."""
    return render_template('control.html')

# Dashboard data API endpoint for history page
@app.route('/api/history_dashboard')
@login_required
def api_history_dashboard():
    """API endpoint to get summary data for the history page dashboard."""
    try:
        # Get total count of data points
        total_points = SensorData.query.count()
        
        # Get the number of active sensors (with data in the last 24 hours)
        one_day_ago = datetime.now() - timedelta(days=1)
        recent_data = SensorData.query.filter(SensorData.timestamp >= one_day_ago).order_by(SensorData.timestamp.desc()).first()
        
        # Count non-null values in the most recent record as "active sensors"
        active_sensors = 0
        if recent_data:
            # Convert to dictionary and count non-null values
            recent_dict = recent_data.to_dict()
            active_sensors = sum(1 for k, v in recent_dict.items() 
                             if k != 'timestamp' and v is not None and v != "")
        
        # Get timestamp range
        first_record = SensorData.query.order_by(SensorData.timestamp.asc()).first()
        last_record = SensorData.query.order_by(SensorData.timestamp.desc()).first()
        
        # Calculate time range
        time_range = None
        last_update = None
        if first_record and last_record:
            time_range = {
                'start': first_record.timestamp.isoformat() if hasattr(first_record.timestamp, 'isoformat') else str(first_record.timestamp),
                'end': last_record.timestamp.isoformat() if hasattr(last_record.timestamp, 'isoformat') else str(last_record.timestamp),
            }
            last_update = time_range['end']
        
        # Get top 5 sensors with most recent data for trend chart
        top_sensors = []
        if last_record:
            data_dict = last_record.to_dict()
            # Filter out non-numeric and empty values
            top_sensors = [k for k, v in data_dict.items() 
                          if k != 'timestamp' and v is not None and v != "" and isinstance(v, (int, float))][:5]
        
        # Get trend data for last 24 hours
        trend_data = []
        if top_sensors:
            recent_records = SensorData.query.filter(SensorData.timestamp >= one_day_ago).order_by(SensorData.timestamp.asc()).all()
            if recent_records:
                trend_data = {
                    'timestamps': [r.timestamp.isoformat() if hasattr(r.timestamp, 'isoformat') else str(r.timestamp) for r in recent_records],
                    'sensors': {sensor: [getattr(r, sensor) for r in recent_records] for sensor in top_sensors}
                }
        
        # Get category distribution
        category_counts = {
            'Genel Hava Durumu': 0,
            'Toprak Koşulları': 0,
            'Su Kalitesi': 0,
            'Bitki Ortamı': 0,
            'Tank Durumu': 0,
            'Diğer': 0
        }
        
        # Simple mapping of sensors to categories
        sensor_to_category = {
            'air_temperature': 'Genel Hava Durumu',
            'humidity': 'Genel Hava Durumu',
            'atmospheric_pressure': 'Genel Hava Durumu',
            'soil_moisture_level': 'Toprak Koşulları',
            'soil_temperature': 'Toprak Koşulları',
            'soil_ph': 'Toprak Koşulları',
            'soil_ec': 'Toprak Koşulları',
            'water_ph': 'Su Kalitesi',
            'water_temperature': 'Su Kalitesi',
            'water_ec': 'Su Kalitesi',
            'tank_water_volume': 'Tank Durumu',
            'water_pressure': 'Tank Durumu',
            'light_par': 'Bitki Ortamı',
            'co2_concentration': 'Bitki Ortamı'
        }
        
        # Count non-null values for each category
        if last_record:
            data_dict = last_record.to_dict()
            for sensor, value in data_dict.items():
                if sensor != 'timestamp' and value is not None and value != "":
                    category = sensor_to_category.get(sensor, 'Diğer')
                    category_counts[category] += 1
        
        # Filter out empty categories
        category_distribution = {k: v for k, v in category_counts.items() if v > 0}
        
        # Return all dashboard data
        return jsonify({
            'success': True,
            'data': {
                'total_points': total_points,
                'active_sensors': active_sensors,
                'last_update': last_update,
                'time_range': time_range,
                'trend_data': trend_data,
                'category_distribution': category_distribution
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# History page route (TASK-061)
@app.route('/history')
@login_required
def history():
    """Renders the historical data page."""
    return render_template('history.html')

@app.route('/alarms')
@login_required
def alarms():
    """Renders the alarms management page."""
    return render_template('alarms.html')


# Register blueprints
app.register_blueprint(alarms_bp)
# Note: Register other blueprints like auth_bp and dashboard_api_bp if they exist and are needed.
# Assuming they might be registered elsewhere or implicitly handled for now.


# --- Authentication Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    # Redirect if already logged in
    if g.user:
        return redirect(url_for('index'))

    """Handles user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        error = None
        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            error = 'Invalid username or password.'

        if error is None:
            # Store the user id in the session, clear previous data
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username # Store username as well
            flash('Login successful!', 'success')
            # Redirect to the 'next' URL if provided, otherwise to index
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))

        flash(error, 'danger') # Use flash categories for styling

    # If GET request or login failed, render the login form
    return render_template('login.html')

# Logout route (TASK-010 & TASK-011)
@app.route('/logout')
def logout():
    """Logs the user out."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# --- Database Initialization Command ---
# It's useful to have a command to create the initial database tables
@app.cli.command('init-db')
def init_db_command():
    """Clear existing data and create new tables."""
    # Need to create the 'instance' folder if it doesn't exist for SQLite
    instance_path = os.path.join(app.instance_path)
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        print(f"Created instance folder at {instance_path}")

    # Create tables based on models
    # Use app context
    with app.app_context():
        db.create_all()
    print('Initialized the database.')

@app.cli.command('create-user')
@click.argument('username')
@click.argument('password')
def create_user_command(username, password):
    """Creates a new user."""
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        print(f"User '{username}' already exists.")
        return

    new_user = User(username=username)
    new_user.set_password(password)
    with app.app_context():
        db.session.add(new_user)
        db.session.commit()
    print(f"User '{username}' created successfully.")


# --- Helper Functions ---

# TASK-056: Implement safety interlock logic
def check_safety_interlocks(device, action):
    """
    Check safety conditions before allowing device control.
    Returns dict with 'blocked' boolean and 'reason' if blocked.
    """
    # Get the latest sensor data
    latest_data = SensorData.query.order_by(SensorData.timestamp.desc()).first()
    
    # Default response (safe)
    result = {
        'blocked': False,
        'reason': None,
        'conditions': {}
    }
    
    # If no sensor data, allow control but note the warning
    if not latest_data:
        result['conditions']['warning'] = 'No sensor data available for safety checks'
        return result
    
    # Device-specific interlock checks
    device_type = device.device_type.upper()
    
    # Water pump interlocks
    if 'PUMP' in device_type and 'WATER' in device_type:
        # Check if tank has enough water
        if action.upper() == 'ON' and latest_data.tank_water_volume is not None:
            # Assume 10% is minimum safe level (you can adjust based on your requirements)
            if latest_data.tank_water_volume < 10:
                result['blocked'] = True
                result['reason'] = 'Insufficient water level in tank'
                result['conditions']['tank_water_volume'] = latest_data.tank_water_volume
                return result
                
    # Valve interlock example
    if 'VALVE' in device_type:
        # Example: Don't allow opening drainage valve if water quality is poor (use water_ph)
        if action.upper() == 'OPEN' and 'DRAIN' in device_type and latest_data.water_ph is not None:
            # Example condition: pH too high or too low
            if latest_data.water_ph < 5 or latest_data.water_ph > 9: # Check against water_ph
                result['blocked'] = True
                result['reason'] = f'Water pH level unsafe: {latest_data.water_ph}'
                result['conditions']['water_ph'] = latest_data.water_ph # Report water_ph
                return result
    
    # Add other device-specific checks as needed...
    
    return result

# --- Main Execution ---
if __name__ == '__main__':
    # Click is already imported at the top
    app.run(debug=True)
