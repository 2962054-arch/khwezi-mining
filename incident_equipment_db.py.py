 
import pandas as pd
from datetime import datetime


 

def add_incident(incidents_df, incident_id, date, shift, location, department,
                  incident_type, severity, lost_time_injury, cause, corrective_action):
    """Adds one new safety incident record to the incidents table."""
    # Build the new row as a small dictionary first, so it is easy to read.
    # pd.to_datetime() keeps the Date column as a proper date type.
    new_row = {
        "IncidentID": incident_id,
        "Date": pd.to_datetime(date),
        "Shift": shift,
        "Location": location,
        "Department": department,
        "IncidentType": incident_type,
        "Severity": severity,
        "LostTimeInjury": lost_time_injury,
        "Cause": cause,
        "CorrectiveAction": corrective_action,
        "Status": "Open",   # every new incident starts as "Open"
    }
    # pd.concat is used instead of the old .append() method, which
    # Pandas has removed in recent versions
    new_row_df = pd.DataFrame([new_row])
    updated_df = pd.concat([incidents_df, new_row_df], ignore_index=True)
    updated_df["Date"] = pd.to_datetime(updated_df["Date"])  # keep the column as dates
    return updated_df


def view_incidents(incidents_df):
    """Returns the full incidents table, sorted with the most recent incident first."""
    return incidents_df.sort_values("Date", ascending=False)


def search_incidents(incidents_df, keyword):
    """Searches incidents for a keyword in Location, IncidentType or Cause."""
    # Not case-sensitive, so convert everything to lower case first
    keyword = keyword.lower()
    # Check each of the three text columns for a match, then combine
    # the three True/False results with "OR" (the | symbol)
    mask = (
        incidents_df["Location"].str.lower().str.contains(keyword, na=False) |
        incidents_df["IncidentType"].str.lower().str.contains(keyword, na=False) |
        incidents_df["Cause"].str.lower().str.contains(keyword, na=False)
    )
    return incidents_df[mask]


def filter_incidents(incidents_df, department=None, severity=None, shift=None):
    """Returns incidents matching the given Department/Severity/Shift filters."""
    # Any filter left as None (or "All") is ignored
    result = incidents_df.copy()
    if department and department != "All":
        result = result[result["Department"] == department]
    if severity and severity != "All":
        result = result[result["Severity"] == severity]
    if shift and shift != "All":
        result = result[result["Shift"] == shift]
    return result


def categorize_incidents(incidents_df):
    """Groups incidents by type and severity, with a count for each group."""
    # groupby + size() counts how many rows fall into each combination
    grouped = (
        incidents_df
        .groupby(["IncidentType", "Severity"])
        .size()
        .reset_index(name="Count")
        .sort_values("Count", ascending=False)
    )
    return grouped


def count_incidents(incidents_df, by="Department"):
    """Counts incidents grouped by a chosen column (e.g. Department, Shift)."""
    # value_counts() automatically sorts from highest to lowest
    return incidents_df[by].value_counts()


def analyse_incident_trends(incidents_df):
    """Summarises incident counts per month, to see if trends are rising or falling."""
    # dt.to_period("M") groups every date into its calendar month
    monthly_counts = incidents_df.groupby(
        incidents_df["Date"].dt.to_period("M")
    ).size()
    return monthly_counts


def high_risk_departments(incidents_df, severity_levels=("High", "Critical")):
    """Counts High/Critical incidents per department, highest first."""
    # Keep only the rows with a high-risk severity, then count by department
    high_risk = incidents_df[incidents_df["Severity"].isin(severity_levels)]
    return high_risk["Department"].value_counts()


 

def add_equipment(equipment_df, equipment_id, equipment_type, manufacturer,
                   operating_hours=0, temperature=25, vibration=0,
                   fuel_consumption=0, brake_status="OK", tyre_status="OK",
                   engine_status="OK", maintenance_status="Up to date",
                   downtime=0):
    """Adds one new piece of equipment to the equipment table."""
    new_row = {
        "EquipmentID": equipment_id,
        "EquipmentType": equipment_type,
        "Manufacturer": manufacturer,
        "OperatingHours": operating_hours,
        "Downtime": downtime,
        "Temperature": temperature,
        "Vibration": vibration,
        "FuelConsumption": fuel_consumption,
        "BrakeStatus": brake_status,
        "TyreStatus": tyre_status,
        "EngineStatus": engine_status,
        "MaintenanceStatus": maintenance_status,
    }
    # Availability is calculated from operating hours and downtime
    total_time = operating_hours + downtime
    new_row["Availability"] = round((operating_hours / total_time) * 100, 1) if total_time > 0 else 0.0

    new_row_df = pd.DataFrame([new_row])
    updated_df = pd.concat([equipment_df, new_row_df], ignore_index=True)
    return updated_df


def view_equipment_records(equipment_df):
    """Returns the full equipment table, sorted by EquipmentID."""
    return equipment_df.sort_values("EquipmentID")


def search_equipment(equipment_df, keyword):
    """Searches equipment for a keyword in ID, EquipmentType or Manufacturer."""
    keyword = keyword.lower()
    mask = (
        equipment_df["EquipmentID"].str.lower().str.contains(keyword, na=False) |
        equipment_df["EquipmentType"].str.lower().str.contains(keyword, na=False) |
        equipment_df["Manufacturer"].str.lower().str.contains(keyword, na=False)
    )
    return equipment_df[mask]


def filter_equipment(equipment_df, equipment_type=None, maintenance_status=None):
    """Returns equipment matching the given Type/Maintenance Status filters."""
    result = equipment_df.copy()
    if equipment_type and equipment_type != "All":
        result = result[result["EquipmentType"] == equipment_type]
    if maintenance_status and maintenance_status != "All":
        result = result[result["MaintenanceStatus"] == maintenance_status]
    return result


def get_equipment_parameters(equipment_df, equipment_id):
    """Returns the full parameter set (temperature, vibration, fuel, status fields) for one machine."""
    # .loc finds the single row matching this EquipmentID
    row = equipment_df.loc[equipment_df["EquipmentID"] == equipment_id]
    if row.empty:
        return None
    return row.iloc[0].to_dict()


def categorize_equipment(equipment_df):
    """Groups equipment by type and maintenance status, with a count for each group."""
    grouped = (
        equipment_df
        .groupby(["EquipmentType", "MaintenanceStatus"])
        .size()
        .reset_index(name="Count")
        .sort_values("Count", ascending=False)
    )
    return grouped


def count_equipment(equipment_df, by="EquipmentType"):
    """Counts equipment grouped by a chosen column (e.g. Type, Manufacturer)."""
    return equipment_df[by].value_counts()


def equipment_summary_stats(equipment_df):
    """Calculates average availability and identifies which equipment needs attention."""
    # idxmax()/idxmin() find the row label with the highest/lowest value
    worst_downtime = equipment_df["Downtime"].idxmax()
    worst_vibration = equipment_df["Vibration"].idxmax()
    worst_temperature = equipment_df["Temperature"].idxmax()
    worst_availability = equipment_df["Availability"].idxmin()

    summary = {
        "average_availability": round(equipment_df["Availability"].mean(), 1),
        "highest_downtime_equipment": equipment_df.loc[worst_downtime, "EquipmentID"],
        "highest_vibration_equipment": equipment_df.loc[worst_vibration, "EquipmentID"],
        "highest_temperature_equipment": equipment_df.loc[worst_temperature, "EquipmentID"],
        "lowest_availability_equipment": equipment_df.loc[worst_availability, "EquipmentID"],
    }
    return summary


 
if __name__ == "__main__":

    sample_incidents = pd.DataFrame({
        "IncidentID": ["INC001", "INC002", "INC003"],
        "Date": pd.to_datetime(["2026-02-10", "2026-03-05", "2026-03-20"]),
        "Shift": ["Day", "Night", "Day"],
        "Location": ["Shaft 1", "Plant", "Shaft 2"],
        "Department": ["Mining", "Processing", "Mining"],
        "IncidentType": ["Slip/Fall", "Fire", "Vehicle Collision"],
        "Severity": ["Low", "Critical", "High"],
        "LostTimeInjury": [False, True, False],
        "Cause": ["Human Error", "Equipment Failure", "Human Error"],
        "CorrectiveAction": ["Retrain staff", "Inspect wiring", "Review procedure"],
        "Status": ["Closed", "Open", "Open"],
    })

    print("===== SAFETY INCIDENT DATABASE TEST =====")
    sample_incidents = add_incident(
        sample_incidents, "INC004", "2026-04-01", "Night", "Shaft 1", "Mining",
        "Fire", "High", False, "Equipment Failure", "Inspect equipment"
    )
    print("\nAfter adding INC004:")
    print(sample_incidents[["IncidentID", "IncidentType", "Status"]])

    print("\nSearch results for 'fire':")
    print(search_incidents(sample_incidents, "fire")[["IncidentID", "IncidentType"]])

    print("\nFilter: Mining department only:")
    print(filter_incidents(sample_incidents, department="Mining")[["IncidentID", "Department"]])

    print("\nIncidents grouped by type and severity:")
    print(categorize_incidents(sample_incidents))

    print("\nIncident count by department:")
    print(count_incidents(sample_incidents, by="Department"))

    print("\nMonthly incident trend:")
    print(analyse_incident_trends(sample_incidents))

    print("\nHigh-risk departments:")
    print(high_risk_departments(sample_incidents))

    sample_equipment = pd.DataFrame({
        "EquipmentID": ["EQ001", "EQ002", "EQ003"],
        "EquipmentType": ["Haul Truck", "Loader", "Drill Rig"],
        "Manufacturer": ["Caterpillar", "Komatsu", "Sandvik"],
        "OperatingHours": [720, 650, 800],
        "Downtime": [80, 40, 120],
        "Temperature": [95, 70, 105],
        "Vibration": [6.5, 3.2, 9.1],
        "FuelConsumption": [150, 120, 100],
        "BrakeStatus": ["OK", "OK", "OK"],
        "TyreStatus": ["OK", "OK", "Fault"],
        "EngineStatus": ["OK", "OK", "OK"],
        "MaintenanceStatus": ["Due", "Up to date", "Overdue"],
    })
    sample_equipment["Availability"] = round(
        sample_equipment["OperatingHours"] /
        (sample_equipment["OperatingHours"] + sample_equipment["Downtime"]) * 100, 1
    )

    print("\n\n===== EQUIPMENT DATABASE TEST =====")
    sample_equipment = add_equipment(
        sample_equipment, "EQ004", "Excavator", "Epiroc",
        operating_hours=500, downtime=20, temperature=75, vibration=4.0
    )
    print("\nAfter adding EQ004:")
    print(sample_equipment[["EquipmentID", "EquipmentType", "Availability"]])

    print("\nSearch results for 'sandvik':")
    print(search_equipment(sample_equipment, "sandvik")[["EquipmentID", "Manufacturer"]])

    print("\nFilter: Overdue maintenance only:")
    print(filter_equipment(sample_equipment, maintenance_status="Overdue")[["EquipmentID", "MaintenanceStatus"]])

    print("\nFull parameter set for EQ003:")
    print(get_equipment_parameters(sample_equipment, "EQ003"))

    print("\nEquipment grouped by type and maintenance status:")
    print(categorize_equipment(sample_equipment))

    print("\nEquipment count by type:")
    print(count_equipment(sample_equipment, by="EquipmentType"))

    print("\nSummary statistics:")
    print(equipment_summary_stats(sample_equipment))
