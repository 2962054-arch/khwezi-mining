import streamlit as st
import pandas as pd

from risk_assessment import assess_risk, risk_matrix
from alerts import (
    check_temperature,
    check_vibration,
    check_downtime,
    check_maintenance,
    check_ppe,
    check_fatigue,
    check_incident,
    check_risk_observation,
    count_by_level,
    format_alert,
)


st.set_page_config(
    page_title="Kwezi Mining Monitoring",
    page_icon="⛏️",
    layout="wide"
)

st.title("⛏️ Kwezi Mining Monitoring System")
st.write("Risk Assessment and Safety Alerts")


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Choose a section:",
    [
        "Risk Assessment",
        "Alerts & Notifications"
    ]
)


# ============================================================
# RISK ASSESSMENT
# ============================================================

if page == "Risk Assessment":

    st.header("Section G — Risk Assessment")

    st.write(
        "Risk Score = Likelihood × Consequence"
    )

    col1, col2 = st.columns(2)

    with col1:
        likelihood = st.selectbox(
            "Likelihood",
            [1, 2, 3, 4, 5]
        )

    with col2:
        consequence = st.selectbox(
            "Consequence",
            [1, 2, 3, 4, 5]
        )

    if st.button("Calculate Risk"):

        result = assess_risk(
            likelihood,
            consequence
        )

        st.subheader("Risk Result")

        st.metric(
            "Risk Score",
            result["risk_score"]
        )

        st.write(
            f"**Likelihood:** {result['likelihood_label']}"
        )

        st.write(
            f"**Consequence:** {result['consequence_label']}"
        )

        st.write(
            f"**Risk Classification:** {result['classification']}"
        )

        if result["warning"]:
            st.warning(result["warning"])
        else:
            st.success("Risk level is Low or Medium.")


    st.divider()

    st.subheader("5 × 5 Risk Matrix")

    matrix = risk_matrix()

    matrix_data = []

    for row in matrix:
        matrix_data.append(
            [
                f"{score} ({classification})"
                for likelihood, consequence, score, classification
                in row
            ]
        )

    df_matrix = pd.DataFrame(
        matrix_data,
        index=[
            "Likelihood 1",
            "Likelihood 2",
            "Likelihood 3",
            "Likelihood 4",
            "Likelihood 5"
        ],
        columns=[
            "Consequence 1",
            "Consequence 2",
            "Consequence 3",
            "Consequence 4",
            "Consequence 5"
        ]
    )

    st.dataframe(
        df_matrix,
        use_container_width=True
    )


# ============================================================
# ALERTS
# ============================================================

elif page == "Alerts & Notifications":

    st.header("Section H — Alerts & Notifications")

    st.write(
        "Enter monitoring information to generate mining safety alerts."
    )

    alert_type = st.selectbox(
        "Select alert check",
        [
            "Equipment Temperature",
            "Equipment Vibration",
            "Equipment Downtime",
            "PPE Compliance",
            "Worker Fatigue",
            "Safety Incident",
            "Risk Observation"
        ]
    )


    # --------------------------------------------------------
    # TEMPERATURE
    # --------------------------------------------------------

    if alert_type == "Equipment Temperature":

        equipment_id = st.text_input(
            "Equipment ID",
            "TRK-012"
        )

        temperature = st.number_input(
            "Temperature (°C)",
            min_value=0.0,
            value=105.0
        )

        if st.button("Check Temperature"):

            alert = check_temperature(
                equipment_id,
                temperature
            )

            if alert:
                if alert["level"] == "CRITICAL":
                    st.error(format_alert(alert))
                else:
                    st.warning(format_alert(alert))
            else:
                st.success("Temperature is within the normal range.")


    # --------------------------------------------------------
    # VIBRATION
    # --------------------------------------------------------

    elif alert_type == "Equipment Vibration":

        equipment_id = st.text_input(
            "Equipment ID",
            "TRK-012"
        )

        vibration = st.number_input(
            "Vibration (mm/s)",
            min_value=0.0,
            value=9.2
        )

        if st.button("Check Vibration"):

            alert = check_vibration(
                equipment_id,
                vibration
            )

            if alert:
                if alert["level"] == "CRITICAL":
                    st.error(format_alert(alert))
                else:
                    st.warning(format_alert(alert))
            else:
                st.success("Vibration is within the normal range.")


    # --------------------------------------------------------
    # DOWNTIME
    # --------------------------------------------------------

    elif alert_type == "Equipment Downtime":

        equipment_id = st.text_input(
            "Equipment ID",
            "TRK-012"
        )

        operating_time = st.number_input(
            "Operating Time",
            min_value=0.0,
            value=80.0
        )

        downtime = st.number_input(
            "Downtime",
            min_value=0.0,
            value=30.0
        )

        if st.button("Check Downtime"):

            alert = check_downtime(
                equipment_id,
                operating_time,
                downtime
            )

            if alert:
                if alert["level"] == "CRITICAL":
                    st.error(format_alert(alert))
                else:
                    st.warning(format_alert(alert))
            else:
                st.success("Downtime is within the normal range.")


    # --------------------------------------------------------
    # PPE
    # --------------------------------------------------------

    elif alert_type == "PPE Compliance":

        worker_id = st.text_input(
            "Worker ID",
            "WRK-001"
        )

        ppe = st.number_input(
            "PPE Compliance (%)",
            min_value=0.0,
            max_value=100.0,
            value=70.0
        )

        if st.button("Check PPE"):

            alert = check_ppe(
                worker_id,
                ppe
            )

            if alert:
                if alert["level"] == "CRITICAL":
                    st.error(format_alert(alert))
                else:
                    st.warning(format_alert(alert))
            else:
                st.success("PPE compliance is acceptable.")


    # --------------------------------------------------------
    # FATIGUE
    # --------------------------------------------------------

    elif alert_type == "Worker Fatigue":

        worker_id = st.text_input(
            "Worker ID",
            "WRK-001"
        )

        fatigue = st.number_input(
            "Fatigue Level (1-10)",
            min_value=1.0,
            max_value=10.0,
            value=8.0
        )

        if st.button("Check Fatigue"):

            alert = check_fatigue(
                worker_id,
                fatigue
            )

            if alert:
                if alert["level"] == "CRITICAL":
                    st.error(format_alert(alert))
                else:
                    st.warning(format_alert(alert))
            else:
                st.success("Fatigue level is within the normal range.")


    # --------------------------------------------------------
    # INCIDENT
    # --------------------------------------------------------

    elif alert_type == "Safety Incident":

        incident_id = st.text_input(
            "Incident ID",
            "INC-001"
        )

        severity = st.selectbox(
            "Severity",
            ["Low", "Medium", "High", "Critical"]
        )

        if st.button("Check Incident"):

            alert = check_incident(
                incident_id,
                severity
            )

            if alert:
                if alert["level"] == "CRITICAL":
                    st.error(format_alert(alert))
                else:
                    st.warning(format_alert(alert))
            else:
                st.success("No high or critical incident alert generated.")


    # --------------------------------------------------------
    # RISK OBSERVATION
    # --------------------------------------------------------

    elif alert_type == "Risk Observation":

        observation_id = st.text_input(
            "Observation ID",
            "OBS-001"
        )

        risk_class = st.selectbox(
            "Risk Classification",
            ["Low", "Medium", "High", "Critical"]
        )

        if st.button("Check Risk Observation"):

            alert = check_risk_observation(
                observation_id,
                risk_class
            )

            if alert:
                if alert["level"] == "CRITICAL":
                    st.error(format_alert(alert))
                else:
                    st.warning(format_alert(alert))
            else:
                st.success(
                    "No high or critical risk observation alert generated."
                )