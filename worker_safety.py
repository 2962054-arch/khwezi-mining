"""
worker_safety.py - Section (b): Worker Health and Safety Monitoring
MINN2020A Mining Health, Safety and Equipment Monitoring Application

Responsibilities:
  * Store worker safety records (data/workers.csv)
  * Validate inputs so bad data never crashes the app
  * Evaluate each worker against prototype safety rules -> warnings + risk level
  * Add / search / filter workers, summary statistics
  * Streamlit page (worker_safety_page)

NOTE: thresholds below are educational prototype values only,
not real mine safety limits.
"""

import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
WORKERS_FILE = os.path.join(DATA_DIR, "workers.csv")

COLUMNS = ["Worker ID", "Department", "Job Role", "Shift", "PPE Compliance (%)",
           "Training Status", "Fatigue Level", "Safety Observations",
           "Near Misses", "Previous Incidents", "Risk Level"]

DEPARTMENTS = ["Drilling", "Blasting", "Loading and Hauling", "Processing",
               "Maintenance", "Ventilation", "Surveying", "Engineering"]
SHIFTS = ["Day", "Afternoon", "Night"]
TRAINING_STATUSES = ["Up to date", "Due soon", "Expired"]

# Prototype thresholds
PPE_WARNING = 90        # below this -> warning
PPE_CRITICAL = 75       # below this -> critical
FATIGUE_WARNING = 6     # fatigue scale 1-10
FATIGUE_CRITICAL = 8
NEAR_MISS_WARNING = 2
INCIDENT_WARNING = 1
INCIDENT_CRITICAL = 3
OBSERVATION_WARNING = 3  # unresolved unsafe observations


# ---------------------------------------------------------------- storage
def load_workers():
    if not os.path.exists(WORKERS_FILE):
        return pd.DataFrame(columns=COLUMNS)
    try:
        df = pd.read_csv(WORKERS_FILE)
    except Exception:
        return pd.DataFrame(columns=COLUMNS)
    for col in COLUMNS:               # tolerate missing columns
        if col not in df.columns:
            df[col] = None
    return df[COLUMNS]


def save_workers(df):
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(WORKERS_FILE, index=False)


# ---------------------------------------------------------------- validation
def validate_worker(record, existing_ids):
    """Return a list of error messages (empty list = valid)."""
    errors = []
    wid = str(record.get("Worker ID", "")).strip().upper()
    if not wid:
        errors.append("Worker ID is required.")
    elif wid in existing_ids:
        errors.append(f"Worker ID {wid} already exists.")
    if record.get("Department") not in DEPARTMENTS:
        errors.append("Select a valid department.")
    if not str(record.get("Job Role", "")).strip():
        errors.append("Job role is required.")
    if record.get("Shift") not in SHIFTS:
        errors.append("Select a valid shift.")
    ppe = record.get("PPE Compliance (%)")
    if not isinstance(ppe, (int, float)) or not 0 <= ppe <= 100:
        errors.append("PPE compliance must be between 0 and 100.")
    if record.get("Training Status") not in TRAINING_STATUSES:
        errors.append("Select a valid training status.")
    fat = record.get("Fatigue Level")
    if not isinstance(fat, (int, float)) or not 1 <= fat <= 10:
        errors.append("Fatigue level must be between 1 and 10.")
    for field in ("Safety Observations", "Near Misses", "Previous Incidents"):
        v = record.get(field)
        if not isinstance(v, (int, float)) or v < 0 or int(v) != v:
            errors.append(f"{field} must be a whole number of 0 or more.")
    return errors


# ---------------------------------------------------------------- rules engine
def assess_worker(record):
    """
    Check one worker against all rules.
    Returns (risk_level, warnings) where warnings is a list of (severity, message).
    Risk level: Low / Medium / High / Critical, from a simple points system.
    """
    warnings = []
    points = 0

    ppe = record["PPE Compliance (%)"]
    if ppe < PPE_CRITICAL:
        warnings.append(("CRITICAL", f"PPE compliance very low ({ppe}%). Stop work and check PPE."))
        points += 3
    elif ppe < PPE_WARNING:
        warnings.append(("WARNING", f"PPE compliance below target ({ppe}%)."))
        points += 1

    fat = record["Fatigue Level"]
    if fat >= FATIGUE_CRITICAL:
        warnings.append(("CRITICAL", f"Fatigue level very high ({fat}/10). Relieve worker from duty."))
        points += 3
    elif fat >= FATIGUE_WARNING:
        warnings.append(("WARNING", f"Fatigue level elevated ({fat}/10). Monitor closely."))
        points += 1

    if record["Training Status"] == "Expired":
        warnings.append(("CRITICAL", "Safety training expired. Restrict to supervised tasks."))
        points += 3
    elif record["Training Status"] == "Due soon":
        warnings.append(("WARNING", "Safety training due soon."))
        points += 1

    inc = record["Previous Incidents"]
    if inc >= INCIDENT_CRITICAL:
        warnings.append(("CRITICAL", f"Repeated incident history ({int(inc)} incidents)."))
        points += 3
    elif inc >= INCIDENT_WARNING:
        warnings.append(("WARNING", f"Previous incident recorded ({int(inc)})."))
        points += 1

    if record["Near Misses"] >= NEAR_MISS_WARNING:
        warnings.append(("WARNING", f"Multiple near misses ({int(record['Near Misses'])})."))
        points += 1

    if record["Safety Observations"] >= OBSERVATION_WARNING:
        warnings.append(("WARNING", f"{int(record['Safety Observations'])} unsafe observations logged."))
        points += 1

    if points >= 6:
        level = "Critical"
    elif points >= 4:
        level = "High"
    elif points >= 2:
        level = "Medium"
    else:
        level = "Low"
    return level, warnings


def format_alert(worker_id, severity, message):
    """Alert text in the same layout as Figure 1 of the brief."""
    line = "=" * 53
    return (f"{line}\nMINING MONITORING ALERT\n{line}\n[{severity}]\n"
            f"Worker ID: {worker_id}\nIssue: {message}\n"
            f"Recommended Action:\n Review with the safety officer and\n"
            f" apply the appropriate safety procedure.\n{line}")


def assess_all(df):
    """Recalculate Risk Level for every worker. Returns a new DataFrame."""
    df = df.copy()
    df["Risk Level"] = [assess_worker(row)[0] for _, row in df.iterrows()]
    return df


# ---------------------------------------------------------------- operations
def add_worker(record):
    """Validate, assess and save. Returns (ok, messages)."""
    df = load_workers()
    existing = set(df["Worker ID"].astype(str).str.upper())
    errors = validate_worker(record, existing)
    if errors:
        return False, errors
    record = dict(record)
    record["Worker ID"] = str(record["Worker ID"]).strip().upper()
    record["Job Role"] = str(record["Job Role"]).strip()
    record["Risk Level"], _ = assess_worker(record)
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    save_workers(df)
    return True, [f"Worker {record['Worker ID']} saved. Risk level: {record['Risk Level']}."]


def search_workers(df, text):
    if not text.strip():
        return df
    t = text.strip().lower()
    mask = df.apply(lambda r: t in " ".join(map(str, r.values)).lower(), axis=1)
    return df[mask]


def filter_workers(df, department=None, shift=None, risk_level=None, training=None):
    for col, val in (("Department", department), ("Shift", shift),
                     ("Risk Level", risk_level), ("Training Status", training)):
        if val and val != "All":
            df = df[df[col] == val]
    return df


def summary_stats(df):
    """Key numbers for the dashboard (shared with the dashboard owner)."""
    if df.empty:
        return {"Total workers": 0, "Average PPE compliance (%)": 0.0,
                "Total near misses": 0, "High-risk workers": 0,
                "Workers with expired training": 0, "Workers with high fatigue": 0}
    return {
        "Total workers": int(len(df)),
        "Average PPE compliance (%)": round(float(df["PPE Compliance (%)"].mean()), 1),
        "Total near misses": int(df["Near Misses"].sum()),
        "High-risk workers": int(df["Risk Level"].isin(["High", "Critical"]).sum()),
        "Workers with expired training": int((df["Training Status"] == "Expired").sum()),
        "Workers with high fatigue": int((df["Fatigue Level"] >= FATIGUE_WARNING).sum()),
    }


def ppe_compliance_by_department(df):
    return df.groupby("Department")["PPE Compliance (%)"].mean().round(1)


def risk_by_department(df):
    return pd.crosstab(df["Department"], df["Risk Level"])


# ---------------------------------------------------------------- Streamlit page
def worker_safety_page(st):
    import plotly.express as px
    import auth
    auth.require_permission(st, "Worker safety data")

    st.header("Worker health and safety monitoring")
    df = assess_all(load_workers())
    tab_view, tab_add, tab_alerts = st.tabs(["Workers", "Add worker", "Alerts"])

    with tab_view:
        stats = summary_stats(df)
        cols = st.columns(len(stats))
        for c, (k, v) in zip(cols, stats.items()):
            c.metric(k, v)

        c1, c2, c3, c4, c5 = st.columns(5)
        text = c1.text_input("Search")
        dep = c2.selectbox("Department", ["All"] + DEPARTMENTS)
        sh = c3.selectbox("Shift", ["All"] + SHIFTS)
        rk = c4.selectbox("Risk level", ["All", "Low", "Medium", "High", "Critical"])
        tr = c5.selectbox("Training", ["All"] + TRAINING_STATUSES)
        view = filter_workers(search_workers(df, text), dep, sh, rk, tr)
        st.dataframe(view, use_container_width=True)
        st.caption(f"{len(view)} of {len(df)} workers shown")

        if not df.empty:
            g1, g2 = st.columns(2)
            g1.plotly_chart(px.bar(ppe_compliance_by_department(df).reset_index(),
                                   x="Department", y="PPE Compliance (%)",
                                   title="Average PPE compliance by department"),
                            use_container_width=True)
            g2.plotly_chart(px.histogram(df, x="Risk Level", color="Shift",
                                         category_orders={"Risk Level": ["Low", "Medium", "High", "Critical"]},
                                         title="Risk level by shift"),
                            use_container_width=True)

    with tab_add:
        with st.form("add_worker", clear_on_submit=False):
            a, b = st.columns(2)
            wid = a.text_input("Worker ID (e.g. W-021)")
            dep = b.selectbox("Department ", DEPARTMENTS)
            role = a.text_input("Job role")
            shift = b.selectbox("Shift ", SHIFTS)
            ppe = a.number_input("PPE compliance (%)", 0.0, 100.0, 100.0, 1.0)
            training = b.selectbox("Training status", TRAINING_STATUSES)
            fatigue = a.slider("Fatigue level (1 = rested, 10 = exhausted)", 1, 10, 3)
            obs = b.number_input("Safety observations", 0, 100, 0)
            nm = a.number_input("Near misses", 0, 100, 0)
            prev = b.number_input("Previous incidents", 0, 100, 0)
            go = st.form_submit_button("Save worker")
        if go:
            record = {"Worker ID": wid, "Department": dep, "Job Role": role, "Shift": shift,
                      "PPE Compliance (%)": ppe, "Training Status": training,
                      "Fatigue Level": fatigue, "Safety Observations": int(obs),
                      "Near Misses": int(nm), "Previous Incidents": int(prev)}
            ok, msgs = add_worker(record)
            for m in msgs:
                if ok:
                    st.success(m)
                else:
                    st.error(m)
            if ok:
                _, warns = assess_worker({**record, "Risk Level": ""})
                for sev, msg in warns:
                    if sev == "CRITICAL":
                        st.error(f"{sev}: {msg}")
                    else:
                        st.warning(f"{sev}: {msg}")

    with tab_alerts:
        shown = 0
        for _, row in df.iterrows():
            _, warns = assess_worker(row)
            for sev, msg in warns:
                if sev == "CRITICAL":
                    st.error(f"**{row['Worker ID']}** ({row['Department']}, {row['Shift']} shift): {msg}")
                    shown += 1
        if shown == 0:
            st.success("No critical worker safety alerts.")
