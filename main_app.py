import streamlit as st
import pandas as pd
from sqlalchemy import text
from io import BytesIO

# Import engine from db.py
from db import engine

# -------------------------------
# Page State
# -------------------------------
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# -------------------------------
# Admin credentials
# -------------------------------
ADMIN_USERS = {
    "admin": "admin123",
}

# -------------------------------
# Reset Session Helper
# -------------------------------
def reset_session():
    keys_to_reset = [
        "latitude", "longitude", "first_name", "last_name", "email",
        "telephone", "cell", "selected_methods",
        "island_selected", "settlement_selected", "street_address",
        "selected_days", "selected_times", "consent_bool"
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    st.success("Session reset!")
    st.rerun()

# -------------------------------
# Landing Page
# -------------------------------
def landing_page():
    st.set_page_config(page_title="NACP Bahamas", layout="wide")
    st.title("🇧🇸 NACP - National Agricultural Census Pilot Project")
    st.markdown("""
    Welcome to the National Agricultural Census Pilot Project (NACP).  
    Please provide your location information to begin the registration process or login as admin.
    """)

    # Map input
    if "latitude" not in st.session_state:
        st.session_state.latitude = None
    if "longitude" not in st.session_state:
        st.session_state.longitude = None

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.latitude = st.number_input("Enter your Latitude", value=25.0343, format="%.6f")
        st.session_state.longitude = st.number_input("Enter your Longitude", value=-77.3963, format="%.6f")
        if st.button("Show on Map"):
            st.success(f"Location set: Latitude {st.session_state.latitude}, Longitude {st.session_state.longitude}")

    with col2:
        if st.session_state.latitude and st.session_state.longitude:
            df = pd.DataFrame([{"lat": st.session_state.latitude, "lon": st.session_state.longitude}])
            st.map(df, zoom=6)

    st.markdown("---")
    col_reg, col_admin, col_reset = st.columns([1,1,1])
    with col_reg:
        if st.button("➡️ Start Registration"):
            st.session_state.page = "registration"
    with col_admin:
        if st.button("🔐 Admin Portal"):
            st.session_state.page = "admin_login"
    with col_reset:
        if st.button("♻️ Reset Session"):
            reset_session()

# -------------------------------
# Admin Login
# -------------------------------
def admin_login():
    st.title("🔐 Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in ADMIN_USERS and password == ADMIN_USERS[username]:
            st.success("✅ Login successful!")
            st.session_state.admin_logged_in = True
            st.session_state.page = "admin_dashboard"
        else:
            st.error("❌ Invalid username or password")

def admin_logout():
    if st.button("Logout"):
        st.session_state.admin_logged_in = False
        st.session_state.page = "landing"
        st.rerun()

# -------------------------------
# Admin Dashboard
# -------------------------------
def admin_dashboard():
    st.title("📊 NACP Admin Dashboard")
    admin_logout()  # Logout button at top

    # Fetch data
    with engine.begin() as conn:
        df = pd.read_sql(text("SELECT * FROM registration_form ORDER BY id DESC"), conn)

    # Refresh button
    if st.button("🔄 Refresh Data"):
        st.rerun()

    # Table
    st.subheader("Table of Registrations")
    st.dataframe(df)

    # Charts
    if 'island' in df.columns:
        st.subheader("Registrations by Island")
        st.bar_chart(df['island'].value_counts())

    if 'communication_methods' in df.columns:
        st.subheader("Preferred Communication Methods")
        methods = ["WhatsApp", "Phone Call", "Email", "Text Message"]
        counts = {m: df['communication_methods'].apply(lambda x: m in x if x else False).sum() for m in methods}
        st.bar_chart(pd.Series(counts))

    # Export
    st.subheader("Export Data")
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv_data, "registration_data.csv", "text/csv")

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

# -------------------------------
# Registration Form
# -------------------------------
def registration_form():
    st.subheader("🌱 Registration Form")
    st.write("I understand my information will be kept strictly confidential and used only for statistical purposes.")

    consent_options = ["I do not wish to participate", "I do wish to participate"]
    consent = st.radio("Consent", consent_options)

    if consent == "I do not wish to participate":
        st.warning("You cannot proceed without consenting.")
        return

    consent_bool = True if consent == "I do wish to participate" else False

    # Contact info
    first_name = st.text_input("First Name", key="first_name")
    last_name = st.text_input("Last Name", key="last_name")
    email = st.text_input("Email", key="email")
    telephone = st.text_input("Telephone Number", key="telephone")
    cell = st.text_input("Cell Number", key="cell")

    # Full address
    st.subheader("Address")
    ISLANDS = ["New Providence", "Grand Bahama", "Abaco", "Acklins", "Andros", "Berry Islands",
               "Bimini", "Cat Island", "Crooked Island", "Eleuthera", "Exuma",
               "Inagua", "Long Island", "Mayaguana", "Ragged Island", "Rum Cay", "San Salvador"]
    island_selected = st.selectbox("Island", ISLANDS, key="island_selected")

    SETTLEMENTS = {
        "New Providence": ["Nassau", "Gros Islet", "Other"],
        "Grand Bahama": ["Freeport", "West End", "Other"],
        "Abaco": ["Marsh Harbour", "Hope Town", "Other"],
        # Add other islands as needed
    }
    settlement_selected = st.selectbox("Settlement/District", SETTLEMENTS.get(island_selected, ["Other"]), key="settlement_selected")

    street_address = st.text_input("Street Address", key="street_address")

    # Communication methods
    st.write("Preferred Communication (Select all that apply)")
    methods = ["WhatsApp", "Phone Call", "Email", "Text Message"]
    selected_methods = []
    cols = st.columns(2)
    for i, method in enumerate(methods):
        with cols[i % 2]:
            if st.checkbox(method, key=f"method_{method}"):
                selected_methods.append(method)

    if st.button("💾 Save & Continue"):
        if not all([first_name, last_name, email, selected_methods, island_selected, settlement_selected, street_address]):
            st.warning("Please fill all required fields and select at least one communication method.")
            return

        # Save to DB
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO registration_form (
                    consent, first_name, last_name, email, telephone, cell,
                    communication_methods, island, settlement, street_address, latitude, longitude
                ) VALUES (
                    :consent, :first_name, :last_name, :email, :telephone, :cell,
                    :communication_methods, :island, :settlement, :street_address, :latitude, :longitude
                )
            """), {
                "consent": consent_bool,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "telephone": telephone,
                "cell": cell,
                "communication_methods": selected_methods,
                "island": island_selected,
                "settlement": settlement_selected,
                "street_address": street_address,
                "latitude": st.session_state.latitude,
                "longitude": st.session_state.longitude
            })

        st.success("✅ Registration info saved!")
        st.session_state.page = "availability"
        st.rerun()

# -------------------------------
# Availability Form
# -------------------------------
def availability_form():
    st.subheader("🕒 Best Time to Visit You")

    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    selected_days = []
    cols = st.columns(4)
    for i, day in enumerate(days):
        with cols[i % 4]:
            if st.checkbox(day, key=f"day_{day}"):
                selected_days.append(day)

    time_slots = ["Morning (7-10am)", "Midday (11-1pm)", "Afternoon (2-5pm)", "Evening (6-8pm)"]
    selected_times = []
    cols2 = st.columns(2)
    for i, slot in enumerate(time_slots):
        with cols2[i % 2]:
            if st.checkbox(slot, key=f"time_{slot}"):
                selected_times.append(slot)

    if st.button("💾 Save Availability"):
        if not selected_days or not selected_times:
            st.warning("Please select at least one day and one time slot.")
            return
        with engine.begin() as conn:
            conn.execute(text("""
                UPDATE registration_form
                SET available_days=:days, available_times=:times
                WHERE id=(SELECT max(id) FROM registration_form)
            """), {
                "days": selected_days,
                "times": selected_times
            })

        st.success("✅ Availability saved!")
        st.session_state.page = "confirmation"
        st.rerun()

# -------------------------------
# Confirmation Page
# -------------------------------
def confirmation_page():
    st.subheader("✅ Registration Confirmation")
    with engine.begin() as conn:
        reg = conn.execute(text("""
            SELECT * FROM registration_form WHERE id=(SELECT max(id) FROM registration_form)
        """)).mappings().fetchone()
        if reg:
            st.json(dict(reg))
        else:
            st.warning("No registration data found.")

# -------------------------------
# Page Routing
# -------------------------------
if st.session_state.page == "landing":
    landing_page()
elif st.session_state.page == "registration":
    registration_form()
elif st.session_state.page == "availability":
    availability_form()
elif st.session_state.page == "confirmation":
    confirmation_page()
elif st.session_state.page == "admin_login":
    admin_login()
elif st.session_state.page == "admin_dashboard":
    if st.session_state.admin_logged_in:
        admin_dashboard()
    else:
        st.warning("Please login as admin first.")
        st.session_state.page = "admin_login"
