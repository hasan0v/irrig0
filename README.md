# İrrigo - Smart Irrigation Management System

## Overview
İrrigo is a sophisticated irrigation management system designed to monitor and control agricultural irrigation systems. It provides real-time monitoring of environmental conditions, soil status, and water management through a web-based interface.

## Features
- **Real-time Monitoring**
  - Temperature and humidity tracking
  - UV intensity measurement
  - Rainfall monitoring
  - Soil moisture and pH levels
  - Water tank volume and pressure monitoring

- **Device Control**
  - Remote control of irrigation devices
  - Automated safety interlocks
  - Device status monitoring
  - Real-time device state updates

- **Data Analysis**
  - Historical data tracking
  - Data visualization
  - Trend analysis
  - Customizable date ranges for analysis

- **Security**
  - User authentication system
  - Password protection
  - Session management
  - Secure API endpoints

## Technology Stack
- **Backend**: Flask (Python)
- **Database**: SQLAlchemy with support for:
  - SQLite (development)
  - MySQL (production)
- **Frontend**: 
  - HTML/CSS
  - JavaScript
  - Material Design
  - Bootstrap Icons

## Prerequisites
- Python 3.x
- MySQL (for production)
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd Irrigo
```

2. Create a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
Create a `.env` file in the root directory with:
```
DATABASE_URL=mysql+pymysql://user:password@localhost/irrigodb
SECRET_KEY=your-secret-key
```

5. Initialize the database:
```bash
flask init-db
```

## Running the Application

1. Start the development server:
```bash
python run.py
```

2. Access the application at `http://localhost:5000`

3. Default login credentials:
   - Username: admin
   - Password: irrigoadmin
   (Change these immediately after first login)

## Project Structure
```
Irrigo/
├── app/
│   ├── templates/    # HTML templates
│   ├── static/       # CSS, JS, and other static files
│   ├── models.py     # Database models
│   ├── auth.py       # Authentication logic
│   ├── database.py   # Database configuration
│   └── app.py        # Main application file
├── requirements.txt  # Python dependencies
├── run.py           # Application entry point
└── db_init.py       # Database initialization script
```

## API Endpoints

- `/api/overview_status` - Get latest sensor data
- `/api/soil_status` - Get soil condition data
- `/api/tank_status` - Get water tank status
- `/api/water_quality` - Get water quality metrics
- `/api/devices` - List all controllable devices
- `/api/historical_data` - Get historical sensor data

## Development Tools

- `create_tables.py` - Database schema creation
- `add_demo_devices.py` - Add test devices
- `add_demo_sensor_data.py` - Add test sensor data
- `check_tables.py` - Database integrity verification

## Contributing
Please read [CONTRIBUTING.md] for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Support
For support and queries, please create an issue in the repository or contact the development team.

---
Last updated: April 23, 2025
