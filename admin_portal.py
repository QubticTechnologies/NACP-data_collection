import streamlit as st
import pandas as pd
from sqlalchemy import text, create_engine
from sqlalchemy.exc import OperationalError
from io import BytesIO
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

# ------------------------------
# Load environment variables
# ------------------------------
load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD", "test1234$"))  # encode special chars
DB_HOST = os.getenv("DB_HOST", "aws-1-us-east-2.pooler.supabase.com")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "registration_form")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ------------------------------
# Create SQLAlchemy engine
# ------------------------------
try:
    engine = create_engine(DATABASE_URL, echo=False)
    # Test connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
except OperationalError as e:
    st.error(f"❌ Database connection failed: {e}")
    st.stop()

# ------------------------------
# Admin credentials
# ------------------------------
ADMIN_USERS = {
    "admin": "admin123",
}

# ------------------------------
# Session state
# ------------------------------
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ------------------------------
# Admin login/logout
# ------------------------------
def admin_login():
    st.title("🔐 Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in ADMIN_USERS and password == ADMIN_USERS[username]:
            st.session_state.admin_logged_in = True
            st.success("✅ Login successful!")
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
    admin_logout()  # logout button at top

    # --- Fetch data safely ---
    try:
        with engine.begin() as conn:
            df = pd.read_sql(text("SELECT * FROM registration_form"), conn)
        st.success(f"✅ Loaded {len(df)} records")
    except Exception as e:
        st.error(f"❌ Failed to fetch registration data: {e}")
        df = pd.DataFrame()

    if df.empty:
        st.info("No data available yet.")
        return

    # --- Table view ---
    st.subheader("Table of Registrations")
    st.dataframe(df)

    # --- Charts ---
    if "island" in df.columns:
        st.subheader("Registrations by Island")
        st.bar_chart(df["island"].value_counts())

    if "communication_methods" in df.columns:
        st.subheader("Preferred Communication Methods")
        methods = ["WhatsApp", "Phone Call", "Email", "Text Message"]
        methods_count = {m: df['communication_methods'].apply(lambda x: m in x if x else False).sum() for m in methods}
        st.bar_chart(pd.Series(methods_count))

    if "available_days" in df.columns:
        st.subheader("Availability (Days Selected)")
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
# Main logic
# ------------------------------
if not st.session_state.admin_logged_in:
    admin_login()
else:
    admin_dashboard()
