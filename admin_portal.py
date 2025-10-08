import streamlit as st
import pandas as pd
from sqlalchemy import text
from io import BytesIO
from census_app.db import engine

# ------------------------------
# Admin credentials
# ------------------------------
ADMIN_USERS = {
    "admin": "admin123",
}

# ------------------------------
# Initialize session state
# ------------------------------
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ------------------------------
# Admin login
# ------------------------------
def admin_login():
    st.title("🔐 Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in ADMIN_USERS and password == ADMIN_USERS[username]:
            st.success("✅ Login successful!")
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

def admin_logout():
    if st.button("Logout"):
        st.session_state.admin_logged_in = False
        st.rerun()

# ------------------------------
# Admin dashboard
# ------------------------------
def admin_dashboard():
    st.title("📊 NACP Admin Dashboard")
    admin_logout()  # Logout button at top

    # --- Fetch data ---
    with engine.begin() as conn:
        df = pd.read_sql(text("SELECT * FROM registration_form"), conn)

    # --- Table view ---
    st.subheader("Table of Registrations")
    st.dataframe(df)

    # --- Charts ---
    st.subheader("Registrations by Island")
    if 'island' in df.columns:
        island_counts = df['island'].value_counts()
        st.bar_chart(island_counts)

    st.subheader("Preferred Communication Methods")
    if 'communication_methods' in df.columns:
        methods = ["WhatsApp", "Phone Call", "Email", "Text Message"]
        methods_count = {m: df['communication_methods'].apply(lambda x: m in x if x else False).sum() for m in methods}
        st.bar_chart(pd.Series(methods_count))

    st.subheader("Availability (Days Selected)")
    if 'available_days' in df.columns:
        days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        day_counts = {day: df['available_days'].apply(lambda x: day in x if x else False).sum() for day in days}
        st.bar_chart(pd.Series(day_counts))

    # --- Download options ---
    st.subheader("Export Data")

    # CSV
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv_data, "registration_data.csv", "text/csv")

    # Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    output.seek(0)
    st.download_button(
        "Download Excel",
        output,
        "registration_data.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ------------------------------
# Main app logic
# ------------------------------
if not st.session_state.admin_logged_in:
    admin_login()
else:
    admin_dashboard()
