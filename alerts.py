"""
Section H - Alerts & Notifications
MINN2020A: Computer Programming for Mining

Generates alerts when predefined conditions are exceeded.
NOTE: All thresholds are educational prototype values only. They are NOT
real manufacturer or mine safety limits (as stated in the project brief).

Alert types covered:
    1. High equipment temperature
    2. High equipment vibration
    3. Low PPE compliance
    4. High fatigue level
    5. Critical safety incident
    6. Excessive equipment downtime
    7. Overdue maintenance
    8. High-risk safety observation
"""

from datetime import date, datetime

# ---------------------------------------------------------------------------
# Prototype thresholds (change here, the rest of the code follows)
# ---------------------------------------------------------------------------
TEMP_WARNING = 80       # degrees C   (<80 normal, 80-100 warning, >100 critical)
TEMP_CRITICAL = 100
VIB_WARNING = 5         # mm/s        (<5 normal, 5-8 warning, >8 critical)
VIB_CRITICAL = 8
PPE_WARNING = 90        # % compliance (below 90 warning, below 75 critical)
PPE_CRITICAL = 75
FATIGUE_WARNING = 6     # scale 1-10  (6-7 warning, 8+ critical)
FATIGUE_CRITICAL = 8
DOWNTIME_WARNING = 15   # % of total time (15-25 warning, above 25 critical)
DOWNTIME_CRITICAL = 25

SEVERITY_ORDER = {"NORMAL": 0, "WARNING": 1, "CRITICAL": 2}

LINE = "=" * 53


# ---------------------------------------------------------------------------
# Building and formatting alerts
# ---------------------------------------------------------------------------
def make_alert(level, alert_type, subject_id, parameter, value, status, action):
    """Create one alert as a dictionary."""
    return {
        "level": level,
        "type": alert_type,
        "subject_id": subject_id,
        "parameter": parameter,
        "value": value,
        "status": status,
        "action": action,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def format_alert(alert):
    """Format an alert in the style shown in Figure 1 of the brief."""
    return "\n".join([
        LINE,
        "MINING MONITORING ALERT",
        LINE,
        f"[{alert['level']}]",
        f"Equipment/Worker ID: {alert['subject_id']}",
        f"Parameter: {alert['parameter']}",
        f"Value: {alert['value']}",
        f"Status: {alert['status']}",
        "Recommended Action:",
        f" {alert['action']}",
        LINE,
    ])


def _to_number(value):
    """Convert to float or return None if it is missing/invalid."""
    try:
        if value is None or value == "":
            return None
        number = float(value)
        if number != number:  # NaN check
            return None
        return number
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Equipment alerts
# ---------------------------------------------------------------------------
def check_temperature(equipment_id, temperature):
    """Alert if temperature is in the warning or critical range."""
    t = _to_number(temperature)
    if t is None:
        return None
    if t > TEMP_CRITICAL:
        return make_alert("CRITICAL", "High equipment temperature", equipment_id,
                          "Temperature", f"{t:g} C", "Above Critical Threshold",
                          "Stop equipment, inspect cooling system and initiate maintenance.")
    if t >= TEMP_WARNING:
        return make_alert("WARNING", "High equipment temperature", equipment_id,
                          "Temperature", f"{t:g} C", "Approaching Critical Threshold",
                          "Monitor closely and schedule an inspection.")
    return None


def check_vibration(equipment_id, vibration):
    """Alert if vibration is in the warning or critical range."""
    v = _to_number(vibration)
    if v is None:
        return None
    if v > VIB_CRITICAL:
        return make_alert("CRITICAL", "High equipment vibration", equipment_id,
                          "Vibration", f"{v:g} mm/s", "Above Critical Threshold",
                          "Inspect equipment and initiate appropriate maintenance/safety procedures.")
    if v >= VIB_WARNING:
        return make_alert("WARNING", "High equipment vibration", equipment_id,
                          "Vibration", f"{v:g} mm/s", "Approaching Critical Threshold",
                          "Monitor closely and schedule an inspection.")
    return None


def check_downtime(equipment_id, operating_time, downtime):
    """Alert if downtime is a large share of total time (operating + downtime)."""
    op = _to_number(operating_time)
    down = _to_number(downtime)
    if op is None or down is None or op < 0 or down < 0 or (op + down) == 0:
        return None
    pct = down / (op + down) * 100
    if pct > DOWNTIME_CRITICAL:
        return make_alert("CRITICAL", "Excessive equipment downtime", equipment_id,
                          "Downtime", f"{pct:.1f} %", "Above Critical Threshold",
                          "Investigate causes of downtime and prioritise repairs.")
    if pct >= DOWNTIME_WARNING:
        return make_alert("WARNING", "Excessive equipment downtime", equipment_id,
                          "Downtime", f"{pct:.1f} %", "Approaching Critical Threshold",
                          "Review maintenance schedule for this equipment.")
    return None


def check_maintenance(equipment_id, next_maintenance_date, today=None):
    """Alert if the next maintenance date has passed (overdue) or is within 7 days."""
    if today is None:
        today = date.today()
    if isinstance(next_maintenance_date, datetime):
        due = next_maintenance_date.date()
    elif isinstance(next_maintenance_date, date):
        due = next_maintenance_date
    else:
        try:
            due = datetime.strptime(str(next_maintenance_date)[:10], "%Y-%m-%d").date()
        except ValueError:
            return None
    days_left = (due - today).days
    if days_left < 0:
        return make_alert("CRITICAL", "Overdue maintenance", equipment_id,
                          "Maintenance due date", str(due),
                          f"Overdue by {-days_left} day(s)",
                          "Schedule maintenance immediately.")
    if days_left <= 7:
        return make_alert("WARNING", "Maintenance due soon", equipment_id,
                          "Maintenance due date", str(due),
                          f"Due in {days_left} day(s)",
                          "Plan and book maintenance.")
    return None


# ---------------------------------------------------------------------------
# Safety alerts
# ---------------------------------------------------------------------------
def check_ppe(worker_id, ppe_compliance_percent):
    """Alert if PPE compliance is low."""
    p = _to_number(ppe_compliance_percent)
    if p is None:
        return None
    if p < PPE_CRITICAL:
        return make_alert("CRITICAL", "Low PPE compliance", worker_id,
                          "PPE compliance", f"{p:g} %", "Below Critical Threshold",
                          "Stop work until PPE is worn correctly and retrain the worker/team.")
    if p < PPE_WARNING:
        return make_alert("WARNING", "Low PPE compliance", worker_id,
                          "PPE compliance", f"{p:g} %", "Below Target",
                          "Remind workers about PPE requirements.")
    return None


def check_fatigue(worker_id, fatigue_level):
    """Alert if fatigue level (1-10) is high."""
    f = _to_number(fatigue_level)
    if f is None:
        return None
    if f >= FATIGUE_CRITICAL:
        return make_alert("CRITICAL", "High fatigue level", worker_id,
                          "Fatigue level", f"{f:g} / 10", "Above Critical Threshold",
                          "Remove worker from safety-critical tasks and allow rest.")
    if f >= FATIGUE_WARNING:
        return make_alert("WARNING", "High fatigue level", worker_id,
                          "Fatigue level", f"{f:g} / 10", "Elevated",
                          "Supervisor to check on worker and consider a break.")
    return None


def check_incident(incident_id, severity):
    """Alert for critical or high severity safety incidents."""
    s = str(severity).strip().capitalize() if severity is not None else ""
    if s == "Critical":
        return make_alert("CRITICAL", "Critical safety incident", incident_id,
                          "Incident severity", s, "Critical incident recorded",
                          "Notify Safety Officer and Manager, start investigation immediately.")
    if s == "High":
        return make_alert("WARNING", "High severity safety incident", incident_id,
                          "Incident severity", s, "High severity incident recorded",
                          "Investigate and apply corrective action.")
    return None


def check_risk_observation(observation_id, risk_class):
    """Alert for High / Critical risk observations (uses Section G classes)."""
    c = str(risk_class).strip().capitalize() if risk_class is not None else ""
    if c == "Critical":
        return make_alert("CRITICAL", "High-risk safety observation", observation_id,
                          "Risk class", c, "Critical risk identified",
                          "Stop the activity and apply controls before work continues.")
    if c == "High":
        return make_alert("WARNING", "High-risk safety observation", observation_id,
                          "Risk class", c, "High risk identified",
                          "Review controls and add measures urgently.")
    return None


# ---------------------------------------------------------------------------
# Running every check over records (dictionaries or DataFrame rows)
# ---------------------------------------------------------------------------
def _add(alerts, alert):
    if alert is not None:
        alerts.append(alert)


def check_equipment_record(rec, today=None):
    """rec keys: Equipment ID, Temperature, Vibration, Operating Hours, Downtime, Next Maintenance."""
    eid = rec.get("Equipment ID", "UNKNOWN")
    alerts = []
    _add(alerts, check_temperature(eid, rec.get("Temperature")))
    _add(alerts, check_vibration(eid, rec.get("Vibration")))
    _add(alerts, check_downtime(eid, rec.get("Operating Hours"), rec.get("Downtime")))
    if rec.get("Next Maintenance") not in (None, ""):
        _add(alerts, check_maintenance(eid, rec.get("Next Maintenance"), today))
    return alerts


def check_worker_record(rec):
    """rec keys: Worker ID, PPE Compliance (%), Fatigue Level, Risk Class."""
    wid = rec.get("Worker ID", "UNKNOWN")
    alerts = []
    _add(alerts, check_ppe(wid, rec.get("PPE Compliance")))
    _add(alerts, check_fatigue(wid, rec.get("Fatigue Level")))
    if rec.get("Risk Class") not in (None, ""):
        _add(alerts, check_risk_observation(wid, rec.get("Risk Class")))
    return alerts


def check_incident_record(rec):
    """rec keys: Incident ID, Severity."""
    alerts = []
    _add(alerts, check_incident(rec.get("Incident ID", "UNKNOWN"), rec.get("Severity")))
    return alerts


def generate_all_alerts(equipment_records=(), worker_records=(), incident_records=(), today=None):
    """Run every check and return alerts sorted with CRITICAL first."""
    alerts = []
    for rec in equipment_records:
        alerts.extend(check_equipment_record(rec, today))
    for rec in worker_records:
        alerts.extend(check_worker_record(rec))
    for rec in incident_records:
        alerts.extend(check_incident_record(rec))
    alerts.sort(key=lambda a: -SEVERITY_ORDER[a["level"]])
    return alerts


def count_by_level(alerts):
    """Counts for the dashboard KPIs (critical alerts, warnings, total)."""
    critical = sum(1 for a in alerts if a["level"] == "CRITICAL")
    warning = sum(1 for a in alerts if a["level"] == "WARNING")
    return {"critical": critical, "warning": warning, "total": len(alerts)}


def alerts_from_dataframes(equipment_df=None, workers_df=None, incidents_df=None, today=None):
    """Convenience wrapper for pandas DataFrames."""
    eq = equipment_df.to_dict("records") if equipment_df is not None else []
    wk = workers_df.to_dict("records") if workers_df is not None else []
    inc = incidents_df.to_dict("records") if incidents_df is not None else []
    return generate_all_alerts(eq, wk, inc, today)


if __name__ == "__main__":
    demo = check_vibration("TRK-012", 9.2)
    print(format_alert(demo))
