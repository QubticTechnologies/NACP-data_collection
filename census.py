import sys
import os
import streamlit as st
import pandas as pd
import requests
from sqlalchemy import text
from datetime import date
from streamlit_js_eval import get_geolocation
import pydeck as pdk

# Add current directory for imports
sys.path.append(os.path.dirname(__file__))

# --- DB & Config ---
from census_app.db import engine
from census_app.config import USERS_TABLE, HOLDERS_TABLE, TOTAL_SURVEY_SECTIONS


# --- Lazy Imports to avoid circular imports ---
def _import_auth():
    from census_app.modules.auth import login_user, register_user, logout_user, create_holder_for_user
    return login_user, register_user, logout_user, create_holder_for_user


def _import_role_sidebar():
    from census_app.modules.role_sidebar import role_sidebar
    return role_sidebar


def _import_dashboards():
    from census_app.modules.dashboards import holder_dashboard, agent_dashboard
    from census_app.modules.admin_dashboard.dashboard import admin_dashboard
    return holder_dashboard, agent_dashboard, admin_dashboard


def _import_survey_sidebar():
    from census_app.modules.survey_sidebar import survey_sidebar
    return survey_sidebar


# --- Dynamic Imports ---
login_user, register_user, logout_user, create_holder_for_user = _import_auth()
role_sidebar = _import_role_sidebar()
holder_dashboard, agent_dashboard, admin_dashboard = _import_dashboards()
survey_sidebar = _import_survey_sidebar()

# --- Survey Forms ---
from census_app.modules.household_information import household_information
from census_app.modules.holding_labour_form import holding_labour_form
from census_app.modules.holder_information_form import holder_information_form
from census_app.helpers import calculate_age

# --- Streamlit Config ---
st.set_page_config(page_title="🌾 Agri Census System", layout="wide")

# --- Session Defaults ---
st.session_state.setdefault("user", None)
st.session_state.setdefault("holder_id", None)
st.session_state.setdefault("logged_out", False)
st.session_state.setdefault("current_section", 1)
st.session_state.setdefault("holder_form_data", {})
st.session_state.setdefault("labour_form_data", {})
st.session_state.setdefault("household_form_data", {})


# -----------------------------
# Helper Functions
# -----------------------------
def get_user_status(user_id: int):
    try:
        with engine.connect() as conn:
            return conn.execute(
                text(f"SELECT status FROM {USERS_TABLE} WHERE id=:uid"),
                {"uid": user_id}
            ).scalar()
    except Exception as e:
        st.error(f"Database error: {e}")
        return None


# -----------------------------
# Enhanced GIS Location Widget
# -----------------------------
def holder_location_widget(holder_id):
    st.subheader("📍 Farm Location")
    st.info("🎯 Click 'Auto Detect Location' for best accuracy, or enter coordinates manually.")

    # Fetch stored coordinates from database
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT latitude, longitude FROM holders WHERE holder_id=:hid"),
            {"hid": holder_id}
        ).fetchone()

    # Default to Nassau, Bahamas if no location stored
    stored_lat = result[0] if result and result[0] is not None else 25.0343
    stored_lon = result[1] if result and result[1] is not None else -77.3963

    # Initialize session state for this holder's coordinates
    if f"holder_lat_{holder_id}" not in st.session_state:
        st.session_state[f"holder_lat_{holder_id}"] = stored_lat
    if f"holder_lon_{holder_id}" not in st.session_state:
        st.session_state[f"holder_lon_{holder_id}"] = stored_lon

    current_lat = st.session_state[f"holder_lat_{holder_id}"]
    current_lon = st.session_state[f"holder_lon_{holder_id}"]

    # Enhanced map visualization with PyDeck
    st.markdown("#### 🗺️ Current Location Preview")

    try:
        # PyDeck map with satellite view
        view_state = pdk.ViewState(
            latitude=current_lat,
            longitude=current_lon,
            zoom=16,
            pitch=45,
        )

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=pd.DataFrame([[current_lat, current_lon]], columns=["lat", "lon"]),
            get_position=["lon", "lat"],
            get_color=[255, 0, 0, 200],
            get_radius=50,
            pickable=True,
        )

        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/satellite-streets-v11",
            initial_view_state=view_state,
            layers=[layer],
            tooltip={"text": "Farm Location: {lat}, {lon}"}
        ))
    except Exception:
        # Fallback to basic map
        st.map(pd.DataFrame([[current_lat, current_lon]], columns=["lat", "lon"]), zoom=15)

    # Auto Detect Location - HIGH ACCURACY
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🎯 Auto Detect My Location", key=f"auto_loc_btn_{holder_id}", type="primary"):
            with st.spinner("🛰️ Getting high-accuracy GPS coordinates..."):
                try:
                    loc_data = get_geolocation()
                    if loc_data and "coords" in loc_data:
                        detected_lat = loc_data["coords"]["latitude"]
                        detected_lon = loc_data["coords"]["longitude"]
                        accuracy = loc_data["coords"].get("accuracy", "Unknown")
                        altitude = loc_data["coords"].get("altitude", "N/A")

                        # Update session state
                        st.session_state[f"holder_lat_{holder_id}"] = detected_lat
                        st.session_state[f"holder_lon_{holder_id}"] = detected_lon

                        st.success(f"✅ **GPS Lock Acquired!**")
                        st.info(f"📍 Coordinates: `{detected_lat:.6f}, {detected_lon:.6f}`\n"
                                f"🎯 Accuracy: ±{accuracy}m\n"
                                f"⛰️ Altitude: {altitude}m")

                        # Fetch address for detected location
                        try:
                            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={detected_lat}&lon={detected_lon}&zoom=18&addressdetails=1"
                            headers = {"User-Agent": "AgriCensusApp/1.0"}
                            response = requests.get(url, headers=headers, timeout=10)
                            if response.status_code == 200:
                                data = response.json()
                                address = data.get("display_name", "Address not available")
                                st.success(f"📬 **Detected Address:**\n{address}")
                        except Exception:
                            pass

                        st.rerun()
                    else:
                        st.error("⚠️ Could not access GPS. Please enable location services in your browser.")
                        st.info("💡 **Tip:** Make sure you clicked 'Allow' when prompted for location access.")
                except Exception as e:
                    st.error(f"❌ GPS Error: {e}")

    with col_btn2:
        if st.button("🔄 Reset to Saved", key=f"reset_loc_btn_{holder_id}"):
            st.session_state[f"holder_lat_{holder_id}"] = stored_lat
            st.session_state[f"holder_lon_{holder_id}"] = stored_lon
            st.rerun()

    st.divider()

    # Manual coordinate entry
    st.markdown("#### ✏️ Manual Coordinate Entry")
    col1, col2 = st.columns(2)
    with col1:
        manual_lat = st.number_input(
            "Latitude",
            value=float(current_lat),
            min_value=-90.0,
            max_value=90.0,
            step=0.000001,
            format="%.6f",
            key=f"lat_input_{holder_id}",
            help="Enter latitude (North/South coordinate)"
        )
    with col2:
        manual_lon = st.number_input(
            "Longitude",
            value=float(current_lon),
            min_value=-180.0,
            max_value=180.0,
            step=0.000001,
            format="%.6f",
            key=f"lon_input_{holder_id}",
            help="Enter longitude (East/West coordinate)"
        )

    # Update button for manual entry
    if st.button("📍 Update Preview", key=f"update_preview_{holder_id}"):
        st.session_state[f"holder_lat_{holder_id}"] = manual_lat
        st.session_state[f"holder_lon_{holder_id}"] = manual_lon
        st.rerun()

    # Reverse geocode for current coordinates
    st.markdown("#### 🏠 Street Address")
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={current_lat}&lon={current_lon}&zoom=18&addressdetails=1"
        headers = {"User-Agent": "AgriCensusApp/1.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            street_address = data.get("display_name", "Address not found")

            # Extract detailed address components
            address_details = data.get("address", {})
            road = address_details.get("road", "")
            suburb = address_details.get("suburb", "")
            city = address_details.get("city", address_details.get("town", ""))
            country = address_details.get("country", "")

            formatted_address = f"{road}, {suburb}, {city}, {country}".strip(", ")
            if not formatted_address:
                formatted_address = street_address
        else:
            formatted_address = "Unable to fetch address"
    except Exception:
        formatted_address = "Address lookup failed"

    st.text_area(
        "Current Address (auto-detected)",
        value=formatted_address,
        height=80,
        disabled=True,
        help="This address is automatically generated from your coordinates"
    )

    # External map links
    col_map1, col_map2, col_map3 = st.columns(3)
    with col_map1:
        google_maps = f"https://www.google.com/maps?q={current_lat},{current_lon}"
        st.markdown(f"[🗺️ Google Maps]({google_maps})")
    with col_map2:
        osm_link = f"https://www.openstreetmap.org/?mlat={current_lat}&mlon={current_lon}&zoom=17"
        st.markdown(f"[🌍 OpenStreetMap]({osm_link})")
    with col_map3:
        apple_maps = f"http://maps.apple.com/?ll={current_lat},{current_lon}"
        st.markdown(f"[🍎 Apple Maps]({apple_maps})")

    st.divider()

    # Save to database
    col_save1, col_save2 = st.columns([2, 1])
    with col_save1:
        if st.button("💾 Save Farm Location", key=f"save_loc_btn_{holder_id}", type="primary"):
            if -90 <= current_lat <= 90 and -180 <= current_lon <= 180:
                try:
                    with engine.begin() as conn:
                        conn.execute(
                            text("UPDATE holders SET latitude=:lat, longitude=:lon WHERE holder_id=:hid"),
                            {"lat": current_lat, "lon": current_lon, "hid": holder_id}
                        )
                    st.success("✅ Location saved successfully!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Database error: {e}")
            else:
                st.error("⚠️ Invalid coordinates.")

    with col_save2:
        status = "✅ GPS Set" if current_lat != 25.0343 or current_lon != -77.3963 else "⚠️ Default"
        st.metric("Status", status)

    # Coordinate precision info
    with st.expander("📊 Location Precision Info"):
        st.markdown(f"""
        **Coordinate Precision Guide:**
        - 6 decimal places = ~0.11 meters (centimeter-level) ✅
        - 5 decimal places = ~1.1 meters
        - 4 decimal places = ~11 meters

        **Your Current Coordinates:**
        - Latitude: `{current_lat:.6f}` (6 decimals)
        - Longitude: `{current_lon:.6f}` (6 decimals)

        ✅ Precision: Centimeter-level accuracy!
        """)


# -----------------------------
# Main Login & Flow
# -----------------------------
st.sidebar.title("🌱 Agri Census System")

# Reset after logout
if st.session_state.get("logged_out"):
    st.session_state.update({"user": None, "holder_id": None, "logged_out": False})
    st.experimental_set_query_params()
    st.rerun()

# Login Flow
if st.session_state["user"] is None:
    login_choice = st.sidebar.radio("Login Type", ["Agent/Farmer", "Admin"])
    if login_choice == "Agent/Farmer":
        action = st.sidebar.radio("Action", ["Login", "Register"])
        if action == "Login":
            login_user()
        else:
            register_user()
    else:
        from census_app.modules.admin_auth import login_admin

        login_admin()

# Logged-In Flow
else:
    user = st.session_state["user"]
    role = user["role"].lower()
    user_id = user["id"]

    st.sidebar.success(f"✅ Logged in as {user['username']} ({role})")
    logout_user()

    holder_id = None
    if role == "holder":
        holder_id = create_holder_for_user(user_id, user["username"])
        st.session_state["holder_id"] = holder_id

        # Approval check
        status = get_user_status(user_id)
        if status != "approved":
            st.error("🚫 Your account is not yet approved by admin.")
            st.stop()

        # ----------- ENHANCED MAP AT THE TOP -----------
        holder_location_widget(holder_id)

        # Validate coordinates
        with engine.connect() as conn:
            loc = conn.execute(
                text("SELECT latitude, longitude FROM holders WHERE holder_id=:hid"),
                {"hid": holder_id}
            ).fetchone()
        if not loc or loc[0] is None or loc[1] is None:
            st.warning("⚠️ Please set your farm location to continue.")
            st.stop()

        # ----------- SURVEY NAVIGATION -----------
        if st.session_state["current_section"] < 1:
            st.session_state["current_section"] = 1

        survey_sidebar(holder_id=holder_id)
        st.divider()

        # Navigation buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅ Back", key=f"back_{holder_id}") and st.session_state["current_section"] > 1:
                st.session_state["current_section"] -= 1
                st.rerun()
        with col3:
            if st.button("Next ➡", key=f"next_{holder_id}") and st.session_state[
                "current_section"] < TOTAL_SURVEY_SECTIONS:
                st.session_state["current_section"] += 1
                st.rerun()

        # Render current section dynamically
        current = st.session_state["current_section"]
        st.markdown(f"### Section {current} of {TOTAL_SURVEY_SECTIONS}")
        if current == 1:
            holder_information_form(holder_id)
        elif current == 2:
            holding_labour_form(holder_id)
        elif current == 3:
            household_information(holder_id)

        # ----------- HOLDER DASHBOARD -----------
        st.divider()
        st.title("📊 Holder Dashboard")

        # Age info
        try:
            with engine.connect() as conn:
                dob_row = conn.execute(
                    text(f"SELECT date_of_birth FROM {HOLDERS_TABLE} WHERE holder_id=:hid"),
                    {"hid": holder_id}
                ).scalar()
            if dob_row:
                if isinstance(dob_row, str):
                    dob_row = date.fromisoformat(dob_row)
                st.sidebar.info(f"🎂 Age: {calculate_age(dob_row)} years")
        except Exception as e:
            st.sidebar.warning(f"Could not fetch holder age: {e}")

    # Agent/Admin Menus
    role_sidebar(user_role=role, holder_id=holder_id)