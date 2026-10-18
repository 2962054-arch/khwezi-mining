# KHWEZI MINING

A Python and Streamlit mining health, safety, equipment and risk-monitoring application developed as an educational project for MINN2020A.

## How to run the application

### 1. Install Python
Install Python 3.11 or later from https://www.python.org/downloads/.

### 2. Install the required packages
Open a terminal in this project folder and run:

```bash
python -m pip install -r requirements.txt
```

### 3. Launch the application
Run:

```bash
python -m streamlit run app.py
```

Open the local address printed in the terminal, usually http://localhost:8501.

## Demo login

The project includes a local demo user database in `data/users.json`. The authentication module defines these demo accounts:

| Username | Demo password | Role |
|---|---|---|
| `admin` | `Admin@123` | Administrator |
| `safety` | `Safety@123` | Safety Officer |
| `engineer` | `Engineer@123` | Mining Engineer |
| `maintenance` | `Maint@1234` | Maintenance Engineer |
| `manager` | `Manager@123` | Manager |

These are demonstration credentials only. Change them before using the application for anything beyond a classroom demonstration. Do not use real passwords.

## Main project files

- `app.py` — Streamlit application and interface.
- `auth.py` — login and role-based permissions.
- `alerts.py` — alert checks and alert summaries.
- `risk_assessment.py` — risk assessment calculations.
- `worker_safety.py` — worker-safety functions.
- `incident_equipment_db.py.py` — incident and equipment functions used by the project exercises.
- `data/` — local user and application data.
- `test_sections_ab.py` and `test_sections_g_h.py` — test/section files.
- `Maintenance.ipynb` and `equipment_condition.ipynb` — supporting notebooks.

## Notes

- The application is an educational prototype. Example thresholds and demonstration records are not official mine or manufacturer safety limits.
- The app stores its monitoring records locally. For a fresh setup, the application may create its monitoring data file when first run.
- Keep the folder structure intact so Python modules and data files can be found.
