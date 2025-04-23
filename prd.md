# Product Requirements Document: Irrigation & Environmental Monitoring System

**Version:** 1.0
**Date:** 2023-10-27
**Author:** AI Assistant (based on user input)

## 1. Introduction

### 1.1 Purpose
This document describes the functional and non-functional requirements for a web and mobile-accessible application designed to monitor and control an environmental and irrigation system. The system aggregates sensor data, presents it intuitively, allows for device control, provides historical insights, and alerts users to critical conditions.

### 1.2 Goals
*   Provide real-time visibility into environmental, soil, water quality, and system status.
*   Enable remote control of connected devices (pumps, valves).
*   Improve resource management efficiency (water, energy).
*   Alert users proactively to potential issues or required actions.
*   Offer historical data analysis for better decision-making.
*   Provide a user-friendly interface accessible via web browsers and potentially mobile devices.

### 1.3 Scope
*   **In Scope:**
    *   Development of a Flask-based web application backend.
    *   Development of a web frontend using HTML, CSS, JavaScript, Bootstrap, and Tailwind CSS (via CDN).
    *   Integration with the `irrigodb.sensordata` database table for reading sensor data.
    *   Display of real-time and historical sensor data as specified.
    *   User interface for controlling specific, defined devices.
    *   Basic user authentication (Login/Logout).
    *   Configurable alert system (in-app notifications initially).
    *   Responsive design for desktop and common mobile browser access.
*   **Out of Scope (for V1.0 unless specified otherwise):**
    *   Native mobile applications (iOS/Android).
    *   Advanced automation rule engine (complex "if-this-then-that" scenarios).
    *   Direct integration with external weather forecast APIs (beyond displaying potentially available sensor data like rainfall).
    *   Machine learning-based predictions or optimizations.
    *   User role management (multiple permission levels).
    *   Sensor provisioning or management interface.
    *   Direct hardware control protocols (assumes an abstraction layer exists or will be built separately for Flask to interact with hardware).

### 1.4 Target Audience / User Personas
*   **Primary:** Farm Manager / System Operator (e.g., "Alex"): Needs a quick overview, detailed data access, control capabilities, historical trends, and alerts for efficient daily management.
*   **Secondary:** Maintenance Technician: Needs device status, control for testing/repair, and possibly diagnostic information.
*   **Tertiary:** Researcher / Agronomist: Primarily interested in detailed historical data export and analysis.

## 2. Functional Requirements

### 2.1 User Authentication
*   **FR-AUTH-001:** Users must be required to log in to access the system dashboard and controls.
*   **FR-AUTH-002:** A basic login page shall be provided, accepting username/password.
*   **FR-AUTH-003:** A logout mechanism shall be provided.
*   **FR-AUTH-004:** Authentication state must be managed securely (e.g., using session cookies).

### 2.2 Dashboard ("Anlık Durum" - Current Status)
*   **FR-DASH-001:** The main page title shall be "Anlık Durum".
*   **FR-DASH-002:** The dashboard shall refresh data automatically at a configurable interval (default: 30 seconds) or via a manual refresh button.
*   **FR-DASH-003:** The dashboard shall display the "Last Updated" timestamp.
*   **FR-DASH-004:** The dashboard shall be structured logically, potentially using collapsible sections for detailed data.

*   **FR-DASH-A (Sticky Header / Overview):**
    *   **FR-DASH-A01:** This section shall remain fixed at the top of the viewport during vertical scrolling.
    *   **FR-DASH-A02:** Display current **Temperature** (`sensordata.temperature`, Unit: °C).
    *   **FR-DASH-A03:** Display current **Humidity** (`sensordata.humidity`, Unit: %).
    *   **FR-DASH-A04:** Display current **UV Intensity** (`sensordata.uv_intensity`, Unit: Index or W/m² - clarify unit). Use appropriate visualization (e.g., gauge, level indicator).
    *   **FR-DASH-A05:** Display recent **Rainfall** (`sensordata.rainfall`, Unit: mm - specify time period, e.g., last hour, last 24h).
    *   **FR-DASH-A06:** Display current **Atmospheric Pressure** (Source TBD - not in `sensordata`. Requires new sensor/column or external API - Mark as V.Next if unavailable).
    *   **FR-DASH-A07:** Display **Water Processed Today** (Source TBD - requires calculation or separate data). Display "Cleaned Water (Today)" and "Water Applied (Today)" in Liters.
    *   **FR-DASH-A08:** Use clear icons and labels for each metric.

*   **FR-DASH-B (Soil Conditions):**
    *   **FR-DASH-B01:** Display **Soil Temperature** (`sensordata.temperature` - Clarify if this is air temp or if a separate soil temp sensor exists/is needed). Unit: °C.
    *   **FR-DASH-B02:** Display **Soil Moisture** (`sensordata.soil_moisture_level`, Unit: %). Use a gauge or percentage bar.
    *   **FR-DASH-B03:** Display **Soil pH** (`sensordata.ph_level`). Use a color-coded indicator based on optimal ranges.
    *   **FR-DASH-B04:** Display **Soil EC** (Electrical Conductivity) (Source TBD - not in `sensordata`). Unit: µS/cm or mS/cm.
    *   **FR-DASH-B05:** Display **Soil N, P, K levels** (Source TBD - not in `sensordata`). Unit: mg/kg or ppm.
    *   **FR-DASH-B06:** Display **SAP Hydrogel Moisture** (Source TBD - requires specific sensor/logic). Unit: %.
    *   **FR-DASH-B07:** Clearly label each parameter and its unit. Provide tooltips for less common acronyms (EC, NPK, SAP).

*   **FR-DASH-C (Water Quality - Post-Treatment):**
    *   **FR-DASH-C01:** Display **Water Temperature** (Source TBD - could be same as `sensordata.temperature` if sensor is in water, or needs separate sensor). Unit: °C.
    *   **FR-DASH-C02:** Display **pH** (`sensordata.ph_level` - Clarify if this is soil pH or water pH, likely needs separate sensor for water).
    *   **FR-DASH-C03:** Display **EC** (Electrical Conductivity) (Source TBD - needs water EC sensor). Unit: µS/cm.
    *   **FR-DASH-C04:** Display **TDS** (Total Dissolved Solids) (Source TBD - often calculated from EC, or needs sensor). Unit: mg/L (ppm).
    *   **FR-DASH-C05:** Display **NTU** (Turbidity) (Source TBD - needs turbidity sensor). Unit: NTU. Use qualitative indicator (Clear, Cloudy, Turbid).
    *   **FR-DASH-C06:** Display **Ammonia** (NH₃/NH₄⁺) (Source TBD - needs sensor). Unit: mg/L.
    *   **FR-DASH-C07:** Display **Nitrate** (NO₃⁻) (Source TBD - needs sensor). Unit: mg/L.
    *   **FR-DASH-C08:** Display **Phosphate** (PO₄³⁻) (Source TBD - needs sensor). Unit: mg/L.
    *   **FR-DASH-C09:** Display **Potassium** (K⁺) (Source TBD - needs sensor). Unit: mg/L.
    *   **FR-DASH-C10:** Display **Sulfate** (SO₄²⁻) (Source TBD - needs sensor). Unit: mg/L.
    *   **FR-DASH-C11:** Display **Heavy Metals** (Pb, Cd, As, Hg, Zn, Cu) (Source TBD - needs specific sensors, often complex/expensive). Indicate Presence/Absence or concentration if available. Unit: µg/L or mg/L. Mark as V.Next if sensors unavailable.
    *   **FR-DASH-C12:** Display **SAR** (Sodium Adsorption Ratio) (Calculated value - requires Na, Ca, Mg sensors - Source TBD).
    *   **FR-DASH-C13:** Display **Water Flow Rate / Debi** (`sensordata.water_pressure` might relate, but likely needs dedicated flow meter). Unit: L/min or m³/h.
    *   **FR-DASH-C14:** Display **Pre-Treatment Pollution Index** (Requires calculation based on input water quality - Source TBD).
    *   **FR-DASH-C15:** Display **Treatment Efficiency Ratio** (Requires calculation comparing pre/post treatment data - Source TBD).
    *   **FR-DASH-C16:** Due to the number of parameters, provide a summary view with critical items (e.g., pH, EC, TDS, Flow Rate) and an expandable "Details" section.

*   **FR-DASH-D (Plant Environmental Factors):**
    *   **FR-DASH-D01:** Display **Light Intensity (PAR)** (Photosynthetically Active Radiation) (Source TBD - needs PAR sensor). Unit: µmol/m²/s.
    *   **FR-DASH-D02:** Display **CO₂ Concentration** (Source TBD - needs CO₂ sensor). Unit: ppm.
    *   **FR-DASH-D03:** Display **Air Temperature** (Use `sensordata.temperature`). Unit: °C.
    *   **FR-DASH-D04:** Display **Soil Moisture** (Use `sensordata.soil_moisture_level` - implies plant water availability). Unit: %. (Cross-reference to Section B).
    *   **FR-DASH-D05:** Display **Soil Temperature** (Cross-reference to Section B). Unit: °C.

*   **FR-DASH-E (Water Tank Status):**
    *   **FR-DASH-E01:** Display **Clean Water Tank Volume** (`sensordata.tank_water_volume` - Clarify if this is clean or dirty, assume clean for now). Use a visual tank indicator. Unit: Liters or %.
    *   **FR-DASH-E02:** Display **Dirty Water Tank Volume** (Source TBD - needs separate sensor/column). Use a visual tank indicator. Unit: Liters or %.
    *   **FR-DASH-E03:** Display **Pump Pressure** (`sensordata.water_pressure` - Clarify which pump this refers to, e.g., Main Pump, Transfer Pump). Unit: bar or psi.
    *   **FR-DASH-E04:** Display **System Water Treatment Rate** (e.g., from FR-DASH-C13 flow meter if applicable, or calculated). Unit: L/min.

*   **FR-DASH-F (Hydroponics System Status - if applicable):**
    *   **FR-DASH-F01:** Display **Nutrient Solution Tank Volume** (Similar to FR-DASH-E01, needs specific sensor/column). Unit: Liters or %.
    *   **FR-DASH-F02:** Display **Hydroponics Circulation Pump Pressure** (Similar to FR-DASH-E03, needs specific sensor/column). Unit: bar or psi.
    *   **FR-DASH-F03:** Display **Hydroponics System Circulation Rate** (Needs specific flow meter). Unit: L/min.
    *   **FR-DASH-F04:** Display relevant Water Quality parameters for the nutrient solution (e.g., pH, EC, Temp - likely requires dedicated sensors within the hydroponics loop).

### 2.3 Device Control ("Kontrol")
*   **FR-CTRL-001:** A dedicated page/section titled "Kontrol" shall be provided for device management.
*   **FR-CTRL-002:** The interface shall list controllable devices (e.g., "Main Water Pump," "Zone 1 Irrigation Valve," "Nutrient Pump"). Device names/identifiers must be configurable.
*   **FR-CTRL-003:** For each device, display its current status (e.g., On/Off, Open/Closed, Running/Idle, Error).
*   **FR-CTRL-004:** Provide intuitive controls (e.g., Toggle Switches for On/Off, Buttons for Open/Close).
*   **FR-CTRL-005:** User actions (e.g., clicking "Turn On") shall send a command to the backend.
*   **FR-CTRL-006:** The backend shall interact with the hardware control layer (details TBD, assumes API/method calls).
*   **FR-CTRL-007:** Provide immediate visual feedback on command initiation (e.g., "Sending command...") and confirmation of state change or error.
*   **FR-CTRL-008:** Implement basic safety interlocks visible in the UI (e.g., disable "Turn On" for Main Pump if Clean Water Tank Volume is below a threshold). Thresholds should be configurable.

### 2.4 Historical Data
*   **FR-HIST-001:** A dedicated page/section shall allow users to view historical sensor data.
*   **FR-HIST-002:** Users shall be able to select one or more parameters from the available `sensordata` columns (and other tracked data points).
*   **FR-HIST-003:** Users shall be able to select a time range (e.g., Last 24 Hours, Last 7 Days, Last 30 Days, Custom Range).
*   **FR-HIST-004:** Selected data shall be presented visually using time-series charts (line graphs preferred).
*   **FR-HIST-005:** Charts shall support zooming and panning.
*   **FR-HIST-006:** Users shall be able to export the selected data (parameter, time range) to a CSV file.

### 2.5 Alerts & Notifications
*   **FR-ALRT-001:** A dedicated page/section shall allow users to configure alerts.
*   **FR-ALRT-002:** Users shall be able to define threshold alerts for key parameters (e.g., Tank Volume Low/High, Soil Moisture Low/High, pH Out of Range). Configurable parameters and thresholds required.
*   **FR-ALRT-003:** Users shall be able to enable/disable alerts for specific conditions.
*   **FR-ALRT-004:** When an alert condition is met, an in-app notification/indicator shall appear prominently.
*   **FR-ALRT-005:** An alert log shall be maintained, showing triggered alerts, timestamps, and current status (Active/Acknowledged).
*   **FR-ALRT-006:** (V.Next) Implement push notifications or email/SMS notifications.

## 3. Non-Functional Requirements

### 3.1 Performance
*   **NFR-PERF-001:** Dashboard data should load within 5 seconds on a standard broadband connection.
*   **NFR-PERF-002:** Real-time data updates on the dashboard should occur within 2 seconds of the configured refresh interval.
*   **NFR-PERF-003:** Historical data queries for a 30-day period should return within 10 seconds.
*   **NFR-PERF-004:** Backend API response times should average below 500ms under normal load.

### 3.2 Usability
*   **NFR-USAB-001:** The user interface shall be intuitive and follow standard web conventions.
*   **NFR-USAB-002:** Navigation shall be clear and consistent across the application.
*   **NFR-USAB-003:** Visual design shall be clean, uncluttered, and use color effectively (e.g., status indication). Leverage Bootstrap/Tailwind for consistent styling.
*   **NFR-USAB-004:** The application shall be responsive and usable on common desktop, tablet, and mobile screen sizes (via browser).

### 3.3 Reliability
*   **NFR-RELY-001:** The application should aim for 99.5% uptime (excluding scheduled maintenance).
*   **NFR-RELY-002:** Data displayed should accurately reflect the latest available data in the database.
*   **NFR-RELY-003:** Control commands should be processed reliably; failures should be reported clearly to the user.

### 3.4 Security
*   **NFR-SECU-001:** User authentication must be enforced for all sensitive data and control actions.
*   **NFR-SECU-002:** Passwords must be stored securely (hashed and salted).
*   **NFR-SECU-003:** Communication between client and server must use HTTPS.
*   **NFR-SECU-004:** Implement basic protection against common web vulnerabilities (e.g., CSRF, XSS, SQL Injection) using Flask best practices.

### 3.5 Scalability
*   **NFR-SCAL-001:** The system should be designed to handle data from up to 50 sensors initially without significant performance degradation.
*   **NFR-SCAL-002:** The database schema (`sensordata`) should include appropriate indexing (`timestamp`, potentially sensor ID if added) for efficient querying.

### 3.6 Maintainability
*   **NFR-MAIN-001:** Backend (Flask) and frontend (JS) code should be well-structured, commented, and follow standard coding practices.
*   **NFR-MAIN-002:** Configuration parameters (e.g., database connection, refresh intervals, alert thresholds) should be externalized from the code.

## 4. Data Model

*   **Database:** `irrigodb` (Assumed SQL-based, e.g., PostgreSQL, MySQL)
*   **Primary Table:** `sensordata`
    *   `id`: SERIAL PRIMARY KEY or BIGSERIAL PRIMARY KEY
    *   `timestamp`: TIMESTAMP WITH TIME ZONE NOT NULL (Indexed)
    *   `humidity`: FLOAT
    *   `rainfall`: FLOAT (Unit: mm, clarify time period accumulation if applicable)
    *   `soil_moisture_level`: FLOAT (Unit: %)
    *   `temperature`: FLOAT (Unit: °C, clarify Air vs Soil vs Water)
    *   `ph_level`: FLOAT (Clarify Soil vs Water)
    *   `uv_intensity`: FLOAT (Clarify unit)
    *   `water_pressure`: FLOAT (Unit: bar or psi, clarify location)
    *   `tank_water_volume`: FLOAT (Unit: Liters, clarify which tank)
    *   *(Potential additions needed based on FRs):* `sensor_id` (VARCHAR/INT, Indexed - if multiple sensors of same type), `soil_temperature`, `water_temperature`, `soil_ph`, `water_ph`, `ec_soil`, `ec_water`, `tds`, `ntu`, `nh3_nh4`, `no3`, `po4`, `k_plus`, `so4`, `par`, `co2`, `flow_rate`, `dirty_tank_volume`, etc. or separate tables.
*   **Other Potential Tables:** `users`, `devices`, `alerts`, `alert_log`, `device_status`.

## 5. Technical Stack

*   **Backend:** Python 3.x, Flask Framework
*   **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5 (CDN), Tailwind CSS (CDN)
*   **Database:** `irrigodb` (Specific SQL database TBD, e.g., PostgreSQL)
*   **Deployment:** TBD (e.g., Docker, Linux Server with Gunicorn/Nginx)

## 6. UI/UX Considerations

*   Use clear data visualization techniques (gauges, charts, status indicators).
*   Prioritize information display on the dashboard (overview first, details on demand).
*   Ensure consistent visual language and branding.
*   Provide feedback for user actions (loading indicators, success/error messages).
*   Optimize for touch interactions on mobile browsers.

## 7. Future Considerations (Post V1.0)

*   Advanced automation rules engine.
*   Integration with external Weather APIs for forecasts and enhanced data.
*   User roles and permissions.
*   Native mobile applications.
*   Machine learning for predictive maintenance or optimized irrigation scheduling.
*   Multi-language support.
*   More sophisticated reporting and data analysis tools.

## 8. Glossary

*   **EC:** Electrical Conductivity
*   **TDS:** Total Dissolved Solids
*   **NTU:** Nephelometric Turbidity Units
*   **PAR:** Photosynthetically Active Radiation
*   **SAR:** Sodium Adsorption Ratio
*   **SAP:** Super Absorbent Polymer
*   **UI:** User Interface
*   **UX:** User Experience
*   **API:** Application Programming Interface