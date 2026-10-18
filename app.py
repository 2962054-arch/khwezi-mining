"""Khwezi Mining Monitoring — MINN2020A educational prototype.

This app uses the existing auth, alerts and risk_assessment modules. Operational
records are stored locally in data/monitoring_records.json. Thresholds are
educational examples only and are not mine or manufacturer safety limits.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

import alerts
import auth
import risk_assessment

st.set_page_config(page_title="Khwezi | Mine Operations Intelligence", page_icon="⛏️", layout="wide", initial_sidebar_state="expanded")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RECORDS_FILE = DATA_DIR / "monitoring_records.json"

# -----------------------------------------------------------------------------
# Visual system — explicit high-contrast rules for Streamlit's header/ribbon,
# sidebar, navigation, labels, inputs, tables and alerts in both themes.
# -----------------------------------------------------------------------------
def inject_theme(theme: str) -> None:
    dark = theme == "Dark"
    bg = "#0b1220" if dark else "#f3f6fa"
    panel = "#121d2d" if dark else "#ffffff"
    text = "#f4f7fb" if dark else "#172338"
    muted = "#b6c3d4" if dark else "#526176"
    border = "#34445a" if dark else "#dbe3ed"
    field = "#172538" if dark else "#ffffff"
    accent = "#35c6b0"
    st.markdown(f"""
    <style>
      :root {{ color-scheme: {'dark' if dark else 'light'}; }}
      .stApp {{ background: {bg}; color: {text}; }}
      [data-testid="stHeader"], [data-testid="stAppHeader"], header[data-testid="stHeader"] {{
        background: {panel} !important; color: {text} !important; border-bottom: 1px solid {border} !important;
      }}
      [data-testid="stHeader"] *, [data-testid="stAppHeader"] *, header[data-testid="stHeader"] * {{
        color: {text} !important; fill: {text} !important; opacity: 1 !important;
      }}
      [data-testid="stToolbar"] {{ color: {text} !important; }}
      [data-testid="stSidebar"] {{ background: {panel}; border-right: 1px solid {border}; }}
      [data-testid="stSidebar"] * {{ color: {text}; }}
      .stMarkdown, .stMarkdown p, .stMarkdown li, label, .stCaption, [data-testid="stMetricLabel"] {{ color: {text} !important; }}
      h1, h2, h3, h4, h5, h6 {{ color: {text} !important; letter-spacing: -0.02em; }}
      [data-testid="stMetric"] {{ background: {panel}; border: 1px solid {border}; padding: 15px 17px; border-radius: 14px; }}
      [data-testid="stMetricValue"] {{ color: {text} !important; font-weight: 750; }}
      [data-testid="stMetricLabel"] {{ color: {muted} !important; }}
      [data-testid="stVerticalBlockBorderWrapper"] > div {{ border-color: {border} !important; }}
      input, textarea, [data-baseweb="select"] > div, [data-baseweb="input"] > div {{
        background: {field} !important; color: {text} !important; border-color: {border} !important;
      }}
      input, textarea {{ -webkit-text-fill-color: {text} !important; }}
      [data-baseweb="select"] *, [data-baseweb="popover"] *, [role="option"] {{ color: {text} !important; }}
      [data-testid="stDataFrame"], [data-testid="stTable"] {{ border: 1px solid {border}; border-radius: 10px; overflow: hidden; }}
      {'[data-testid="stDataFrame"] { filter: invert(1) hue-rotate(180deg); }' if dark else ''}
      [data-testid="stTable"] td, [data-testid="stTable"] th {{ color: {text} !important; background: {panel} !important; }}
      input::placeholder, textarea::placeholder {{ color: {muted} !important; -webkit-text-fill-color: {muted} !important; opacity: 1; }}
      [data-testid="stNumberInput"] button {{ background: {field} !important; color: {text} !important; }}
      [data-testid="stNumberInput"] button * {{ color: {text} !important; fill: {text} !important; }}
      [data-testid="stDateInput"] *, [data-testid="stTextInput"] *, [data-testid="stTextArea"] * {{ color: {text} !important; }}
      [data-testid="stAlert"] {{ border-radius: 10px; }}
      .khwezi-ribbon {{ background: linear-gradient(115deg, #0d2830 0%, #135c61 58%, #167c78 100%);
        border: 1px solid #277d7b; border-radius: 18px; padding: 25px 28px; color: #ffffff !important;
        margin: 2px 0 20px 0; box-shadow: 0 9px 26px rgba(8,25,40,.13); }}
      .khwezi-ribbon * {{ color: #ffffff !important; }}
      .khwezi-eyebrow {{ font-size: 11px; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; opacity: .88; }}
      .khwezi-title {{ font-size: clamp(25px, 3vw, 36px); font-weight: 800; line-height: 1.15; margin: 7px 0 8px; }}
      .khwezi-subtitle {{ font-size: 14px; line-height: 1.6; max-width: 820px; color: #e5fffb !important; }}
      .khwezi-chip {{ display:inline-block; padding:5px 10px; border:1px solid rgba(255,255,255,.38); border-radius:100px;
        font-size:11px; font-weight:700; margin-top:14px; background:rgba(255,255,255,.09); }}
      .section-kicker {{ color: {muted} !important; text-transform: uppercase; letter-spacing: .12em; font-size: 11px; font-weight: 800; }}
      .small-note {{ color: {muted} !important; font-size: 12px; }}
      /* Buttons: set background AND text together so they are always readable */
      div.stButton > button, div.stDownloadButton > button, div.stFormSubmitButton > button,
      button[data-testid^="stBaseButton"] {{
        border-radius: 9px; font-weight: 700; border: 1px solid {border} !important;
        background: {panel} !important; color: {text} !important;
      }}
      div.stButton > button *, div.stDownloadButton > button *, div.stFormSubmitButton > button *,
      button[data-testid^="stBaseButton"] * {{ color: {text} !important; }}
      div.stButton > button:hover, div.stDownloadButton > button:hover, div.stFormSubmitButton > button:hover,
      button[data-testid^="stBaseButton"]:hover {{ border-color: {accent} !important; background: {field} !important; }}
      div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"],
      button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primaryFormSubmit"] {{
        background: {accent} !important; border-color: {accent} !important; color: #062b2c !important;
      }}
      button[data-testid="stBaseButton-primary"] *, button[data-testid="stBaseButton-primaryFormSubmit"] *,
      div.stButton > button[kind="primary"] *, div.stFormSubmitButton > button[kind="primary"] * {{ color: #062b2c !important; }}
      /* Dropdown menus / popovers / options */
      [data-baseweb="popover"], [data-baseweb="popover"] > div, [data-baseweb="menu"], [data-baseweb="menu"] ul,
      ul[role="listbox"], div[role="listbox"] {{ background: {panel} !important; color: {text} !important; }}
      [role="option"], [role="option"] *, [data-baseweb="menu"] li, [data-baseweb="menu"] li * {{
        background: {panel} !important; color: {text} !important; }}
      [role="option"]:hover, [role="option"][aria-selected="true"], [data-baseweb="menu"] li:hover {{
        background: {field} !important; }}
      [data-baseweb="select"] svg, [data-baseweb="select"] input {{ color: {text} !important; fill: {text} !important; }}
      [data-testid="stSelectbox"] div, [data-testid="stMultiSelect"] div {{ color: {text} !important; }}
      [data-testid="stRadio"] label, [data-testid="stRadio"] label * , [data-testid="stCheckbox"] label * {{ color: {text} !important; }}
      [data-testid="stTabs"] button, [data-testid="stTabs"] button * {{ color: {text} !important; }}
      [data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {{ color: {text} !important; }}
      [data-testid="stSidebar"] [role="radiogroup"] label {{ padding: 7px 9px; border-radius: 8px; }}
      hr {{ border-color: {border}; }}
    </style>
    """, unsafe_allow_html=True)


def ribbon(eyebrow: str, title: str, subtitle: str, chip: str = "OPERATIONS INTELLIGENCE") -> None:
    st.markdown(f"""
      <section class="khwezi-ribbon">
        <div class="khwezi-eyebrow">{eyebrow}</div>
        <div class="khwezi-title">{title}</div>
        <div class="khwezi-subtitle">{subtitle}</div>
        <span class="khwezi-chip">⛏ &nbsp; {chip}</span>
      </section>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Local JSON repository. Records persist between app reruns and restarts.
# -----------------------------------------------------------------------------
def seed_data() -> dict:
    today = date.today()
    return {
        "workers": [
            {"Worker ID":"WRK-001","Name":"Demo Worker A","Department":"Production","Job Role":"Machine Operator","Shift":"Day","PPE Compliance":98,"Training Status":"Current","Fatigue Level":2,"Near Misses":0,"Previous Incidents":0,"Observation":"No concern recorded","Updated":str(today)},
            {"Worker ID":"WRK-002","Name":"Demo Worker B","Department":"Engineering","Job Role":"Artisan Assistant","Shift":"Night","PPE Compliance":84,"Training Status":"Current","Fatigue Level":6,"Near Misses":1,"Previous Incidents":0,"Observation":"Fatigue check recommended","Updated":str(today)},
            {"Worker ID":"WRK-003","Name":"Demo Worker C","Department":"Plant","Job Role":"Plant Operator","Shift":"Day","PPE Compliance":72,"Training Status":"Due","Fatigue Level":8,"Near Misses":0,"Previous Incidents":1,"Observation":"PPE and fatigue follow-up required","Updated":str(today)},
        ],
        "incidents": [
            {"Incident ID":"INC-001","Date":str(today-timedelta(days=4)),"Time":"09:20","Shift":"Day","Location":"Plant 1","Department":"Plant","Incident Type":"Near miss","Severity":"Medium","Injury Status":"No injury","Lost Time Injury":"No","Cause":"Obstructed walkway","Corrective Action":"Walkway cleared and inspected","Status":"Closed"},
            {"Incident ID":"INC-002","Date":str(today-timedelta(days=1)),"Time":"22:10","Shift":"Night","Location":"Workshop","Department":"Engineering","Incident Type":"Unsafe condition","Severity":"High","Injury Status":"No injury","Lost Time Injury":"No","Cause":"Guarding concern","Corrective Action":"Inspect guarding and isolate if required","Status":"Open"},
        ],
        "equipment": [
            {"Equipment ID":"TRK-012","Equipment Type":"Haul truck","Manufacturer":"Demo manufacturer","Department":"Production","Operating Hours":1200,"Temperature":88,"Vibration":5.8,"Fuel Consumption":32.5,"Brake Status":"Good","Tyre Status":"Good","Engine Status":"Monitor","Maintenance Status":"Operational","Downtime":18,"Next Maintenance":str(today+timedelta(days=4)),"Last Updated":str(today)},
            {"Equipment ID":"LD-004","Equipment Type":"Loader","Manufacturer":"Demo manufacturer","Department":"Production","Operating Hours":890,"Temperature":74,"Vibration":3.2,"Fuel Consumption":25.1,"Brake Status":"Good","Tyre Status":"Monitor","Engine Status":"Good","Maintenance Status":"Operational","Downtime":6,"Next Maintenance":str(today+timedelta(days=20)),"Last Updated":str(today)},
            {"Equipment ID":"CV-002","Equipment Type":"Conveyor","Manufacturer":"Demo manufacturer","Department":"Plant","Operating Hours":2150,"Temperature":105,"Vibration":8.7,"Fuel Consumption":0,"Brake Status":"Not applicable","Tyre Status":"Not applicable","Engine Status":"Critical","Maintenance Status":"Under maintenance","Downtime":42,"Next Maintenance":str(today-timedelta(days=2)),"Last Updated":str(today)},
        ],
        "risks": [
            {"Observation ID":"RISK-001","Date":str(today),"Department":"Production","Location":"Haul road","Hazard":"Vehicle interaction","Likelihood":3,"Consequence":4,"Risk Score":12,"Classification":"High","Controls":"Traffic separation and spotter","Owner":"Shift supervisor","Status":"Open"},
        ],
    }


def load_data() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not RECORDS_FILE.exists():
        data = seed_data()
        save_data(data)
        return data
    try:
        with RECORDS_FILE.open("r", encoding="utf-8") as f:
            loaded = json.load(f)
        defaults = {"workers": [], "incidents": [], "equipment": [], "risks": []}
        defaults.update({k: loaded.get(k, []) for k in defaults})
        return defaults
    except (OSError, json.JSONDecodeError):
        st.error("The monitoring data file could not be read. Please back up data/monitoring_records.json and check its JSON format.")
        return {"workers": [], "incidents": [], "equipment": [], "risks": []}


def save_data(data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temp = RECORDS_FILE.with_suffix(".tmp")
    with temp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    temp.replace(RECORDS_FILE)


def as_df(records: list) -> pd.DataFrame:
    return pd.DataFrame(records) if records else pd.DataFrame()


def safe_num(value, default=0.0) -> float:
    try:
        n = float(value)
        return n if pd.notna(n) else default
    except (TypeError, ValueError):
        return default


def build_alerts(data: dict) -> list[dict]:
    result = []
    for w in data["workers"]:
        for a in alerts.check_worker_record({"Worker ID":w.get("Worker ID"),"PPE Compliance":w.get("PPE Compliance"),"Fatigue Level":w.get("Fatigue Level")}):
            result.append(a)
    for e in data["equipment"]:
        rec = {"Equipment ID":e.get("Equipment ID"),"Temperature":e.get("Temperature"),"Vibration":e.get("Vibration"),"Operating Hours":e.get("Operating Hours"),"Downtime":e.get("Downtime"),"Next Maintenance":e.get("Next Maintenance")}
        for a in alerts.check_equipment_record(rec): result.append(a)
        if e.get("Maintenance Status") == "Under maintenance":
            result.append(alerts.make_alert("WARNING", "Equipment under maintenance", e.get("Equipment ID"), "Maintenance status", "Under maintenance", "Not available for normal operation", "Confirm work order, isolation and return-to-service checks."))
    for i in data["incidents"]:
        a = alerts.check_incident(i.get("Incident ID"), i.get("Severity"))
        if a: result.append(a)
    for r in data["risks"]:
        a = alerts.check_risk_observation(r.get("Observation ID"), r.get("Classification"))
        if a: result.append(a)
    # Deduplicate records that may share a source and parameter.
    unique, seen = [], set()
    for a in result:
        key = (a.get("level"), a.get("type"), a.get("subject_id"), a.get("parameter"))
        if key not in seen:
            unique.append(a); seen.add(key)
    return unique


def _is_date(value: str) -> bool:
    try:
        date.fromisoformat(value[:10])
        return True
    except (TypeError, ValueError):
        return False


def equipment_availability(e: dict) -> float:
    op = max(0.0, safe_num(e.get("Operating Hours")))
    down = max(0.0, safe_num(e.get("Downtime")))
    total = op + down
    return (op / total * 100) if total > 0 else 0.0


def maintenance_state(e: dict) -> str:
    if e.get("Maintenance Status") == "Under maintenance": return "Under maintenance"
    try: due = date.fromisoformat(str(e.get("Next Maintenance", ""))[:10])
    except ValueError: return "Date not set"
    days = (due - date.today()).days
    if days < 0: return "Overdue"
    if days <= 7: return "Due soon"
    return "Scheduled"


def metric_row(items: list[tuple[str, object, str | None]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value, delta) in zip(cols, items):
        col.metric(label, value, delta)


def filtered_table(df: pd.DataFrame, key: str, search_columns: list[str] | None = None) -> pd.DataFrame:
    if df.empty:
        st.info("No records have been saved for this section yet.")
        return df
    q = st.text_input("Search records", placeholder="Type an ID, department, status or keyword…", key=f"search_{key}")
    if q.strip():
        cols = [c for c in (search_columns or list(df.columns)) if c in df.columns]
        mask = df[cols].astype(str).apply(lambda col: col.str.contains(q.strip(), case=False, na=False)).any(axis=1)
        df = df[mask]
    st.caption(f"Showing {len(df)} record(s)")
    st.dataframe(df, use_container_width=True, hide_index=True)
    return df


# -----------------------------------------------------------------------------
# Authentication and global layout
# -----------------------------------------------------------------------------
if not auth.is_logged_in(st):
    # Apply a reliable light login theme; the main header remains high contrast.
    inject_theme("Light")
    ribbon("KHWEZI MINING · SECURE PORTAL", "Mine Operations Intelligence", "A single workspace for worker safety, incidents, equipment health, maintenance and operational risk.", "SECURE SIGN-IN")
    auth.login_page(st)
    st.stop()

role = st.session_state["role"]
username = st.session_state.get("user", "User")
with st.sidebar:
    st.markdown("## ⛏ Khwezi Mining")
    st.caption("HEALTH · SAFETY · RELIABILITY")
    st.divider()
    st.markdown(f"**Role:** {role}")
    theme = st.selectbox("Appearance / Theme", ["Light", "Dark"], index=0, key="theme_choice")
    st.caption(f"Current theme: {theme}")
    st.caption("Build: alerts-fix v3 (18 Oct 2026)")
    st.divider()
    pages = ["Dashboard"]
    if auth.has_permission(role, "Worker safety data"): pages.append("Worker Safety")
    if auth.has_permission(role, "Safety incidents"): pages.append("Safety Incidents")
    if auth.has_permission(role, "Equipment data"): pages.append("Equipment Monitoring")
    if auth.has_permission(role, "Maintenance data"): pages.append("Maintenance")
    if auth.has_permission(role, "Risk assessment"): pages.append("Risk Assessment")
    if auth.has_permission(role, "Generate reports"): pages.append("Reports & Analytics")
    if auth.has_permission(role, "Manage users"): pages.append("Manage Users")
    page = st.radio("Navigation", pages, label_visibility="visible")
    st.divider()
    st.caption("Prototype thresholds only — not a substitute for mine procedures or manufacturer limits.")
    auth.logout_button(st)

inject_theme(theme)
data = load_data()
workers_df, incidents_df = as_df(data["workers"]), as_df(data["incidents"])
equipment_df, risks_df = as_df(data["equipment"]), as_df(data["risks"])
all_alerts = build_alerts(data)
critical_count = sum(a["level"] == "CRITICAL" for a in all_alerts)
warning_count = sum(a["level"] == "WARNING" for a in all_alerts)

# -----------------------------------------------------------------------------
# Dashboard
# -----------------------------------------------------------------------------
if page == "Dashboard":
    ribbon("OPERATIONS OVERVIEW", "Khwezi Mining Control Room", "See the health of your workforce, safety events and critical equipment at a glance. Use the modules to investigate, record and analyse operational data.")
    metric_row([
        ("Workers monitored", len(data["workers"]), None),
        ("Safety incidents", len(data["incidents"]), None),
        ("Equipment assets", len(data["equipment"]), None),
        ("Critical alerts", critical_count, "Immediate review" if critical_count else "No critical alerts"),
        ("Warnings", warning_count, "Review required" if warning_count else "No active warnings"),
    ])
    st.markdown("### Operational picture")
    left, right = st.columns([1.15, 1])
    with left:
        st.markdown("#### Equipment condition")
        if equipment_df.empty:
            st.info("Add equipment records to start viewing condition trends.")
        else:
            plot_df = equipment_df.copy()
            for c in ["Temperature", "Vibration"]: plot_df[c] = pd.to_numeric(plot_df.get(c), errors="coerce")
            temp_col, vib_col = st.columns(2)
            with temp_col:
                st.caption("Temperature · °C")
                temp_series = plot_df.set_index("Equipment ID")["Temperature"] if "Temperature" in plot_df else pd.Series(dtype=float)
                st.bar_chart(temp_series, height=220)
            with vib_col:
                st.caption("Vibration · mm/s")
                vib_series = plot_df.set_index("Equipment ID")["Vibration"] if "Vibration" in plot_df else pd.Series(dtype=float)
                st.bar_chart(vib_series, height=220)
            st.caption("Example thresholds: temperature warning at 80°C and critical above 100°C; vibration warning at 5 mm/s and critical above 8 mm/s. Educational prototype values only.")
    with right:
        st.markdown("#### Maintenance availability")
        if equipment_df.empty:
            st.info("No equipment data available.")
        else:
            avail = pd.DataFrame([{"Equipment ID":e.get("Equipment ID"), "Availability (%)":round(equipment_availability(e),1), "Maintenance":maintenance_state(e)} for e in data["equipment"]])
            st.dataframe(avail, use_container_width=True, hide_index=True)
    st.markdown("#### Active alerts")
    if all_alerts:
        for a in sorted(all_alerts, key=lambda x: 0 if x["level"] == "CRITICAL" else 1)[:8]:
            msg = f"**{a['type']}** · {a['subject_id']} · {a['parameter']}: {a['value']} — {a['action']}"
            if a["level"] == "CRITICAL":
                st.error(msg)
            else:
                st.warning(msg)
    else: st.success("No alerts generated from the current records.")
    with st.expander("Access available to your role"):
        for f in auth.allowed_functions(role): st.write("✓", f)
    st.caption("Sample records are clearly labelled as demo records. Replace them with your group's validated project data before presenting results.")

# -----------------------------------------------------------------------------
# Worker health and safety
# -----------------------------------------------------------------------------
elif page == "Worker Safety":
    auth.require_permission(st, "Worker safety data")
    ribbon("PEOPLE & SAFETY", "Worker Safety Monitoring", "Track PPE compliance, fatigue, training and observations. The application flags values that cross the prototype thresholds.")
    if not workers_df.empty:
        metric_row([("Workers",len(workers_df),None),("Average PPE compliance",f"{pd.to_numeric(workers_df['PPE Compliance'],errors='coerce').mean():.1f}%" if 'PPE Compliance' in workers_df else "—",None),("High fatigue (≥8)",int((pd.to_numeric(workers_df.get('Fatigue Level',pd.Series(dtype=float)),errors='coerce')>=8).sum()),None),("Training due",int((workers_df.get('Training Status',pd.Series(dtype=str))=='Due').sum()),None)])
    st.markdown("### Record a worker safety check")
    existing_ids = [str(w.get("Worker ID")) for w in data["workers"]]
    choice = st.selectbox("Worker", ["Select existing worker", "Register a new worker"] + existing_ids, key="worker_choice")
    with st.form("worker_form", clear_on_submit=False):
        if choice == "Register a new worker":
            c1,c2,c3 = st.columns(3)
            worker_id = c1.text_input("New Worker ID", placeholder="WRK-004")
            name = c2.text_input("Worker name / label", placeholder="Worker name")
            department = c3.selectbox("Department", ["Production","Engineering","Plant","Safety","Maintenance","Other"])
            c4,c5,c6 = st.columns(3)
            job_role = c4.selectbox("Job role", ["Machine Operator","Artisan","Drill Operator","Plant Operator","Supervisor","Engineer","Other"])
            shift = c5.selectbox("Shift", ["Day","Night","Rotating"])
            training = c6.selectbox("Safety training", ["Current","Due","Expired","Unknown"])
        else:
            selected = next((w for w in data["workers"] if w.get("Worker ID")==choice), {})
            worker_id = choice if choice != "Select existing worker" else ""
            name = selected.get("Name", "")
            department = selected.get("Department", "Production")
            job_role = selected.get("Job Role", "Machine Operator")
            shift = selected.get("Shift", "Day")
            training = selected.get("Training Status", "Current")
            if choice != "Select existing worker": st.caption(f"Updating record for {name or worker_id} · {department} · {shift} shift")
        c1,c2,c3 = st.columns(3)
        ppe = c1.slider("PPE compliance (%)", 0, 100, int(safe_num(next((w.get("PPE Compliance") for w in data['workers'] if w.get('Worker ID')==worker_id), 100),100)))
        fatigue = c2.slider("Fatigue level (1–10)", 1, 10, int(safe_num(next((w.get("Fatigue Level") for w in data['workers'] if w.get('Worker ID')==worker_id), 2),2)))
        near_misses = c3.number_input("Near misses recorded", min_value=0, max_value=10000, value=int(safe_num(next((w.get("Near Misses") for w in data['workers'] if w.get('Worker ID')==worker_id),0))), step=1)
        observation = st.text_area("Safety observation / corrective action", placeholder="Describe what was observed and what follow-up is needed…")
        save_worker = st.form_submit_button("Save worker safety record", type="primary")
    if save_worker:
        if not worker_id or worker_id == "Select existing worker": st.error("Choose an existing worker or enter a new Worker ID.")
        elif choice == "Register a new worker" and any(w.get("Worker ID"," ").lower()==worker_id.strip().lower() for w in data["workers"]): st.error("That Worker ID already exists. Choose the existing worker instead.")
        else:
            record = {"Worker ID":worker_id.strip(),"Name":name or worker_id.strip(),"Department":department,"Job Role":job_role,"Shift":shift,"PPE Compliance":int(ppe),"Training Status":training,"Fatigue Level":int(fatigue),"Near Misses":int(near_misses),"Previous Incidents":int(safe_num(next((w.get("Previous Incidents") for w in data['workers'] if w.get('Worker ID')==worker_id),0))),"Observation":observation.strip(),"Updated":str(date.today())}
            data["workers"] = [w for w in data["workers"] if w.get("Worker ID") != worker_id] + [record]
            save_data(data); st.success("Worker safety record saved."); st.rerun()
    st.markdown("### Worker register")
    filtered_table(as_df(data["workers"]), "workers", ["Worker ID","Name","Department","Job Role","Shift","Training Status","Observation"])

# -----------------------------------------------------------------------------
# Safety incidents: create, browse, filter, and trend
# -----------------------------------------------------------------------------
elif page == "Safety Incidents":
    auth.require_permission(st, "Safety incidents")
    ribbon("INCIDENT MANAGEMENT", "Safety Incident Register", "Capture the incident context, corrective actions and status; search records and review patterns by department, shift and severity.")
    st.markdown("### Record an incident")
    with st.form("incident_form", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        iid = c1.text_input("Incident ID", placeholder="INC-003")
        incident_date = c2.date_input("Date", value=date.today())
        incident_time = c3.text_input("Time (HH:MM)", value=datetime.now().strftime("%H:%M"))
        c1,c2,c3 = st.columns(3)
        shift = c1.selectbox("Shift", ["Day","Night","Rotating","Unknown"])
        location = c2.text_input("Location", placeholder="Workshop / haul road / plant")
        department = c3.selectbox("Department", ["Production","Engineering","Plant","Safety","Maintenance","Other"])
        c1,c2,c3 = st.columns(3)
        itype = c1.selectbox("Incident type", ["Near miss","Unsafe condition","Unsafe act","Injury","Equipment-related","Environmental","Other"])
        severity = c2.selectbox("Severity", ["Low","Medium","High","Critical"])
        injury = c3.selectbox("Injury status", ["No injury","First aid","Medical treatment","Lost-time injury"])
        c1,c2 = st.columns(2)
        cause = c1.text_input("Cause / contributing factor")
        action = c2.text_input("Corrective action")
        status = st.selectbox("Incident status", ["Open","Under investigation","Action in progress","Closed"])
        submit_incident = st.form_submit_button("Save incident", type="primary")
    if submit_incident:
        if not iid.strip(): st.error("Incident ID is required.")
        elif any(i.get("Incident ID","").lower()==iid.strip().lower() for i in data["incidents"]): st.error("That Incident ID already exists.")
        else:
            data["incidents"].append({"Incident ID":iid.strip(),"Date":str(incident_date),"Time":incident_time.strip(),"Shift":shift,"Location":location.strip(),"Department":department,"Incident Type":itype,"Severity":severity,"Injury Status":injury,"Lost Time Injury":"Yes" if injury=="Lost-time injury" else "No","Cause":cause.strip(),"Corrective Action":action.strip(),"Status":status})
            save_data(data)
            a = alerts.check_incident(iid.strip(),severity)
            if a: st.warning(f"Alert generated: {a['level']} — {a['type']}. {a['action']}")
            st.success("Incident saved to the register."); st.rerun()
    st.markdown("### Incident register")
    idf = as_df(data["incidents"])
    if not idf.empty:
        f1,f2,f3 = st.columns(3)
        sev_filter = f1.multiselect("Severity filter", sorted(idf["Severity"].dropna().unique().tolist()), default=[])
        dept_filter = f2.multiselect("Department filter", sorted(idf["Department"].dropna().unique().tolist()), default=[])
        status_filter = f3.multiselect("Status filter", sorted(idf["Status"].dropna().unique().tolist()), default=[])
        if sev_filter: idf=idf[idf["Severity"].isin(sev_filter)]
        if dept_filter: idf=idf[idf["Department"].isin(dept_filter)]
        if status_filter: idf=idf[idf["Status"].isin(status_filter)]
    filtered_table(idf,"incidents",["Incident ID","Location","Department","Incident Type","Severity","Status","Cause"])
    if not incidents_df.empty:
        st.markdown("### Incident analysis")
        a,b = st.columns(2)
        with a:
            st.write("Incidents by severity")
            st.bar_chart(incidents_df["Severity"].value_counts())
        with b:
            st.write("Incidents by department")
            st.bar_chart(incidents_df["Department"].value_counts())

# -----------------------------------------------------------------------------
# Equipment database and condition monitoring
# -----------------------------------------------------------------------------
elif page == "Equipment Monitoring":
    auth.require_permission(st, "Equipment data")
    ribbon("ASSET HEALTH", "Equipment Condition Monitoring", "Monitor temperature, vibration, operating time, downtime, component status and maintenance state. Thresholds shown are educational prototype values.")
    st.markdown("### Add or update equipment")
    equipment_ids = [str(e.get("Equipment ID")) for e in data["equipment"]]
    choice = st.selectbox("Equipment record", ["Register new equipment"] + equipment_ids, key="equipment_choice")
    selected = next((e for e in data["equipment"] if e.get("Equipment ID")==choice), {})
    with st.form("equipment_form"):
        c1,c2,c3 = st.columns(3)
        eid = c1.text_input("Equipment ID", value="" if choice=="Register new equipment" else choice, placeholder="TRK-013")
        etype = c2.selectbox("Equipment type", ["Haul truck","Loader","Excavator","Drilling machine","Bulldozer","Scraper winch","Crusher","Conveyor","Other"], index=( ["Haul truck","Loader","Excavator","Drilling machine","Bulldozer","Scraper winch","Crusher","Conveyor","Other"].index(selected.get("Equipment Type")) if selected.get("Equipment Type") in ["Haul truck","Loader","Excavator","Drilling machine","Bulldozer","Scraper winch","Crusher","Conveyor","Other"] else 0))
        manufacturer = c3.text_input("Manufacturer", value=selected.get("Manufacturer",""), placeholder="Manufacturer / model")
        c1,c2,c3 = st.columns(3)
        department = c1.selectbox("Department", ["Production","Plant","Engineering","Maintenance","Other"], index=(["Production","Plant","Engineering","Maintenance","Other"].index(selected.get("Department")) if selected.get("Department") in ["Production","Plant","Engineering","Maintenance","Other"] else 0))
        operating = c2.number_input("Operating hours", min_value=0.0, max_value=10000000.0, value=float(safe_num(selected.get("Operating Hours",0))), step=10.0)
        downtime = c3.number_input("Downtime hours", min_value=0.0, max_value=10000000.0, value=float(safe_num(selected.get("Downtime",0))), step=1.0)
        c1,c2,c3 = st.columns(3)
        temp = c1.number_input("Temperature (°C)", min_value=0.0, max_value=500.0, value=float(safe_num(selected.get("Temperature",70))), step=1.0)
        vibration = c2.number_input("Vibration (mm/s)", min_value=0.0, max_value=100.0, value=float(safe_num(selected.get("Vibration",2))), step=0.1, format="%.1f")
        fuel = c3.number_input("Fuel consumption (L/h, if applicable)", min_value=0.0, max_value=100000.0, value=float(safe_num(selected.get("Fuel Consumption",0))), step=0.5)
        c1,c2,c3 = st.columns(3)
        brake = c1.selectbox("Brake status", ["Good","Monitor","Fault","Not applicable"], index=(["Good","Monitor","Fault","Not applicable"].index(selected.get("Brake Status")) if selected.get("Brake Status") in ["Good","Monitor","Fault","Not applicable"] else 0))
        tyre = c2.selectbox("Tyre status", ["Good","Monitor","Fault","Not applicable"], index=(["Good","Monitor","Fault","Not applicable"].index(selected.get("Tyre Status")) if selected.get("Tyre Status") in ["Good","Monitor","Fault","Not applicable"] else 0))
        engine = c3.selectbox("Engine status", ["Good","Monitor","Fault","Critical","Not applicable"], index=(["Good","Monitor","Fault","Critical","Not applicable"].index(selected.get("Engine Status")) if selected.get("Engine Status") in ["Good","Monitor","Fault","Critical","Not applicable"] else 0))
        c1,c2 = st.columns(2)
        mstatus = c1.selectbox("Maintenance status", ["Operational","Under maintenance","Out of service","Inspection required"], index=(["Operational","Under maintenance","Out of service","Inspection required"].index(selected.get("Maintenance Status")) if selected.get("Maintenance Status") in ["Operational","Under maintenance","Out of service","Inspection required"] else 0))
        next_date = c2.date_input("Next maintenance date", value=(date.fromisoformat(str(selected.get("Next Maintenance"))) if selected.get("Next Maintenance") and str(selected.get("Next Maintenance"))[:10] and _is_date(str(selected.get("Next Maintenance"))) else date.today()+timedelta(days=30)))
        submit_equipment = st.form_submit_button("Save equipment record", type="primary")
    if submit_equipment:
        if not eid.strip(): st.error("Equipment ID is required.")
        elif choice == "Register new equipment" and any(e.get("Equipment ID","").lower()==eid.strip().lower() for e in data["equipment"]): st.error("That Equipment ID already exists. Select it from the dropdown to update it.")
        else:
            rec={"Equipment ID":eid.strip(),"Equipment Type":etype,"Manufacturer":manufacturer.strip(),"Department":department,"Operating Hours":float(operating),"Temperature":float(temp),"Vibration":float(vibration),"Fuel Consumption":float(fuel),"Brake Status":brake,"Tyre Status":tyre,"Engine Status":engine,"Maintenance Status":mstatus,"Downtime":float(downtime),"Next Maintenance":str(next_date),"Last Updated":str(date.today())}
            data["equipment"]=[e for e in data["equipment"] if e.get("Equipment ID")!=eid.strip()]+[rec]
            save_data(data)
            checks=alerts.check_equipment_record({"Equipment ID":eid.strip(),"Temperature":temp,"Vibration":vibration,"Operating Hours":operating,"Downtime":downtime,"Next Maintenance":next_date})
            st.success("Equipment record saved.")
            for a in checks:
                alert_msg = f"{a['level']}: {a['type']} — {a['action']}"
                if a["level"] == "CRITICAL":
                    st.error(alert_msg)
                else:
                    st.warning(alert_msg)
            st.rerun()
    st.markdown("### Equipment register")
    eq = as_df(data["equipment"])
    if not eq.empty:
        eq["Availability (%)"] = [round(equipment_availability(e),1) for e in data["equipment"]]
        eq["Maintenance Due Status"] = [maintenance_state(e) for e in data["equipment"]]
        filtered_table(eq,"equipment",["Equipment ID","Equipment Type","Department","Manufacturer","Maintenance Status","Engine Status","Maintenance Due Status"])
        st.markdown("### Parameter checks")
        for e in data["equipment"]:
            issues=[]
            if safe_num(e.get("Temperature"))>100: issues.append(f"Temperature critical: {e.get('Temperature')} °C")
            elif safe_num(e.get("Temperature"))>=80: issues.append(f"Temperature warning: {e.get('Temperature')} °C")
            if safe_num(e.get("Vibration"))>8: issues.append(f"Vibration critical: {e.get('Vibration')} mm/s")
            elif safe_num(e.get("Vibration"))>=5: issues.append(f"Vibration warning: {e.get('Vibration')} mm/s")
            if e.get("Brake Status")=="Fault" or e.get("Tyre Status")=="Fault" or e.get("Engine Status") in ["Fault","Critical"]: issues.append("Component status requires inspection")
            if issues: st.error(f"**{e.get('Equipment ID')}** — " + " · ".join(issues))
            else: st.success(f"**{e.get('Equipment ID')}** — within the example temperature/vibration thresholds; continue normal inspections.")

# -----------------------------------------------------------------------------
# Maintenance: availability, status, due/overdue and repeated alerts
# -----------------------------------------------------------------------------
elif page == "Maintenance":
    auth.require_permission(st, "Maintenance data")
    ribbon("MAINTENANCE PLANNING", "Reliability & Maintenance", "Identify equipment due or overdue for maintenance, under maintenance, with excessive downtime or low availability.")
    eqdata = data["equipment"]
    if eqdata:
        states=[maintenance_state(e) for e in eqdata]
        metric_row([("Overdue",states.count("Overdue"),None),("Due within 7 days",states.count("Due soon"),None),("Under maintenance",sum(e.get("Maintenance Status")=="Under maintenance" for e in eqdata),None),("Low availability (<80%)",sum(equipment_availability(e)<80 for e in eqdata),None)])
        maint = pd.DataFrame([{"Equipment ID":e.get("Equipment ID"),"Type":e.get("Equipment Type"),"Maintenance status":e.get("Maintenance Status"),"Next maintenance":e.get("Next Maintenance"),"Due status":maintenance_state(e),"Operating hours":e.get("Operating Hours"),"Downtime hours":e.get("Downtime"),"Availability (%)":round(equipment_availability(e),1)} for e in eqdata])
        st.dataframe(maint, use_container_width=True, hide_index=True)
        due_only=st.checkbox("Show only equipment requiring attention", value=False)
        if due_only:
            urgent=maint[maint["Due status"].isin(["Overdue","Due soon","Under maintenance"]) | (maint["Availability (%)"]<80) | (maint["Maintenance status"].isin(["Out of service","Inspection required"]))]
            st.dataframe(urgent,use_container_width=True,hide_index=True)
        st.markdown("### Maintenance attention list")
        any_issue=False
        for e in eqdata:
            reasons=[]
            state=maintenance_state(e)
            if state in ["Overdue","Due soon","Under maintenance","Date not set"]: reasons.append(state)
            if equipment_availability(e)<80: reasons.append(f"Low availability {equipment_availability(e):.1f}%")
            if safe_num(e.get("Downtime"))>24: reasons.append(f"High downtime {e.get('Downtime')} h")
            if e.get("Maintenance Status") in ["Out of service","Inspection required"]: reasons.append(e.get("Maintenance Status"))
            if reasons:
                any_issue=True
                msg=f"**{e.get('Equipment ID')}** — " + "; ".join(reasons)
                if "Overdue" in reasons or "Out of service" in reasons:
                    st.error(msg)
                else:
                    st.warning(msg)
        if not any_issue: st.success("No equipment is currently flagged by the prototype maintenance checks.")
    else: st.info("Add equipment records in Equipment Monitoring to populate maintenance planning.")

# -----------------------------------------------------------------------------
# Risk assessment with persisted observations and 5x5 matrix
# -----------------------------------------------------------------------------
elif page == "Risk Assessment":
    auth.require_permission(st, "Risk assessment")
    ribbon("HAZARD REVIEW", "Risk Assessment", "Record hazards using the brief's 1–5 likelihood and consequence scales. The risk score is likelihood × consequence.")
    with st.form("risk_form", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        rid=c1.text_input("Observation ID",placeholder="RISK-002")
        rdate=c2.date_input("Assessment date",value=date.today())
        dept=c3.selectbox("Department",["Production","Engineering","Plant","Safety","Maintenance","Other"])
        c1,c2 = st.columns(2)
        location=c1.text_input("Location",placeholder="Where is the hazard?")
        hazard=c2.text_input("Hazard / unsafe observation",placeholder="Describe the hazard")
        c1,c2 = st.columns(2)
        likelihood=c1.select_slider("Likelihood (1–5)",options=[1,2,3,4,5],value=3,help="1 = Rare; 5 = Almost certain")
        consequence=c2.select_slider("Consequence (1–5)",options=[1,2,3,4,5],value=3,help="1 = Insignificant; 5 = Catastrophic")
        controls=st.text_area("Existing / proposed controls")
        owner=st.text_input("Responsible person / role",placeholder="Shift supervisor")
        status=st.selectbox("Action status",["Open","Controls in progress","Controlled","Closed"])
        save_risk=st.form_submit_button("Calculate and save risk",type="primary")
    if save_risk:
        if not rid.strip() or not hazard.strip(): st.error("Observation ID and hazard description are required.")
        elif any(r.get("Observation ID","").lower()==rid.strip().lower() for r in data["risks"]): st.error("That Observation ID already exists.")
        else:
            result=risk_assessment.assess_risk(likelihood,consequence)
            rec={"Observation ID":rid.strip(),"Date":str(rdate),"Department":dept,"Location":location.strip(),"Hazard":hazard.strip(),"Likelihood":likelihood,"Consequence":consequence,"Risk Score":result["risk_score"],"Classification":result["classification"],"Controls":controls.strip(),"Owner":owner.strip(),"Status":status}
            data["risks"].append(rec); save_data(data)
            st.success(f"Risk saved: score {result['risk_score']} — {result['classification']}.")
            if result["warning"]:
                if result["classification"] == "Critical":
                    st.error(result["warning"])
                else:
                    st.warning(result["warning"])
            st.rerun()
    st.markdown("### Risk register")
    rdf=as_df(data["risks"])
    filtered_table(rdf,"risks",["Observation ID","Department","Location","Hazard","Classification","Owner","Status"])
    st.markdown("### 5 × 5 risk matrix")
    matrix=[]
    for l in range(5,0,-1):
        row={"Likelihood":f"{l} — {risk_assessment.LIKELIHOOD_LABELS[l]}"}
        for c in range(1,6):
            score=l*c; cls=risk_assessment.classify_risk(score); row[f"C{c}"]=f"{score} · {cls}"
        matrix.append(row)
    st.dataframe(pd.DataFrame(matrix),use_container_width=True,hide_index=True)
    st.caption("Classification follows the project brief: 1–4 Low, 5–9 Medium, 10–16 High, 17–25 Critical.")

# -----------------------------------------------------------------------------
# Reports and interactive business questions
# -----------------------------------------------------------------------------
elif page == "Reports & Analytics":
    auth.require_permission(st, "Generate reports")
    ribbon("DATA & DECISIONS", "Reports & Interactive Analytics", "Use the monitoring records to answer mining engineering questions, compare groups and export a report for review.")
    question=st.selectbox("Choose a business question",[
        "Safety incidents by selected period", "Which department has the most incidents?", "Which shift records the most incidents?", "What is the PPE compliance percentage?", "How many near misses have been recorded?", "Which incident types are most frequent?", "How many high or critical incidents are recorded?", "Equipment with lowest availability", "Equipment temperature and vibration overview", "Maintenance status overview", "High and critical risk observations", "Full monitoring summary"])
    idf=as_df(data["incidents"]); wdf=as_df(data["workers"]); edf=as_df(data["equipment"]); rdf=as_df(data["risks"])
    if question == "Safety incidents by selected period":
        c1,c2=st.columns(2); start=c1.date_input("From",value=date.today()-timedelta(days=30)); end=c2.date_input("To",value=date.today())
        if start>end: st.error("The start date must be before or equal to the end date.")
        elif not idf.empty:
            dt=pd.to_datetime(idf["Date"],errors="coerce"); selected=idf[(dt.dt.date>=start)&(dt.dt.date<=end)]
            st.metric("Incidents in selected period",len(selected)); st.dataframe(selected,use_container_width=True,hide_index=True)
            if not selected.empty: st.bar_chart(selected["Date"].value_counts().sort_index())
        else: st.info("No incidents have been recorded yet.")
    elif question == "Which department has the most incidents?":
        if not idf.empty: st.bar_chart(idf["Department"].value_counts()); st.write("Highest count:", idf["Department"].value_counts().idxmax())
        else: st.info("No incidents recorded.")
    elif question == "Which shift records the most incidents?":
        if not idf.empty: st.bar_chart(idf["Shift"].value_counts()); st.write("Highest count:", idf["Shift"].value_counts().idxmax())
        else: st.info("No incidents recorded.")
    elif question == "What is the PPE compliance percentage?":
        if not wdf.empty:
            vals=pd.to_numeric(wdf["PPE Compliance"],errors="coerce"); st.metric("Average PPE compliance",f"{vals.mean():.1f}%"); st.metric("Workers meeting 90% example target",f"{(vals>=90).sum()} / {len(vals)}"); st.bar_chart(wdf.set_index("Worker ID")["PPE Compliance"])
        else: st.info("No worker safety records available.")
    elif question == "How many near misses have been recorded?":
        count=int(pd.to_numeric(wdf.get("Near Misses",pd.Series(dtype=float)),errors="coerce").fillna(0).sum()) if not wdf.empty else 0
        count += int((idf["Incident Type"]=="Near miss").sum()) if not idf.empty and "Incident Type" in idf else 0
        st.metric("Recorded near misses",count); st.caption("Count combines worker-record near-miss totals and incidents categorised as Near miss. Avoid double-counting when entering real data.")
    elif question == "Which incident types are most frequent?":
        if not idf.empty: st.bar_chart(idf["Incident Type"].value_counts())
        else: st.info("No incidents recorded.")
    elif question == "How many high or critical incidents are recorded?":
        count=int(idf["Severity"].isin(["High","Critical"]).sum()) if not idf.empty else 0
        st.metric("High / critical incidents",count)
        if not idf.empty: st.dataframe(idf[idf["Severity"].isin(["High","Critical"])],use_container_width=True,hide_index=True)
    elif question == "Equipment with lowest availability":
        if not edf.empty:
            av=pd.DataFrame([{"Equipment ID":e.get("Equipment ID"),"Equipment Type":e.get("Equipment Type"),"Availability (%)":round(equipment_availability(e),1),"Downtime":e.get("Downtime"),"Maintenance Status":e.get("Maintenance Status")} for e in data["equipment"]]).sort_values("Availability (%)")
            st.dataframe(av,use_container_width=True,hide_index=True); st.bar_chart(av.set_index("Equipment ID")["Availability (%)"])
        else: st.info("No equipment data available.")
    elif question == "Equipment temperature and vibration overview":
        if not edf.empty: st.dataframe(edf[[c for c in ["Equipment ID","Equipment Type","Temperature","Vibration","Engine Status"] if c in edf]],use_container_width=True,hide_index=True)
        else: st.info("No equipment data available.")
    elif question == "Maintenance status overview":
        if data["equipment"]:
            md=pd.DataFrame([{"Equipment ID":e.get("Equipment ID"),"Due status":maintenance_state(e),"Availability (%)":round(equipment_availability(e),1)} for e in data["equipment"]]); st.bar_chart(md["Due status"].value_counts()); st.dataframe(md,use_container_width=True,hide_index=True)
        else: st.info("No equipment data available.")
    elif question == "High and critical risk observations":
        if not rdf.empty: st.metric("High / critical risks",int(rdf["Classification"].isin(["High","Critical"]).sum())); st.dataframe(rdf[rdf["Classification"].isin(["High","Critical"])],use_container_width=True,hide_index=True)
        else: st.info("No risk observations available.")
    else:
        summary=pd.DataFrame([{"Metric":"Workers monitored","Value":len(data["workers"])},{"Metric":"Safety incidents","Value":len(data["incidents"])},{"Metric":"Near misses in worker records","Value":int(pd.to_numeric(wdf.get("Near Misses",pd.Series(dtype=float)),errors="coerce").fillna(0).sum()) if not wdf.empty else 0},{"Metric":"Equipment assets","Value":len(data["equipment"])},{"Metric":"Equipment under maintenance","Value":sum(e.get("Maintenance Status")=="Under maintenance" for e in data["equipment"])},{"Metric":"High / critical risks","Value":int(rdf["Classification"].isin(["High","Critical"]).sum()) if not rdf.empty else 0},{"Metric":"Critical alerts","Value":critical_count},{"Metric":"Warnings","Value":warning_count}])
        st.dataframe(summary,use_container_width=True,hide_index=True)
    st.markdown("### Export data")
    with st.expander("Download full report and source registers"):
        for key,label in [("workers","Worker safety"),("incidents","Safety incidents"),("equipment","Equipment"),("risks","Risk register")]:
            df=as_df(data[key])
            if not df.empty: st.download_button(f"Download {label} CSV",df.to_csv(index=False).encode("utf-8"),file_name=f"khwezi_{key}.csv",mime="text/csv",key=f"download_{key}")
        report={"generated_at":datetime.now().isoformat(timespec="seconds"),"role":role,"summary":{"workers":len(data["workers"]),"incidents":len(data["incidents"]),"equipment":len(data["equipment"]),"risks":len(data["risks"]),"critical_alerts":critical_count,"warnings":warning_count},"alerts":all_alerts,"data":data}
        st.download_button("Download complete monitoring report (JSON)",json.dumps(report,indent=2,ensure_ascii=False),file_name="khwezi_mining_full_report.json",mime="application/json",key="download_full_json")
    st.caption("Charts and counts are calculated from saved records. Demo data is illustrative, not operational mine data.")

elif page == "Manage Users":
    auth.require_permission(st, "Manage users")
    ribbon("ADMINISTRATION", "User & Access Management", "Manage accounts for the five project roles. Access permissions are enforced by the application's role-based access-control module.")
    auth.manage_users_page(st)

st.divider()
st.caption("Khwezi Mining Monitoring · MINN2020A educational prototype · Example thresholds and demo records only · Last rendered " + datetime.now().strftime("%d %b %Y, %H:%M"))
