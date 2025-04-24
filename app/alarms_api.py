from flask import Blueprint, jsonify, request, abort
from app.database import db
from app.models import Alarm, AlarmRule, Device, AlarmStatus, AlarmSeverity, AlarmCondition, SensorData
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, asc

alarms_bp = Blueprint('alarms_bp', __name__)

# --- Alarm Endpoints ---

@alarms_bp.route('/api/alarms', methods=['GET'])
def get_alarms():
    """
    Get a list of alarms, with optional filtering and sorting.
    Query Parameters:
    - status (str): Filter by status (active, acknowledged, cleared)
    - severity (str): Filter by severity (info, warning, critical)
    - device_id (int): Filter by device ID
    - sort_by (str): Field to sort by (timestamp, severity, status). Default: timestamp
    - order (str): Sort order (asc, desc). Default: desc
    """
    query = Alarm.query

    # Filtering
    status_filter = request.args.get('status')
    if status_filter:
        try:
            status_enum = AlarmStatus(status_filter.lower())
            query = query.filter(Alarm.status == status_enum)
        except ValueError:
            return jsonify({"error": f"Invalid status value: {status_filter}"}), 400

    severity_filter = request.args.get('severity')
    if severity_filter:
        try:
            severity_enum = AlarmSeverity(severity_filter.lower())
            query = query.filter(Alarm.severity == severity_enum)
        except ValueError:
            return jsonify({"error": f"Invalid severity value: {severity_filter}"}), 400

    device_id_filter = request.args.get('device_id')
    if device_id_filter:
        try:
            device_id = int(device_id_filter)
            query = query.filter(Alarm.device_id == device_id)
        except ValueError:
            return jsonify({"error": f"Invalid device_id value: {device_id_filter}"}), 400

    # Sorting
    sort_by = request.args.get('sort_by', 'timestamp')
    order = request.args.get('order', 'desc')

    sort_column = getattr(Alarm, sort_by, None)
    if sort_column is None:
        return jsonify({"error": f"Invalid sort_by value: {sort_by}"}), 400

    if order.lower() == 'desc':
        query = query.order_by(desc(sort_column))
    elif order.lower() == 'asc':
        query = query.order_by(asc(sort_column))
    else:
        return jsonify({"error": f"Invalid order value: {order}"}), 400

    alarms = query.all()
    return jsonify([alarm.to_dict() for alarm in alarms])

@alarms_bp.route('/api/alarms/<int:alarm_id>', methods=['GET'])
def get_alarm_detail(alarm_id):
    """Get details of a specific alarm."""
    alarm = Alarm.query.get_or_404(alarm_id)
    return jsonify(alarm.to_dict())

# Note: Alarm creation is typically handled internally when rules are triggered.
# We might need an endpoint to update alarm status (e.g., acknowledge).

@alarms_bp.route('/api/alarms/<int:alarm_id>/status', methods=['PUT'])
def update_alarm_status(alarm_id):
    """Update the status of an alarm (e.g., acknowledge)."""
    alarm = Alarm.query.get_or_404(alarm_id)
    data = request.get_json()

    if not data or 'status' not in data:
        return jsonify({"error": "Missing 'status' in request body"}), 400

    new_status_str = data['status'].lower()
    try:
        new_status = AlarmStatus(new_status_str)
    except ValueError:
        return jsonify({"error": f"Invalid status value: {new_status_str}"}), 400

    # Basic state transition validation (can be more complex)
    if alarm.status == AlarmStatus.ACTIVE and new_status == AlarmStatus.ACKNOWLEDGED:
        alarm.status = new_status
    elif alarm.status == AlarmStatus.ACKNOWLEDGED and new_status == AlarmStatus.CLEARED:
         # Clearing might be automatic when condition resolves, but allow manual for now
         alarm.status = new_status
    elif new_status == AlarmStatus.ACTIVE:
         # Potentially allow reactivation? Or should this only happen via rules?
         # For now, let's prevent manual setting to ACTIVE.
         return jsonify({"error": "Cannot manually set status to ACTIVE"}), 400
    # Allow setting to cleared directly from active? Maybe.
    elif alarm.status == AlarmStatus.ACTIVE and new_status == AlarmStatus.CLEARED:
        alarm.status = new_status
    elif alarm.status == new_status:
        pass # No change needed
    else:
        return jsonify({"error": f"Invalid status transition from {alarm.status.value} to {new_status.value}"}), 400


    try:
        db.session.commit()
        return jsonify(alarm.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update alarm status", "details": str(e)}), 500


# --- Alarm Rule Endpoints ---

@alarms_bp.route('/api/alarm_rules', methods=['GET'])
def get_alarm_rules():
    """Get a list of all alarm rules."""
    rules = AlarmRule.query.order_by(AlarmRule.name).all()
    return jsonify([rule.to_dict() for rule in rules])

@alarms_bp.route('/api/alarm_rules', methods=['POST'])
def create_alarm_rule():
    """Create a new alarm rule."""
    data = request.get_json()

    required_fields = ['name', 'device_id', 'sensor_metric', 'condition', 'threshold_value']
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

    # Validate enums and device_id
    try:
        condition = AlarmCondition(data['condition'])
        severity = AlarmSeverity(data.get('severity', 'warning').lower()) # Default to warning
        device_id = int(data['device_id'])
        threshold = float(data['threshold_value'])
        cooldown = int(data.get('cooldown_period_seconds', 300)) # Default cooldown
        is_active = bool(data.get('is_active', True)) # Default to active
    except (ValueError, TypeError) as e:
        return jsonify({"error": "Invalid data type or enum value", "details": str(e)}), 400

    # Check if device exists
    device = Device.query.get(device_id)
    if not device:
        return jsonify({"error": f"Device with id {device_id} not found"}), 404

    # Check if sensor_metric is a valid column in SensorData (basic check)
    if not hasattr(SensorData, data['sensor_metric']):
         return jsonify({"error": f"Invalid sensor_metric: {data['sensor_metric']}"}), 400

    new_rule = AlarmRule(
        name=data['name'],
        device_id=device_id,
        sensor_metric=data['sensor_metric'],
        condition=condition,
        threshold_value=threshold,
        severity=severity,
        is_active=is_active,
        cooldown_period_seconds=cooldown
    )

    try:
        db.session.add(new_rule)
        db.session.commit()
        return jsonify(new_rule.to_dict()), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Database integrity error, possibly duplicate rule?", "details": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create alarm rule", "details": str(e)}), 500


@alarms_bp.route('/api/alarm_rules/<int:rule_id>', methods=['GET'])
def get_alarm_rule_detail(rule_id):
    """Get details of a specific alarm rule."""
    rule = AlarmRule.query.get_or_404(rule_id)
    return jsonify(rule.to_dict())


@alarms_bp.route('/api/alarm_rules/<int:rule_id>', methods=['PUT'])
def update_alarm_rule(rule_id):
    """Update an existing alarm rule."""
    rule = AlarmRule.query.get_or_404(rule_id)
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body cannot be empty"}), 400

    try:
        if 'name' in data:
            rule.name = data['name']
        if 'device_id' in data:
            device_id = int(data['device_id'])
            device = Device.query.get(device_id)
            if not device:
                return jsonify({"error": f"Device with id {device_id} not found"}), 404
            rule.device_id = device_id
        if 'sensor_metric' in data:
            if not hasattr(SensorData, data['sensor_metric']):
                 return jsonify({"error": f"Invalid sensor_metric: {data['sensor_metric']}"}), 400
            rule.sensor_metric = data['sensor_metric']
        if 'condition' in data:
            rule.condition = AlarmCondition(data['condition'])
        if 'threshold_value' in data:
            rule.threshold_value = float(data['threshold_value'])
        if 'severity' in data:
            rule.severity = AlarmSeverity(data['severity'].lower())
        if 'is_active' in data:
            rule.is_active = bool(data['is_active'])
        if 'cooldown_period_seconds' in data:
            rule.cooldown_period_seconds = int(data['cooldown_period_seconds'])

    except (ValueError, TypeError) as e:
        return jsonify({"error": "Invalid data type or enum value", "details": str(e)}), 400

    try:
        db.session.commit()
        return jsonify(rule.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update alarm rule", "details": str(e)}), 500


@alarms_bp.route('/api/alarm_rules/<int:rule_id>', methods=['DELETE'])
def delete_alarm_rule(rule_id):
    """Delete an alarm rule."""
    rule = AlarmRule.query.get_or_404(rule_id)

    try:
        # Optional: Check if any active alarms were triggered by this rule?
        # Decide on deletion policy (e.g., prevent deletion if active alarms exist, or just delete the rule)
        # For now, just delete the rule.
        db.session.delete(rule)
        db.session.commit()
        return jsonify({"message": f"Alarm rule {rule_id} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete alarm rule", "details": str(e)}), 500

# Helper endpoint to get available sensor metrics for rule creation UI
@alarms_bp.route('/api/sensor_metrics', methods=['GET'])
def get_sensor_metrics():
    """Get a list of valid sensor metric names from the SensorData model."""
    # Exclude primary key, timestamp, and potentially others not suitable for rules
    excluded_columns = {'id', 'timestamp'}
    metrics = [c.name for c in SensorData.__table__.columns if c.name not in excluded_columns and isinstance(getattr(SensorData, c.name).property.columns[0].type, (db.Float, db.Integer))]
    return jsonify(metrics)

# Helper endpoint to get available devices for rule creation UI
@alarms_bp.route('/api/devices_list', methods=['GET'])
def get_devices_list():
    """Get a simple list of devices (id and name)."""
    devices = Device.query.with_entities(Device.id, Device.name).order_by(Device.name).all()
    return jsonify([{"id": d.id, "name": d.name} for d in devices])
