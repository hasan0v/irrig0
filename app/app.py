import os
import click # Import click for CLI commands
from dotenv import load_dotenv # Import dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session, g, jsonify
from app.database import db, init_app as init_db_app # Use alias to avoid name clash
from app.models import User, SensorData, Device # Import the User, SensorData, and Device models
from app.auth import login_required # Import the decorator
from datetime import datetime  # Add datetime import for historical data

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
        return jsonify({
            'timestamp': None,
            'temperature': None,
            'humidity': None,
            'uv_intensity': None,
            'rainfall': None,
            # Add other relevant fields with null/default values
            'soil_moisture_level': None, # Added for consistency
            'ph_level': None,            # Added for consistency
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
            'soil_temperature': latest_data.temperature, # Assuming temperature is soil temp for now (FR-DASH-B01) - Needs clarification
            'soil_moisture_level': latest_data.soil_moisture_level, # FR-DASH-B02
            'ph_level': latest_data.ph_level, # Assuming this is soil pH for now (FR-DASH-B03) - Needs clarification
            # Placeholders for other soil data (EC, NPK, SAP) - FR-DASH-B04, B05, B06
            'soil_ec': None,
            'soil_npk': None,
            'sap_moisture': None,
        })
    else:
        # Return empty object or default values if no data exists
        return jsonify({
            'timestamp': None,
            'soil_temperature': None,
            'soil_moisture_level': None,
            'ph_level': None,
            'soil_ec': None,
            'soil_npk': None,
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
            'tank_water_volume': latest_data.tank_water_volume, # FR-DASH-E01 (Assuming clean tank)
            'pump_pressure': latest_data.water_pressure, # FR-DASH-E03 (Assuming relevant pump)
            # Placeholders for other tank data
            'dirty_tank_volume': None, # FR-DASH-E02
            'system_water_treatment_rate': None, # FR-DASH-E04
        })
    else:
        # Return empty object or default values if no data exists
        return jsonify({
            'timestamp': None,
            'tank_water_volume': None,
            'pump_pressure': None,
            'dirty_tank_volume': None,
            'system_water_treatment_rate': None,
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
            
    # Try to use existing ambiguous fields if they *might* represent water data
    water_temp = latest_data.temperature if latest_data else None # Needs clarification
    water_ph = latest_data.ph_level if latest_data else None # Needs clarification

    return jsonify({
        'timestamp': timestamp,
        # Core items from STORY-007 / FR-DASH-C
        'water_temperature': water_temp, # FR-DASH-C01 (Source TBD)
        'ph': water_ph,                  # FR-DASH-C02 (Source TBD)
        'ec': None,                      # FR-DASH-C03 (Source TBD)
        'tds': None,                     # FR-DASH-C04 (Source TBD)
        'flow_rate': None,               # FR-DASH-C13 (Source TBD)
        # Other placeholders from FR-DASH-C
        'ntu': None,
        'ammonia': None,
        'nitrate': None,
        'phosphate': None,
        'potassium': None,
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
            
    air_temp = latest_data.temperature if latest_data else None # FR-DASH-D03 (Assuming air temp)
    soil_moisture = latest_data.soil_moisture_level if latest_data else None # FR-DASH-D04
    soil_temp = latest_data.temperature if latest_data else None # FR-DASH-D05 (Assuming soil temp - ambiguous)

    return jsonify({
        'timestamp': timestamp,
        # Items from STORY-008 / FR-DASH-D
        'light_par': None,              # FR-DASH-D01 (Source TBD)
        'co2_concentration': None,      # FR-DASH-D02 (Source TBD)
        'air_temperature': air_temp,
        'soil_moisture': soil_moisture, # Cross-ref B02
        'soil_temperature': soil_temp,  # Cross-ref B01
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

# History page route (TASK-061)
@app.route('/history')
@login_required
def history():
    """Renders the historical data page."""
    return render_template('history.html')


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
        # Example: Don't allow opening drainage valve if water quality is poor
        if action.upper() == 'OPEN' and 'DRAIN' in device_type and latest_data.ph_level is not None:
            # Example condition: pH too high or too low
            if latest_data.ph_level < 5 or latest_data.ph_level > 9:
                result['blocked'] = True
                result['reason'] = f'Water pH level unsafe: {latest_data.ph_level}'
                result['conditions']['ph_level'] = latest_data.ph_level
                return result
    
    # Add other device-specific checks as needed...
    
    return result

# --- Main Execution ---
if __name__ == '__main__':
    # Click is already imported at the top
    app.run(debug=True)
