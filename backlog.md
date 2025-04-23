# Product Backlog: Irrigation & Environmental Monitoring System

**Version:** 1.0
**Date:** 2023-10-27

*   **Prioritization:** High, Medium, Low
*   **Estimation:** Story Points (SP) - Placeholder values, to be estimated by the team.

---

## Epics

*   **EPIC-001:** Core System Setup & Authentication
*   **EPIC-002:** Dashboard ("Anlık Durum") Implementation
*   **EPIC-003:** Device Control ("Kontrol") Implementation
*   **EPIC-004:** Historical Data Viewing & Export
*   **EPIC-005:** Alerting System

---

## Backlog Items (User Stories & Tasks)

### EPIC-001: Core System Setup & Authentication

*   **STORY-001 (High, 3 SP):** [DONE] As a Developer, I want to set up the basic Flask application structure with database connectivity (`irrigodb`), so that other features can be built upon it.
    *   TASK-001: [DONE] Initialize Flask project, configure virtual environment.
    *   TASK-002: [DONE] Implement database connection module for `irrigodb`.
    *   TASK-003: [DONE] Set up basic project layout (templates, static folders).
*   **STORY-002 (High, 5 SP):** [DONE] As a User, I want to log in securely using a username and password, so that I can access the system's features.
    *   TASK-004: [DONE] Create `users` table schema (username, password_hash).
    *   TASK-005: [DONE] Implement password hashing/verification.
    *   TASK-006: [DONE] Create Flask routes for login page rendering and form submission.
    *   TASK-007: [DONE] Implement session management for authenticated users.
    *   TASK-008: [DONE] Create simple HTML/CSS login form using Bootstrap/Tailwind.
    *   TASK-009: [DONE] Protect dashboard/control routes, redirecting unauthenticated users to login.
*   **STORY-003 (Medium, 2 SP):** [DONE] As a User, I want to log out of the system, so that my session is securely ended.
    *   TASK-010: [DONE] Implement Flask route for logout action (clear session).
    *   TASK-011: [DONE] Add logout button to the UI (e.g., in header/navbar).

### EPIC-002: Dashboard ("Anlık Durum") Implementation

*   **STORY-004 (High, 3 SP):** [DONE] As a User, I want the main dashboard page to be titled "Anlık Durum" and have a basic layout with a header and content area, so that the structure is established.
    *   TASK-012: [DONE] Create main dashboard HTML template.
    *   TASK-013: [DONE] Set page title dynamically via Flask.
    *   TASK-014: [DONE] Implement basic layout using Bootstrap/Tailwind (header, main content).
*   **STORY-005 (High, 5 SP):** [DONE] As a User, I want to see the key overview metrics (Temp, Humidity, UV, Rainfall) in a sticky header section, so that they are always visible. (FR-DASH-A)
    *   TASK-015: [DONE] Create Flask API endpoint (`/api/overview_status`) to fetch latest relevant data from `sensordata`.
    *   TASK-016: [DONE] Create frontend JS to fetch data from API endpoint periodically.
    *   TASK-017: [DONE] Design sticky header component (HTML/CSS) using Bootstrap/Tailwind.
    *   TASK-018: [DONE] Populate header component with fetched data (Temp, Humidity, UV, Rainfall). Add units.
    *   TASK-019: [DONE] Implement "Last Updated" timestamp display.
    *   TASK-020: [DONE] *Note:* Address missing data sources (Pressure, Water Processed) - potentially defer or use placeholders. (UI shows placeholders)
*   **STORY-006 (High, 5 SP):** [DONE] As a User, I want to see the current Soil Conditions (Temp, Moisture, pH) on the dashboard, so that I can assess soil health. (FR-DASH-B - Core Items)
    *   TASK-021: [DONE] Create Flask API endpoint (`/api/soil_status`) for latest soil data.
    *   TASK-022: [DONE] Create frontend JS to fetch soil data.
    *   TASK-023: [DONE] Design Soil Conditions component (HTML/CSS).
    *   TASK-024: [DONE] Display Soil Temp, Moisture, pH with units and basic visualization (e.g., text, simple gauge).
    *   TASK-025: [DONE] *Note:* Address missing data sources (EC, NPK, SAP) - defer or use placeholders. (UI shows placeholders)
*   **STORY-007 (Medium, 8 SP):** As a User, I want to see the key Water Quality metrics (Temp, pH, EC, TDS, Flow Rate) on the dashboard, so that I understand the treated water status. (FR-DASH-C - Core Items)
    *   TASK-026: [DONE] Create Flask API endpoint (`/api/water_quality`) for latest water data. (Backend returns placeholders)
    *   TASK-027: [DONE] Create frontend JS to fetch water quality data.
    *   TASK-028: [DONE] Design Water Quality component (HTML/CSS).
    *   TASK-029: [DONE] Display Water Temp, pH, EC, TDS, Flow Rate with units. (UI shows placeholders)
    *   TASK-030: Implement expandable section for detailed parameters (initially placeholders if data unavailable).
    *   TASK-031: [DONE] *Note:* Address missing data sources (NTU, Chemicals, SAR etc.) - defer or use placeholders. (UI shows placeholders)
*   **STORY-008 (Medium, 3 SP):** As a User, I want to see key Plant Environmental factors (Light/PAR, CO2, Air Temp) on the dashboard, so that I understand growth conditions. (FR-DASH-D)
    *   TASK-032: [DONE] Create Flask API endpoint (`/api/plant_env`) for latest data. (Backend returns placeholders)
    *   TASK-033: [DONE] Create frontend JS to fetch plant env data.
    *   TASK-034: [DONE] Design Plant Environment component (HTML/CSS).
    *   TASK-035: [DONE] Display PAR, CO2, Air Temp with units. Use placeholders if sensors unavailable. (UI shows placeholders)
*   **STORY-009 (High, 5 SP):** [DONE] As a User, I want to see the status of the Water Tanks (Clean Volume, Pump Pressure) on the dashboard, so that I know water availability and system pressure. (FR-DASH-E - Core Items)
    *   TASK-036: [DONE] Create Flask API endpoint (`/api/tank_status`) for latest data (`tank_water_volume`, `water_pressure`).
    *   TASK-037: [DONE] Create frontend JS to fetch tank data.
    *   TASK-038: [DONE] Design Tank Status component (HTML/CSS).
    *   TASK-039: [DONE] Display Clean Water Volume using a visual tank indicator.
    *   TASK-040: [DONE] Display relevant Pump Pressure with units.
    *   TASK-041: [DONE] *Note:* Address Dirty Water Volume - defer or use placeholder. (UI shows placeholder)
*   **STORY-010 (Low, 3 SP):** As a User (with Hydroponics), I want to see the status of my Hydroponics system (Nutrient Volume, Pump Pressure, Flow Rate) on the dashboard. (FR-DASH-F)
    *   TASK-042: Create Flask API endpoint (`/api/hydroponics_status`). (Requires specific sensor data).
    *   TASK-043: Create frontend JS to fetch hydroponics data.
    *   TASK-044: Design Hydroponics component (HTML/CSS).
    *   TASK-045: Display relevant metrics with units. Use placeholders if sensors unavailable.

### EPIC-003: Device Control ("Kontrol") Implementation

*   **STORY-011 (High, 8 SP):** [DONE] As a User, I want to see a list of controllable devices (e.g., Main Pump, Zone 1 Valve) with their current status (On/Off, Open/Closed) on the "Kontrol" page, so that I know the state of my equipment.
    *   TASK-046: [DONE] Define device configuration (e.g., in a config file or DB table `devices`). (Device model exists)
    *   TASK-047: [DONE] Create Flask API endpoint (`/api/devices`) to list configured devices and their current status (requires mechanism to query hardware status). (API exists, reads from DB)
    *   TASK-048: [DONE] Create "Kontrol" page HTML template.
    *   TASK-049: [DONE] Create frontend JS to fetch and display the device list and statuses.
    *   TASK-050: [DONE] Design UI elements for each device showing name and status indicator (e.g., icon, text).
*   **STORY-012 (High, 8 SP):** [DONE] As a User, I want to be able to turn pumps On/Off and open/close valves using controls on the "Kontrol" page, so that I can manually operate my system.
    *   TASK-051: [DONE] Create Flask API endpoint (`/api/control_device/<device_id>`) to receive control commands (e.g., POST with action: 'ON', 'OFF', 'OPEN', 'CLOSE').
    *   TASK-052: [DONE] Implement backend logic to translate API calls into hardware commands (requires hardware interface layer).
    *   TASK-053: [DONE] Add interactive controls (buttons, switches) to the frontend device list items.
    *   TASK-054: [DONE] Implement frontend JS to send control commands to the API on user interaction.
    *   TASK-055: [DONE] Implement frontend feedback (command sent, success, error) and update device status display based on response.
*   **STORY-013 (Medium, 3 SP):** [DONE] As a User, I want device controls to be disabled with a visual cue if a safety interlock is active (e.g., cannot turn on pump if tank is empty), so that I don't cause damage.
    *   TASK-056: [DONE] Implement backend logic to check safety conditions before executing control commands.
    *   TASK-057: [DONE] Include interlock status/reason in the `/api/devices` response.
    *   TASK-058: [DONE] Update frontend to disable controls and show reason based on interlock status.

### EPIC-004: Historical Data Viewing & Export

*   **STORY-014 (Medium, 8 SP):** [DONE] As a User, I want to view historical data for selected sensors (e.g., Temperature, Soil Moisture) over a chosen time range (e.g., Last 7 days) as a line chart, so that I can analyze trends.
    *   TASK-059: [DONE] Create Flask API endpoint (`/api/historical_data`) accepting parameters (sensor list, start_time, end_time).
    *   TASK-060: [DONE] Implement backend logic to query `sensordata` based on parameters, handling potentially large datasets (consider aggregation for long ranges).
    *   TASK-061: [DONE] Create "History" page HTML template.
    *   TASK-062: [DONE] Add frontend controls for selecting sensors and time ranges.
    *   TASK-063: [DONE] Integrate a JavaScript charting library (e.g., Chart.js, Plotly.js).
    *   TASK-064: [DONE] Implement frontend JS to fetch historical data and render the chart.
*   **STORY-015 (Medium, 3 SP):** [DONE] As a User, I want to export the currently viewed historical data to a CSV file, so that I can perform offline analysis.
    *   TASK-065: [DONE] Create Flask API endpoint (`/api/export_data`) accepting parameters (sensor list, start_time, end_time).
    *   TASK-066: [DONE] Implement backend logic to query data and generate a CSV formatted response.
    *   TASK-067: [DONE] Add an "Export CSV" button to the History page frontend that triggers the download.

### EPIC-005: Alerting System

*   **STORY-016 (Medium, 8 SP):** As a User, I want to define threshold alerts (e.g., Soil Moisture < 20%, Tank Volume < 10%) via a configuration page, so that I can be notified of critical conditions.
    *   TASK-068: Design database schema for `alerts` (parameter, condition, threshold, enabled).
    *   TASK-069: Create "Alerts" page HTML template for configuration.
    *   TASK-070: Create Flask API endpoints for listing, creating, updating, and deleting alerts.
    *   TASK-071: Implement frontend interface for managing alert configurations.
*   **STORY-017 (High, 5 SP):** As a System, I want to periodically check sensor data against configured alerts and trigger an internal notification when a condition is met.
    *   TASK-072: Implement a background task/service (e.g., using Celery, APScheduler, or simple threading) to periodically check alert conditions.
    *   TASK-073: Implement logic to compare latest sensor data against enabled alerts.
    *   TASK-074: Design database schema for `alert_log` (alert_id, timestamp, status).
    *   TASK-075: Log triggered alerts to the `alert_log`.
*   **STORY-018 (Medium, 3 SP):** As a User, I want to see active alerts prominently displayed within the application (e.g., a banner or notification count in the header), so that I am immediately aware of issues.
    *   TASK-076: Create Flask API endpoint (`/api/active_alerts`) to fetch currently active alerts from `alert_log`.
    *   TASK-077: Implement frontend component (e.g., header badge/dropdown) to fetch and display active alerts periodically.
*   **STORY-019 (Low, 3 SP):** As a User, I want to view a log of past alerts, so that I can review historical events.
    *   TASK-078: Create Flask API endpoint (`/api/alert_history`) to fetch data from `alert_log`.
    *   TASK-079: Add a section/page to display the alert history table.

---
