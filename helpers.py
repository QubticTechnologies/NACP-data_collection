# census_app/helpers.py

import os
import yagmail
from datetime import datetime, timedelta, date
import streamlit as st
import pandas as pd
from sqlalchemy import text
from db import engine
from passlib.hash import bcrypt

# --- Email credentials (from config or env vars) ---
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# --- Password helpers ---
def hash_password(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.verify(password, hashed)

def safe_verify_password(password: str, hashed: str) -> bool:
    """Wrapper to safely verify passwords; returns False on exception."""
    try:
        return bcrypt.verify(password, hashed)
    except Exception:
        return False

# --- Formatting helpers ---
def format_name(name: str) -> str:
    """Capitalize each word in a name."""
    return " ".join(part.capitalize() for part in name.strip().split())

def format_date(d: date | datetime | str | None) -> str | None:
    """
    Convert datetime.date, datetime.datetime, or YYYY-MM-DD string into YYYY-MM-DD string.
    Returns None if d is None.
    """
    if d is None:
        return None

    if isinstance(d, str):
        try:
            d = datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid date string: {d}. Expected YYYY-MM-DD")
    elif isinstance(d, datetime):
        d = d.date()
    elif not isinstance(d, date):
        raise TypeError(f"Expected date, datetime, or YYYY-MM-DD string, got {type(d)}")

    return d.strftime("%Y-%m-%d")

def calculate_age(dob: date | datetime | str | None) -> int | None:
    """
    Calculate age in years from date of birth.
    Accepts datetime.date, datetime.datetime, or YYYY-MM-DD string.
    Returns None if dob is None.
    """
    if dob is None:
        return None

    if isinstance(dob, str):
        try:
            dob = datetime.strptime(dob, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid date string: {dob}. Expected YYYY-MM-DD")
    elif isinstance(dob, datetime):
        dob = dob.date()
    elif not isinstance(dob, date):
        raise TypeError(f"dob must be datetime.date, datetime.datetime, or ISO string, got {type(dob)}")

    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

# --- Email helpers ---
def send_email(to_email: str, subject: str, contents: str) -> bool:
    """Send an email; returns True if successful."""
    if not to_email or not EMAIL_USER or not EMAIL_PASS:
        print("Email not sent: missing recipient or credentials.")
        return False
    try:
        yag = yagmail.SMTP(EMAIL_USER, EMAIL_PASS)
        yag.send(to=to_email, subject=subject, contents=contents)
        print(f"✅ Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return False

def send_agent_reminders():
    """Send reminder emails to agents for pending holders submitted within the last 24 hours."""
    now = datetime.now()
    cutoff = now - timedelta(hours=24)

    with engine.connect() as conn:
        pending_holders = conn.execute(text("""
            SELECT h.id, h.name AS holder_name, h.submitted_at, u.email AS agent_email
            FROM holders h
            JOIN users u ON u.role='Agent' AND u.status='active'
            WHERE h.status='pending'
              AND h.submitted_at >= :cutoff
        """), {"cutoff": cutoff}).mappings().all()

    if not pending_holders:
        print("No pending holders found for reminders.")
        return

    for h in pending_holders:
        agent_email = h.get('agent_email')
        if not agent_email:
            print(f"Holder {h['holder_name']} has no assigned agent email. Skipping.")
            continue

        subject = f"Reminder: Review Holder {h['holder_name']}"
        body = f"""
Dear Agent,

The holder registration for {h['holder_name']} is pending review.
Please review it before the 24-hour window expires.

Submitted at: {h['submitted_at']}

Thank you.
"""
        if send_email(agent_email, subject, body):
            print(f"Reminder sent to {agent_email} for holder {h['holder_name']}")
        else:
            print(f"Failed to send reminder to {agent_email}")

# --- Dashboard badges ---
def status_badge(status: str):
    """Display a colored status badge in Streamlit."""
    colors = {
        "pending": "orange",
        "approved": "blue",
        "rejected": "red",
        "changes_requested": "purple",
        "active": "green"
    }
    color = colors.get(status.lower(), "gray")
    st.markdown(f"<span style='color:{color}; font-weight:bold'>{status}</span>", unsafe_allow_html=True)

def time_left_badge(submitted_at: datetime):
    """Show time-left badge for Streamlit based on a 24-hour deadline."""
    if not submitted_at:
        return
    deadline = submitted_at + timedelta(hours=24)
    now = datetime.now()
    remaining = deadline - now
    hours_left = remaining.total_seconds() / 3600

    color = "green" if hours_left > 12 else "orange" if hours_left > 6 else "red"
    badge_text = f"{int(max(hours_left, 0))}h left"
    st.markdown(f"<span style='color:{color}; font-weight:bold'>{badge_text}</span>", unsafe_allow_html=True)

# --- Admin summary helpers ---
def get_pending_holders_summary() -> pd.DataFrame:
    """Return a DataFrame of pending holders with urgency and hours left."""
    now = datetime.now()
    with engine.connect() as conn:
        pending = conn.execute(text("""
            SELECT h.id, h.name AS holder_name, h.submitted_at, h.status,
                   u.username AS agent_username
            FROM holders h
            LEFT JOIN users u ON u.role='Agent' AND u.status='active'
            WHERE h.status='pending'
        """)).mappings().all()

    summary_data = []
    for h in pending:
        time_left = (h['submitted_at'] + timedelta(hours=24)) - now
        hours_left = time_left.total_seconds() / 3600
        if hours_left < 0:
            urgency = "Overdue"
        elif hours_left <= 6:
            urgency = "High"
        elif hours_left <= 12:
            urgency = "Medium"
        else:
            urgency = "Low"

        summary_data.append({
            "Holder Name": h['holder_name'],
            "Agent": h.get('agent_username') or "Unassigned",
            "Submitted At": h['submitted_at'],
            "Hours Left": round(max(hours_left, 0), 1),
            "Urgency": urgency
        })

    return pd.DataFrame(summary_data)

# --- Export helpers ---
def export_pending_holders_csv(df: pd.DataFrame, filename: str = "pending_holders.csv") -> str:
    df.to_csv(filename, index=False)
    return filename

def export_pending_holders_pdf(df: pd.DataFrame, filename: str = "pending_holders.pdf") -> str:
    from fpdf import FPDF

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    col_width = pdf.w / len(df.columns)
    row_height = pdf.font_size * 1.5

    # Header
    for col_name in df.columns:
        pdf.cell(col_width, row_height, str(col_name), border=1)
    pdf.ln(row_height)

    # Rows
    for i in range(len(df)):
        for col in df.columns:
            pdf.cell(col_width, row_height, str(df.iloc[i][col]), border=1)
        pdf.ln(row_height)

    pdf.output(filename)
    return filename
