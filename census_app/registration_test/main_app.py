# main_app.py

import streamlit as st
import pandas as pd
from sqlalchemy import text
from db import connect_with_retries, engine
from geopy.geocoders import Nominatim
import requests
import re
import pydeck as pdk

# -------------------------------
# Streamlit page config
# -------------------------------
st.set_page_config(page_title="NACP Bahamas", layout="wide")

# -------------------------------
# DB connection
# -------------------------------
engine = connect_with_retries(retries=5, delay=3)
if engine is None:
    st.error("❌ Unable to connect to the database. Please try again later.")
else:
    st.success("✅ Connected to the database!")

# -------------------------------
# Page state
# -------------------------------
for key, default in {
    "page": "landing",
    "admin_logged_in": False,
    "latitude": None,
    "longitude": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# -------------------------------
# Admin credentials
# -------------------------------
ADMIN_USERS = {"admin": "admin123"}

# -------------------------------
# Reset session
# -------------------------------
def reset_session():
    keys_to_reset = [
        "latitude", "longitude", "auto_lat", "auto_lon",
        "auto_island", "auto_settlement", "auto_street",
        "first_name", "last_name", "email", "telephone", "cell",
        "selected_methods", "island_selected", "settlement_selected",
        "street_address", "selected_days", "selected_times",
        "consent_bool"
    ]
    for key in keys_to_reset:
        st.session_state.pop(key, None)
    st.success("Session reset!")
    st.rerun()

# -------------------------------
# Auto-detect location
# -------------------------------
def get_location():
    try:
        resp = requests.get("https://ipinfo.io/json", timeout=5)
        data = resp.json()
        loc = data.get("loc")  # "lat,lon"
        if loc:
            lat, lon = map(float, loc.split(","))
            st.session_state["auto_lat"] = lat
            st.session_state["auto_lon"] = lon

            geolocator = Nominatim(user_agent="nacp_app")
            location = geolocator.reverse((lat, lon), exactly_one=True, addressdetails=True)
            if location and "address" in location.raw:
                addr = location.raw["address"]
                st.session_state["auto_island"] = addr.get("state") or addr.get("region")
                st.session_state["auto_settlement"] = addr.get("city") or addr.get("town") or addr.get("village")
                st.session_state["auto_street"] = addr.get("road") or addr.get("pedestrian") or ""
            st.success(f"📍 Location detected: {lat}, {lon}")
            return True
    except Exception:
        pass
    st.warning("⚠️ Unable to auto-detect location. Please select manually or use dropdown.")
    return False

# -------------------------------
# Interactive map
# -------------------------------
def show_map(lat=None, lon=None):
    lat = lat or 25.0343
    lon = lon or -77.3963
    st.session_state.latitude = st.session_state.get("latitude") or lat
    st.session_state.longitude = st.session_state.get("longitude") or lon

    view_state = pdk.ViewState(
        latitude=st.session_state.latitude,
        longitude=st.session_state.longitude,
        zoom=10,
        pitch=0
    )

    marker = pdk.Layer(
        "ScatterplotLayer",
        data=pd.DataFrame([{"lat": st.session_state.latitude, "lon": st.session_state.longitude}]),
        get_position=["lon", "lat"],
        get_color=[255, 0, 0],
        get_radius=300,
    )

    r = pdk.Deck(layers=[marker], initial_view_state=view_state, tooltip={"text": "Click to set location"})
    st.pydeck_chart(r)

    st.markdown("**Adjust location manually by changing latitude/longitude below:**")
    col_lat, col_lon = st.columns(2)
    with col_lat:
        st.number_input("Latitude", value=st.session_state.latitude, format="%.6f", key="latitude")
    with col_lon:
        st.number_input("Longitude", value=st.session_state.longitude, format="%.6f", key="longitude")

# -------------------------------
# Landing page
# -------------------------------
def landing_page():
    st.title("🌾 NACP - National Agricultural Census Pilot Project")
    st.markdown(
        "Welcome to the National Agricultural Census Pilot Project (NACP).  \n"
        "Please provide your location information to begin registration or log in as admin."
    )

    if st.button("📍 Auto-detect my location"):
        get_location()

    show_map(
        lat=st.session_state.get("auto_lat") or st.session_state.get("latitude"),
        lon=st.session_state.get("auto_lon") or st.session_state.get("longitude")
    )

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➡️ Start Registration"):
            st.session_state.page = "registration"
            st.rerun()
    with col2:
        if st.button("🔐 Admin Portal"):
            st.session_state.page = "admin_login"
            st.rerun()
    with col3:
        if st.button("♻️ Reset Session"):
            reset_session()

# -------------------------------
# Admin login
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
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

# -------------------------------
# Admin dashboard with pagination & tick selection
# -------------------------------
# -------------------------------
# Admin dashboard with tick box in table
# -------------------------------
def admin_dashboard():
    st.title("📊 NACP Admin Dashboard")
    if st.button("Logout"):
        st.session_state.admin_logged_in = False
        st.session_state.page = "landing"
        st.rerun()

    TABLES = ["registration_form"]
    rows_per_page = 20

    for table_name in TABLES:
        st.markdown("---")
        st.subheader(f"📄 {table_name.capitalize()} Data")

        with engine.begin() as conn:
            df = pd.read_sql(text(f"SELECT * FROM {table_name} ORDER BY id DESC"), conn)

        if df.empty:
            st.info("No data found.")
            continue

        # Pagination
        if f"{table_name}_page" not in st.session_state:
            st.session_state[f"{table_name}_page"] = 0
        page = st.session_state[f"{table_name}_page"]
        total_pages = (len(df) - 1) // rows_per_page + 1

        start_idx = page * rows_per_page
        end_idx = start_idx + rows_per_page
        df_page = df.iloc[start_idx:end_idx].copy()

        # Add tick column for deletion
        if "Delete" not in df_page.columns:
            df_page["Delete"] = False

        # Data editor with checkbox column
        edited_df = st.data_editor(
            df_page,
            column_config={
                "Delete": st.column_config.CheckboxColumn("Delete", help="Tick to delete row"),
                "id": st.column_config.NumberColumn("ID", disabled=True)
            },
            use_container_width=True,
            key=f"editor_{table_name}"
        )

        # Delete confirmation
        if edited_df["Delete"].any():
            st.warning(f"⚠️ You have selected {edited_df['Delete'].sum()} row(s) to delete.")
            confirm_delete = st.radio(
                "Are you sure you want to delete the selected row(s)?",
                ["No", "Yes"],
                horizontal=True,
                key=f"confirm_delete_{table_name}"
            )
            if confirm_delete == "Yes" and st.button(f"✅ Delete Selected from {table_name}"):
                rows_to_delete = edited_df[edited_df["Delete"]]
                with engine.begin() as conn:
                    for rid in rows_to_delete["id"]:
                        conn.execute(text(f"DELETE FROM {table_name} WHERE id=:id"), {"id": rid})
                st.success(f"✅ Deleted {len(rows_to_delete)} record(s).")
                st.rerun()

        # Pagination buttons
        col_prev, col_next = st.columns([1, 1])
        with col_prev:
            if st.button("⬅️ Previous Page") and page > 0:
                st.session_state[f"{table_name}_page"] -= 1
                st.rerun()
        with col_next:
            if st.button("Next Page ➡️") and page < total_pages - 1:
                st.session_state[f"{table_name}_page"] += 1
                st.rerun()

        # Registrations by island
        if "island" in df.columns:
            st.subheader("📍 Registrations by Island")
            st.bar_chart(df["island"].value_counts())


# -------------------------------
# Registration form
# -------------------------------
def registration_form():
    st.subheader("🌱 Registration Form")
    st.markdown("### 📝 Consent")
    consent = st.radio(
        "Please indicate your consent:",
        ["I do not wish to participate", "I do wish to participate"]
    )
    st.session_state["consent_bool"] = consent == "I do wish to participate"
    if not st.session_state["consent_bool"]:
        st.warning("⚠️ You must give consent before proceeding.")
        return

    st.markdown("### 👤 Personal Information")
    first_name = st.text_input("First Name *")
    last_name = st.text_input("Last Name *")
    email = st.text_input("Email *")
    telephone = st.text_input("Telephone Number *")
    cell = st.text_input("Cell Number")

    if email and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,4}$", email):
        st.warning("⚠️ Invalid email format.")
    if telephone and not re.match(r"^\(\d{3}\) \d{3}-\d{4}$", telephone):
        st.warning("⚠️ Phone number must be in format (242) 456-4567")

    st.markdown("### 📍 Address Information")
    ISLANDS = [
        "New Providence", "Grand Bahama", "Abaco", "Acklins", "Andros",
        "Berry Islands", "Bimini", "Cat Island", "Crooked Island",
        "Eleuthera", "Exuma", "Inagua", "Long Island", "Mayaguana",
        "Ragged Island", "Rum Cay", "San Salvador"
    ]
    island_default = st.session_state.get("auto_island", ISLANDS[0])
    island_selected = st.selectbox("Island *", ISLANDS,
                                   index=ISLANDS.index(island_default) if island_default in ISLANDS else 0)
    settlement_default = st.session_state.get("auto_settlement", "Other")
    settlement_selected = st.text_input("Settlement/District *", value=settlement_default)
    street_default = st.session_state.get("auto_street", "")
    street_address = st.text_input("Street Address *", value=street_default)

    st.markdown("### 💬 Preferred Communication")
    comm_methods = ["WhatsApp", "Phone Call", "Email", "Text Message"]
    selected_methods = [m for m in comm_methods if st.checkbox(m, value=False, key=f"m_{m}")]

    st.markdown("### 🗣️ Interview Method")
    interview_methods = ["In-person Interview", "Phone Interview", "Self Reporting"]
    interview_selected = [m for m in interview_methods if st.checkbox(m, value=False, key=f"i_{m}")]

    if st.button("💾 Save & Continue"):
        if not all([first_name, last_name, telephone, email, island_selected, settlement_selected, street_address]):
            st.warning("⚠️ Please complete all required fields.")
            return
        if not selected_methods:
            st.warning("⚠️ Please select at least one communication method.")
            return
        if not interview_selected:
            st.warning("⚠️ Please select at least one interview method.")
            return

        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO registration_form (
                    consent, first_name, last_name, email, telephone, cell,
                    communication_methods, island, settlement, street_address,
                    interview_methods, latitude, longitude
                ) VALUES (
                    :consent, :first_name, :last_name, :email, :telephone, :cell,
                    :communication_methods, :island, :settlement, :street_address,
                    :interview_methods, :latitude, :longitude
                )
            """), {
                "consent": st.session_state["consent_bool"],
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "telephone": telephone,
                "cell": cell,
                "communication_methods": selected_methods,
                "island": island_selected,
                "settlement": settlement_selected,
                "street_address": street_address,
                "interview_methods": interview_selected,
                "latitude": st.session_state.get("latitude") or st.session_state.get("auto_lat"),
                "longitude": st.session_state.get("longitude") or st.session_state.get("auto_lon")
            })
        st.success("✅ Registration saved successfully!")
        st.session_state.page = "availability"
        st.rerun()

# -------------------------------
# Availability form
# -------------------------------
def availability_form():
    st.subheader("🕒 Availability")
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    selected_days = [d for d in days if st.checkbox(d, key=f"d_{d}")]
    time_slots = ["Morning (7-10am)", "Midday (11-1pm)", "Afternoon (2-5pm)", "Evening (6-8pm)"]
    selected_times = [t for t in time_slots if st.checkbox(t, key=f"t_{t}")]

    if st.button("💾 Save Availability"):
        if not selected_days or not selected_times:
            st.warning("Please select at least one day and one time slot.")
            return
        selected_days_sorted = [d for d in days if d in selected_days]

        with engine.begin() as conn:
            conn.execute(text("""
                UPDATE registration_form
                SET available_days=:days, available_times=:times
                WHERE id=(SELECT max(id) FROM registration_form)
            """), {"days": selected_days_sorted, "times": selected_times})

        st.success("✅ Availability saved successfully!")
        st.session_state.page = "confirmation"
        st.rerun()

# -------------------------------
# Confirmation page
# -------------------------------
def confirmation_page():
    st.subheader("🎉 Thank You for registering for the NACP!")
    with engine.begin() as conn:
        reg = conn.execute(text("SELECT * FROM registration_form ORDER BY id DESC LIMIT 1")).mappings().fetchone()
        if reg:
            st.json(dict(reg))
        else:
            st.warning("No registration found.")

# -------------------------------
# Routing
# -------------------------------
page_map = {
    "landing": landing_page,
    "registration": registration_form,
    "availability": availability_form,
    "confirmation": confirmation_page,
    "admin_login": admin_login,
    "admin_dashboard": lambda: admin_dashboard() if st.session_state.admin_logged_in else st.warning("Please login as admin first.")
}
page_map.get(st.session_state.page, landing_page)()
