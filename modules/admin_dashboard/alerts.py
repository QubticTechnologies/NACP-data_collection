# census_app/modules/admin_dashboard/alerts.py

import json
import os
from datetime import datetime
from sqlalchemy import text
from census_app.config import engine
import streamlit as st

# Paths for alert templates and history
BASE_DIR = os.path.dirname(__file__)
TEMPLATES_FILE = os.path.join(BASE_DIR, "alert_templates.json")
HISTORY_FILE = os.path.join(BASE_DIR, "alert_history.json")

# -------------------- Load Alert Templates --------------------
def load_alerts():
    """Load alert templates from JSON file."""
    try:
        with open(TEMPLATES_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# -------------------- Load Alert History --------------------
def load_history():
    """Load alert history from JSON file."""
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# -------------------- Save Alert History --------------------
def save_history(history):
    """Save alert history to JSON file."""
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

# -------------------- Check Alerts --------------------
def check_alerts(engine, send_notifications=False):
    """
    Evaluate alert conditions and return newly triggered alerts.
    Adds them to history and optionally displays notifications in Streamlit.
    """
    alerts = load_alerts()
    history = load_history()
    new_alerts = []

    for name, alert in alerts.items():
        condition_sql = alert.get("condition")
        message = alert.get("message", name)
        if not condition_sql:
            continue

        triggered_count = 0
        # Check both users and holders tables
        for table in ["users", "holders"]:
            query = f"SELECT COUNT(*) FROM {table} WHERE {condition_sql}"
            try:
                with engine.connect() as conn:
                    count = conn.execute(text(query)).scalar()
                triggered_count += count
            except Exception as e:
                st.warning(f"Failed to evaluate alert '{name}' on table '{table}': {e}")

        # Log if alert triggered
        if triggered_count > 0:
            today_str = datetime.now().strftime("%Y-%m-%d")
            already_logged = any(
                h.get("alert_name") == name and h.get("triggered_at", "").startswith(today_str)
                for h in history
            )
            if not already_logged:
                entry = {
                    "alert_name": name,
                    "triggered_at": datetime.now().isoformat(),
                    "details": f"{triggered_count} record(s) triggered"
                }
                history.append(entry)
                save_history(history)
                new_alerts.append(f"{message} ({triggered_count} triggered)")
                if send_notifications:
                    st.warning(f"🔥 {message} ({triggered_count} triggered)")

    return new_alerts
