# main_app.py - NACP Bahamas Complete Application

import os
import streamlit as st
import pandas as pd
from sqlalchemy import text, create_engine
from sqlalchemy.exc import SQLAlchemyError
import requests
import re
import time
import json
import folium
from streamlit_folium import folium_static, st_folium
import math


# =============================
# DATABASE CONNECTION WITH RENDER POSTGRESQL
# =============================
@st.cache_resource(show_spinner=False)
def get_database_connection():
    """Create database connection with Render PostgreSQL"""
    connection_strings = [
        "postgresql://agri_data_user:lo7GjOG52LrKPTlk2wDEnNgq1965WG0Q@dpg-d3jgpvc9c44c73bs8m60-a.oregon-postgres.render.com/agri_data",
        "postgresql://postgres:postgres@localhost:5432/nacp_bahamas",
        "sqlite:///nacp_bahamas.db"
    ]

    for connection_string in connection_strings:
        if connection_string:
            try:
                if connection_string.startswith('postgres://'):
                    connection_string = connection_string.replace('postgres://', 'postgresql://', 1)

                engine = create_engine(connection_string, pool_pre_ping=True)

                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))

                db_type = "PostgreSQL" if "postgresql" in connection_string else "SQLite"

                if "render.com" in connection_string:
                    st.success("✅ Connected to Render PostgreSQL Database")
                elif "localhost" in connection_string:
                    st.success("✅ Connected to Local PostgreSQL Database")
                else:
                    st.success("✅ Connected to SQLite Database")

                return engine, db_type
            except Exception as e:
                continue

    st.error("❌ All database connection attempts failed. Using in-memory storage.")
    return None, "memory"


# Initialize database connection
engine, db_type = get_database_connection()

# =============================
# STREAMLIT PAGE CONFIG
# =============================
st.set_page_config(page_title="NACP Bahamas", layout="wide")

# =============================
# SESSION STATE DEFAULTS
# =============================
for key, default in {
    "page": "landing",
    "admin_logged_in": False,
    "latitude": None,
    "longitude": None,
    "consent_bool": False,
    "auto_lat": None,
    "auto_lon": None,
    "auto_full_address": "",
    "gps_accuracy": None,
    "address_components": {},
    "map_counter": 0,
    "formatted_cell": "",
    "formatted_tel": "",
    "location_source": None,
    "current_island": None,
    "registration_data": {},
    "current_registration_id": None,
    "database_initialized": False,
    "map_click_lat": None,
    "map_click_lon": None,
    "manual_coordinates": False
}.items():
    st.session_state.setdefault(key, default)

# =============================
# ADMIN CREDENTIALS AND ISLAND DATA
# =============================
ADMIN_USERS = {"admin": "admin123"}

ISLAND_SETTLEMENTS = {
    "New Providence": ["Nassau", "Cable Beach", "Paradise Island", "South Beach", "Lyford Cay"],
    "Grand Bahama": ["Freeport", "Lucaya", "West End", "Eight Mile Rock"],
    "Abaco": ["Marsh Harbour", "Treasure Cay", "Hope Town", "Man-O-War Cay"],
    "Eleuthera": ["Governor's Harbour", "Rock Sound", "Tarpum Bay", "Palmetto Point"],
    "Exuma": ["George Town", "Rolleville", "Mount Thompson", "Barraterre"],
    "Andros": ["Fresh Creek", "Nicholl's Town", "Staniard Creek", "Congo Town"],
    "Long Island": ["Clarence Town", "Deadman's Cay", "Salt Pond", "Stella Maris"],
    "Cat Island": ["Arthur's Town", "The Bight", "Orange Creek", "Port Howe"],
    "Acklins": ["Spring Point", "Snug Corner", "Lovely Bay", "Mason's Bay"],
    "Crooked Island": ["Colonel Hill", "Landrail Point", "Cabbage Hill", "French Wells"],
    "Bimini": ["Alice Town", "Bailey Town", "Porgy Bay", "North Bimini"],
    "Berry Islands": ["Great Harbour Cay", "Chub Cay", "Bullocks Harbour", "Sugar Beach"],
    "Inagua": ["Matthew Town", "Main Town", "The Salt Pond", "Northeast Point"],
    "Mayaguana": ["Abraham's Bay", "Pirate's Well", "Betsy Bay", "Upper Bay"],
    "Ragged Island": ["Duncan Town", "Ragged Island Settlement"],
    "San Salvador": ["Cockburn Town", "United Estates", "Sugar Loaf", "Pigeon Creek"],
    "Rum Cay": ["Port Nelson", "Black Rock", "The Harbor", "Conch Shell Bay"]
}

ISLAND_CENTERS = {
    "New Providence": (25.0343, -77.3963),
    "Grand Bahama": (26.6594, -78.5207),
    "Abaco": (26.4670, -77.0833),
    "Eleuthera": (25.1106, -76.1480),
    "Exuma": (23.6193, -75.9696),
    "Andros": (24.2886, -77.6850),
    "Long Island": (23.1765, -75.0962),
    "Cat Island": (24.4033, -75.5250),
    "Acklins": (22.3650, -74.0100),
    "Crooked Island": (22.6392, -74.1536),
    "Bimini": (25.7000, -79.2833),
    "Berry Islands": (25.6250, -77.7500),
    "Inagua": (20.9500, -73.6667),
    "Mayaguana": (22.3833, -73.0000),
    "Ragged Island": (22.2167, -75.7333),
    "San Salvador": (24.0583, -74.5333),
    "Rum Cay": (23.6853, -74.8419)
}


# =============================
# UTILITY FUNCTIONS
# =============================
def safe_convert_array_data(data):
    """Safely convert array data from database to Python list"""
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, str):
        try:
            if data.startswith('[') and data.endswith(']'):
                return json.loads(data)
            elif data.startswith('{') and data.endswith('}'):
                return data[1:-1].split(',')
        except:
            pass
    return [data] if data else []


def format_array_for_display(data):
    """Format array data for display in the UI"""
    if not data:
        return "None"
    array_data = safe_convert_array_data(data)
    if array_data:
        return ", ".join(str(item) for item in array_data)
    return "None"


def format_phone_number(phone_str):
    """Format phone number as (242) XXX-XXXX"""
    if not phone_str:
        return ""
    digits = re.sub(r'\D', '', phone_str)
    if len(digits) == 7:
        return f"(242) {digits[:3]}-{digits[3:]}"
    elif len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        return digits


def validate_phone_number(phone_str):
    """Validate Bahamian phone number format"""
    if not phone_str:
        return False
    digits = re.sub(r'\D', '', phone_str)
    if len(digits) == 7:
        return True
    elif len(digits) == 10 and digits[:3] == '242':
        return True
    elif len(digits) == 11 and digits[0] == '1' and digits[1:4] == '242':
        return True
    return False


def get_island_zoom_level(island):
    """Get appropriate zoom level for each island"""
    zoom_levels = {
        "New Providence": 12, "Grand Bahama": 11, "Abaco": 10, "Eleuthera": 10,
        "Exuma": 10, "Andros": 9, "Long Island": 10, "Cat Island": 10,
        "Acklins": 11, "Crooked Island": 11, "Bimini": 12, "Berry Islands": 11,
        "Inagua": 10, "Mayaguana": 11, "Ragged Island": 12, "San Salvador": 11,
        "Rum Cay": 12
    }
    return zoom_levels.get(island, 10)


# =============================
# DATABASE INITIALIZATION
# =============================
def initialize_database():
    """Initialize database tables if they don't exist"""
    if engine is None:
        return False

    if st.session_state.get("database_initialized"):
        return True

    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS registration_form (
                    id SERIAL PRIMARY KEY,
                    consent BOOLEAN NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    email VARCHAR(150) NOT NULL,
                    telephone VARCHAR(20),
                    cell VARCHAR(20) NOT NULL,
                    communication_methods TEXT[],
                    island VARCHAR(100) NOT NULL,
                    settlement VARCHAR(100) NOT NULL,
                    street_address TEXT NOT NULL,
                    interview_methods TEXT[],
                    available_days TEXT[],
                    available_times TEXT[],
                    latitude DECIMAL(10, 8),
                    longitude DECIMAL(11, 8),
                    gps_accuracy DECIMAL(10, 2),
                    location_source VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

        st.session_state.database_initialized = True
        st.success("✅ Database initialized successfully")
        return True

    except Exception as e:
        st.error(f"❌ Database initialization error: {e}")
        return False


# Initialize database on startup
if st.session_state.get("page") == "landing" and engine is not None and not st.session_state.get(
        "database_initialized"):
    initialize_database()


# =============================
# DATA STORAGE FUNCTIONS
# =============================
def save_registration_data(data):
    """Save registration data to database or session state as fallback"""
    if engine is not None:
        try:
            sql = """
                INSERT INTO registration_form (
                    consent, first_name, last_name, email, telephone, cell,
                    communication_methods, island, settlement, street_address,
                    interview_methods, available_days, available_times, 
                    latitude, longitude, gps_accuracy, location_source
                ) VALUES (
                    :consent, :first_name, :last_name, :email, :telephone, :cell,
                    :communication_methods, :island, :settlement, :street_address,
                    :interview_methods, :available_days, :available_times, 
                    :latitude, :longitude, :gps_accuracy, :location_source
                ) RETURNING id
            """

            with engine.begin() as conn:
                result = conn.execute(text(sql), data)
                registration_id = result.scalar()
                st.session_state.current_registration_id = registration_id
                return True

        except Exception as e:
            st.error(f"❌ Database save error: {e}")
            return False
    else:
        registration_id = len(st.session_state.get("registration_data", {})) + 1
        if "registration_data" not in st.session_state:
            st.session_state.registration_data = {}

        data['id'] = registration_id
        st.session_state.registration_data[registration_id] = data
        st.session_state.current_registration_id = registration_id
        st.warning("⚠️ Using temporary storage (database unavailable)")
        return True


def update_registration_location(registration_id, lat, lon, accuracy=None, source=None):
    """Update location data for a specific registration"""
    if engine is not None:
        try:
            update_data = {
                "lat": lat,
                "lon": lon,
                "id": registration_id
            }

            if accuracy is not None:
                update_data["accuracy"] = accuracy
            if source is not None:
                update_data["source"] = source

            if accuracy is not None and source is not None:
                sql = """
                    UPDATE registration_form 
                    SET latitude = :lat, longitude = :lon, 
                        gps_accuracy = :accuracy, location_source = :source
                    WHERE id = :id
                """
            else:
                sql = """
                    UPDATE registration_form 
                    SET latitude = :lat, longitude = :lon
                    WHERE id = :id
                """

            with engine.begin() as conn:
                result = conn.execute(text(sql), update_data)
                return result.rowcount > 0

        except Exception as e:
            return False
    else:
        if registration_id in st.session_state.get("registration_data", {}):
            st.session_state.registration_data[registration_id]['latitude'] = lat
            st.session_state.registration_data[registration_id]['longitude'] = lon
            st.session_state.registration_data[registration_id]['gps_accuracy'] = accuracy
            st.session_state.registration_data[registration_id]['location_source'] = source
            return True
        return False


def get_latest_registration():
    """Get the latest registration from database or session state"""
    registration_id = st.session_state.get("current_registration_id")

    if registration_id:
        if engine is not None:
            try:
                with engine.begin() as conn:
                    result = conn.execute(
                        text("SELECT * FROM registration_form WHERE id = :id"),
                        {"id": registration_id}
                    )
                    return result.mappings().fetchone()
            except Exception as e:
                return None
        else:
            return st.session_state.get("registration_data", {}).get(registration_id)

    if engine is not None:
        try:
            with engine.begin() as conn:
                result = conn.execute(
                    text("SELECT * FROM registration_form ORDER BY id DESC LIMIT 1")
                )
                return result.mappings().fetchone()
        except Exception as e:
            return None
    else:
        registration_data = st.session_state.get("registration_data", {})
        if registration_data:
            latest_id = max(registration_data.keys())
            return registration_data[latest_id]
        return None


# =============================
# LOCATION FUNCTIONS
# =============================
def get_enhanced_ip_location():
    """Enhanced fallback method using IP geolocation"""
    try:
        st.info("🔍 Detecting approximate location...")
        resp = requests.get("https://ipapi.co/json/", timeout=10)
        data = resp.json()

        lat = data.get("latitude")
        lon = data.get("longitude")

        if lat and lon:
            st.session_state.update({
                "latitude": lat,
                "longitude": lon,
                "location_source": "ip",
                "manual_coordinates": False
            })

            registration_id = st.session_state.get("current_registration_id")
            if registration_id:
                update_registration_location(registration_id, lat, lon, None, "ip")
                st.success(f"📍 **IP Location Detected and Saved!** {lat:.6f}, {lon:.6f}")
            else:
                st.success(f"📍 IP Location detected: {lat:.6f}, {lon:.6f}")
            return True
        else:
            st.warning("⚠️ Unable to detect location via IP")
            return False

    except Exception as e:
        st.warning("⚠️ Unable to auto-detect location. Please use the map or manual entry.")
        return False


def get_safe_coordinates():
    """Get safe coordinate values with fallbacks"""
    default_lat = 25.0343
    default_lon = -77.3963

    lat = (st.session_state.get("map_click_lat") or
           st.session_state.get("latitude") or
           default_lat)
    lon = (st.session_state.get("map_click_lon") or
           st.session_state.get("longitude") or
           default_lon)

    try:
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        lat = default_lat
        lon = default_lon

    return lat, lon


def save_current_location_to_registration():
    """Save current location from session state to the current registration"""
    registration_id = st.session_state.get("current_registration_id")
    lat = st.session_state.get("latitude")
    lon = st.session_state.get("longitude")
    accuracy = st.session_state.get("gps_accuracy")
    source = st.session_state.get("location_source")

    if registration_id and lat and lon:
        return update_registration_location(registration_id, lat, lon, accuracy, source)
    return False


def handle_map_click(click_data):
    """Handle map click events to set coordinates"""
    if click_data and 'lat' in click_data and 'lng' in click_data:
        st.session_state.map_click_lat = click_data['lat']
        st.session_state.map_click_lon = click_data['lng']
        st.session_state.latitude = click_data['lat']
        st.session_state.longitude = click_data['lng']
        st.session_state.location_source = "map_click"
        st.session_state.manual_coordinates = False
        return True
    return False


def show_interactive_map():
    """Display an interactive map for coordinate selection"""
    lat, lon = get_safe_coordinates()
    current_island = st.session_state.get("current_island")

    if current_island and current_island in ISLAND_CENTERS:
        center_lat, center_lon = ISLAND_CENTERS[current_island]
        zoom_level = get_island_zoom_level(current_island)
        map_title = f"🗺️ Interactive Map of {current_island}"
    else:
        center_lat, center_lon = lat, lon
        zoom_level = 15
        map_title = "🗺️ Interactive Location Map"

    st.markdown(f"### {map_title}")
    st.markdown("**📌 Click anywhere on the map to set your exact location**")

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_level,
        tiles='OpenStreetMap'
    )

    if st.session_state.get("map_click_lat") and st.session_state.get("map_click_lon"):
        folium.Marker(
            [st.session_state.map_click_lat, st.session_state.map_click_lon],
            popup="Selected Location",
            tooltip="Your selected location",
            icon=folium.Icon(color='green', icon='ok-sign')
        ).add_to(m)
    elif st.session_state.get("latitude") and st.session_state.get("longitude"):
        folium.Marker(
            [lat, lon],
            popup="Current Location",
            tooltip="Current detected location",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    m.add_child(folium.LatLngPopup())

    map_data = st_folium(m, width=700, height=500, key=f"interactive_map_{st.session_state.map_counter}")

    if map_data and map_data.get("last_clicked"):
        if handle_map_click(map_data["last_clicked"]):
            st.success(
                f"📍 **Location selected!** Coordinates: {map_data['last_clicked']['lat']:.6f}, {map_data['last_clicked']['lng']:.6f}")
            st.session_state.map_counter += 1
            st.rerun()

    return map_data


def show_coordinate_controls():
    """Show coordinate display and manual input controls"""
    st.markdown("#### 📍 Coordinate Controls")

    lat, lon = get_safe_coordinates()

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        st.metric("Latitude", f"{lat:.6f}")

    with col2:
        st.metric("Longitude", f"{lon:.6f}")

    with col3:
        source = st.session_state.get("location_source", "unknown")
        source_display = {
            "gps": "🎯 GPS",
            "ip": "🌐 IP",
            "map_click": "🗺️ Map",
            "manual": "✏️ Manual",
            "unknown": "❓ Unknown"
        }
        st.metric("Source", source_display.get(source, "❓ Unknown"))

    with st.expander("✏️ Enter Coordinates Manually", expanded=False):
        st.markdown("**Enter precise coordinates manually:**")

        col_lat, col_lon = st.columns(2)
        with col_lat:
            manual_lat = st.number_input(
                "Latitude",
                value=float(lat),
                format="%.6f",
                step=0.0001,
                key="manual_lat_input"
            )
        with col_lon:
            manual_lon = st.number_input(
                "Longitude",
                value=float(lon),
                format="%.6f",
                step=0.0001,
                key="manual_lon_input"
            )

        if st.button("✅ Use Manual Coordinates", key="use_manual_coords"):
            st.session_state.latitude = manual_lat
            st.session_state.longitude = manual_lon
            st.session_state.location_source = "manual"
            st.session_state.manual_coordinates = True
            st.session_state.map_click_lat = None
            st.session_state.map_click_lon = None
            st.success("✅ Manual coordinates set!")
            st.rerun()

    if st.session_state.get("latitude") or st.session_state.get("longitude"):
        if st.button("🗑️ Clear Coordinates", key="clear_coords"):
            st.session_state.latitude = None
            st.session_state.longitude = None
            st.session_state.map_click_lat = None
            st.session_state.map_click_lon = None
            st.session_state.location_source = None
            st.session_state.manual_coordinates = False
            st.success("✅ Coordinates cleared!")
            st.rerun()


# =============================
# RESET SESSION FUNCTION
# =============================
def reset_session():
    """Clear all session state data"""
    keys_to_keep = ["registration_data", "database_initialized"]
    keys_to_reset = [key for key in st.session_state.keys() if key not in keys_to_keep]

    for key in keys_to_reset:
        st.session_state.pop(key, None)

    st.success("✅ Session reset successfully!")
    st.rerun()


# =============================
# PAGE FUNCTIONS
# =============================
def landing_page():
    st.title("🌾 NACP - National Agricultural Census Pilot Project")
    st.markdown("""
    Welcome to the **National Agricultural Census Pilot Project (NACP)** for The Bahamas.

    This initiative aims to collect accurate agricultural data to better serve our farming communities. 
    Your participation helps shape the future of agriculture in The Bahamas.
    """)

    if engine is None:
        st.warning("⚠️ Running in offline mode - data will be stored temporarily in browser")
    elif not st.session_state.get("database_initialized"):
        if st.button("🔄 Initialize Database"):
            if initialize_database():
                st.rerun()

    st.divider()

    st.markdown("### 📍 Location Setup")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗺️ **Use Interactive Map**", use_container_width=True, type="primary"):
            st.session_state.page = "location_confirmation"
            st.rerun()
    with col2:
        if st.button("🌐 **Detect Location**", use_container_width=True):
            get_enhanced_ip_location()
            st.rerun()

    st.divider()

    st.markdown("### 🚀 Get Started")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("📝 **Start Registration**", use_container_width=True, type="primary"):
            st.session_state.page = "registration"
            st.rerun()
    with col_b:
        if st.button("🔐 **Admin Portal**", use_container_width=True):
            st.session_state.page = "admin_login"
            st.rerun()
    with col_c:
        if st.button("🔄 **Reset Session**", use_container_width=True):
            reset_session()


def registration_form():
    st.title("🌱 Registration Form")

    nscp_text = """The Government of The Bahamas, through the Ministry of Agriculture and Marine Resources and its agencies, is committed to delivering timely, relevant, and effective support to producers. However, when agricultural data and producers' needs are misaligned, the effectiveness of these efforts diminishes.

**National Agricultural Census Pilot (NACP)** is your opportunity to directly influence how agricultural data is collected, processed, and used. By participating, you help design better, more responsive processes that reflect the realities of the industry."""

    st.markdown("### ℹ️ About the NACP")
    st.text_area("Please read before providing consent:", value=nscp_text, height=200, disabled=True)

    st.divider()

    st.markdown("### 📝 Consent")
    consent = st.radio(
        "Do you wish to participate in the NACP?",
        ["I do not wish to participate", "I do wish to participate"],
        key="consent_radio"
    )
    st.session_state["consent_bool"] = (consent == "I do wish to participate")

    if not st.session_state["consent_bool"]:
        st.warning("⚠️ You must give consent to proceed with registration.")
        if st.button("← Back to Home"):
            st.session_state.page = "landing"
            st.rerun()
        return

    st.markdown("### 👤 Personal Information")
    col1, col2 = st.columns(2)

    with col1:
        first_name = st.text_input("First Name *", key="reg_fname")
        last_name = st.text_input("Last Name *", key="reg_lname")
        email = st.text_input("Email *", key="reg_email")

    with col2:
        cell_raw = st.text_input("Cell Number (Primary Contact) *",
                                 key="reg_cell",
                                 placeholder="e.g., 2424567890 or 4567890")
        telephone_raw = st.text_input("Alternate Number (Optional)",
                                      key="reg_tel",
                                      placeholder="e.g., 2424567890")

    st.markdown("### 📍 Address Information")
    col1, col2 = st.columns(2)
    with col1:
        island_selected = st.selectbox(
            "Island *",
            list(ISLAND_SETTLEMENTS.keys()),
            key="reg_island"
        )

        settlements = ISLAND_SETTLEMENTS.get(island_selected, [])
        if settlements:
            settlement_selected = st.selectbox(
                "Settlement/District *",
                settlements,
                key="reg_settlement"
            )
        else:
            settlement_selected = st.text_input(
                "Settlement/District *",
                key="reg_settlement"
            )

    with col2:
        street_address = st.text_input(
            "Street Address *",
            key="reg_street",
            placeholder="e.g., 123 Main Street, Coral Harbour"
        )

    st.markdown("### 💬 Preferred Communication Methods")
    comm_methods = ["WhatsApp", "Phone Call", "Email", "Text Message"]
    selected_methods = []
    cols = st.columns(4)
    for i, method in enumerate(comm_methods):
        with cols[i]:
            if st.checkbox(method, key=f"comm_{method}"):
                selected_methods.append(method)

    st.markdown("### 🗣️ Preferred Interview Method")
    interview_methods = ["In-person Interview", "Phone Interview", "Self Reporting"]
    interview_selected = []
    cols = st.columns(3)
    for i, method in enumerate(interview_methods):
        with cols[i]:
            if st.checkbox(method, key=f"interview_{method}"):
                interview_selected.append(method)

    st.divider()

    col_back, col_save = st.columns([1, 2])
    with col_back:
        if st.button("← Back to Home"):
            st.session_state.page = "landing"
            st.rerun()

    with col_save:
        if st.button("💾 Save & Continue to Availability", type="primary", use_container_width=True):
            if not all([first_name, last_name, cell_raw, email, island_selected, settlement_selected, street_address]):
                st.error("⚠️ Please complete all required fields marked with *")
                return

            if not validate_phone_number(cell_raw):
                st.error("⚠️ Please enter a valid Bahamian cell number (7 or 10 digits).")
                return

            if telephone_raw and not validate_phone_number(telephone_raw):
                st.error("⚠️ Please enter a valid telephone number (7 or 10 digits).")
                return

            if not selected_methods:
                st.error("⚠️ Please select at least one communication method.")
                return

            if not interview_selected:
                st.error("⚠️ Please select at least one interview method.")
                return

            formatted_cell = format_phone_number(cell_raw)
            formatted_telephone = format_phone_number(telephone_raw) if telephone_raw else None

            registration_data = {
                "consent": st.session_state["consent_bool"],
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "telephone": formatted_telephone,
                "cell": formatted_cell,
                "communication_methods": selected_methods,
                "island": island_selected,
                "settlement": settlement_selected,
                "street_address": street_address,
                "interview_methods": interview_selected,
                "available_days": [],
                "available_times": [],
                "latitude": st.session_state.get("latitude"),
                "longitude": st.session_state.get("longitude"),
                "gps_accuracy": st.session_state.get("gps_accuracy"),
                "location_source": st.session_state.get("location_source")
            }

            if save_registration_data(registration_data):
                st.success("✅ Registration information saved successfully!")
                st.session_state.page = "availability"
                st.rerun()
            else:
                st.error("❌ Failed to save registration. Please try again.")


def availability_form():
    st.title("🕒 Availability Preferences")

    st.markdown("### 📅 Preferred Days")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    selected_days = []
    cols = st.columns(7)
    for i, day in enumerate(days):
        with cols[i]:
            if st.checkbox(day[:3], key=f"day_{day}"):
                selected_days.append(day)

    st.markdown("### ⏰ Preferred Time Slots")
    time_slots = ["Morning (7-10am)", "Midday (11-1pm)", "Afternoon (2-5pm)", "Evening (6-8pm)"]
    selected_times = []
    cols = st.columns(4)
    for i, time_slot in enumerate(time_slots):
        with cols[i]:
            if st.checkbox(time_slot, key=f"time_{time_slot}"):
                selected_times.append(time_slot)

    st.divider()

    col_back, col_save = st.columns([1, 2])
    with col_back:
        if st.button("← Back to Registration"):
            st.session_state.page = "registration"
            st.rerun()

    with col_save:
        if st.button("💾 Save Availability & Continue to Location", type="primary"):
            if not selected_days or not selected_times:
                st.error("⚠️ Please select at least one day and one time slot.")
                return

            registration_id = st.session_state.get("current_registration_id")
            if registration_id:
                if engine is not None:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                UPDATE registration_form 
                                SET available_days = :days, available_times = :times
                                WHERE id = :id
                            """), {
                                "days": selected_days,
                                "times": selected_times,
                                "id": registration_id
                            })
                    except Exception as e:
                        st.error(f"❌ Database update error: {e}")
                        return

                if registration_id in st.session_state.get("registration_data", {}):
                    st.session_state.registration_data[registration_id]['available_days'] = selected_days
                    st.session_state.registration_data[registration_id]['available_times'] = selected_times

                st.success("✅ Availability information saved successfully!")
                st.session_state.page = "location_confirmation"
                st.rerun()
            else:
                st.error("❌ No registration found. Please start over.")


def location_confirmation_page():
    st.title("📍 Confirm Your Location")

    st.markdown("""
    ### 🎯 Set Your Exact Location

    **Choose your method:**
    - 🗺️ **Click on the map** below to select your exact location
    - 🌐 **Use IP** for approximate location  
    - ✏️ **Enter manually** if you know your coordinates
    """)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌐 **DETECT LOCATION**", use_container_width=True, type="primary"):
            get_enhanced_ip_location()
            st.rerun()
    with col2:
        if st.button("🗑️ **CLEAR LOCATION**", use_container_width=True):
            st.session_state.latitude = None
            st.session_state.longitude = None
            st.session_state.map_click_lat = None
            st.session_state.map_click_lon = None
            st.session_state.location_source = None
            st.session_state.manual_coordinates = False
            st.success("✅ Location cleared!")
            st.rerun()

    st.divider()

    show_interactive_map()

    st.divider()

    show_coordinate_controls()

    st.divider()

    col_back, col_save, col_continue = st.columns([1, 1, 1])

    with col_back:
        if st.button("← Back"):
            st.session_state.page = "availability" if st.session_state.get("current_registration_id") else "landing"
            st.rerun()

    with col_save:
        if st.session_state.get("latitude") and st.session_state.get("longitude"):
            if st.button("💾 Save Location", type="primary", use_container_width=True):
                if save_current_location_to_registration():
                    st.success("✅ Location saved to your registration!")
                else:
                    st.error("❌ Failed to save location. Please try again.")
        else:
            st.button("💾 Save Location", disabled=True, use_container_width=True)

    with col_continue:
        if st.button("✅ Continue", type="primary", use_container_width=True):
            if st.session_state.get("latitude") and st.session_state.get("longitude"):
                save_current_location_to_registration()
                st.session_state.page = "final_confirmation"
                st.rerun()
            else:
                st.warning("⚠️ Please set your location first")


def final_confirmation_page():
    st.title("🎉 Registration Complete!")

    st.success("✅ **All information saved! Thank you for completing your registration.**")

    reg = get_latest_registration()
    if reg:
        if reg.get('latitude') and reg.get('longitude'):
            source = reg.get('location_source', 'manual')
            source_display = {
                'gps': '🎯 GPS',
                'ip': '🌐 IP',
                'map_click': '🗺️ Map',
                'manual': '✏️ Manual',
                'unknown': '❓ Unknown'
            }
            st.success(f"📍 **Location saved via {source_display.get(source, 'manual')}**")

        st.markdown("### 📋 Registration Summary")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 👤 Personal Information")
            st.write(f"**Name:** {reg.get('first_name', '')} {reg.get('last_name', '')}")
            st.write(f"**Email:** {reg.get('email', '')}")
            st.write(f"**Cell:** {reg.get('cell', '')}")
            if reg.get('telephone'):
                st.write(f"**Alternate:** {reg.get('telephone', '')}")

            st.markdown("#### 📍 Address")
            st.write(f"**Island:** {reg.get('island', '')}")
            st.write(f"**Settlement:** {reg.get('settlement', '')}")
            st.write(f"**Street:** {reg.get('street_address', '')}")

        with col2:
            st.markdown("#### 💬 Communication Preferences")
            st.write(f"**Methods:** {format_array_for_display(reg.get('communication_methods'))}")
            st.write(f"**Interview:** {format_array_for_display(reg.get('interview_methods'))}")

            st.markdown("#### 🕒 Availability")
            st.write(f"**Days:** {format_array_for_display(reg.get('available_days'))}")
            st.write(f"**Times:** {format_array_for_display(reg.get('available_times'))}")

            if reg.get('latitude') and reg.get('longitude'):
                st.markdown("#### 📍 Location")
                st.write(f"**Coordinates:** {reg.get('latitude'):.6f}, {reg.get('longitude'):.6f}")
                st.write(f"**Source:** {source_display.get(source, 'Unknown')}")

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()

    with col2:
        if st.button("📝 New Registration", use_container_width=True):
            reset_session()
            st.session_state.page = "registration"
            st.rerun()

    with col3:
        if st.button("🗺️ View Location", use_container_width=True):
            st.session_state.page = "location_confirmation"
            st.rerun()


def admin_login():
    st.title("🔐 Admin Portal")

    st.markdown("### Administrator Login")

    col1, col2 = st.columns(2)

    with col1:
        username = st.text_input("Username", key="admin_user")
    with col2:
        password = st.text_input("Password", type="password", key="admin_pass")

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        if st.button("🚪 Login", use_container_width=True, type="primary"):
            if username in ADMIN_USERS and ADMIN_USERS[username] == password:
                st.session_state.admin_logged_in = True
                st.session_state.page = "admin_dashboard"
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

    st.divider()

    if st.button("← Back to Home"):
        st.session_state.page = "landing"
        st.rerun()


def admin_dashboard():
    if not st.session_state.get("admin_logged_in"):
        st.error("❌ Access denied. Please log in.")
        st.session_state.page = "admin_login"
        st.rerun()
        return

    st.title("📊 Admin Dashboard")

    tab1, tab2, tab3 = st.tabs(["📋 Registrations", "🗺️ Map View", "⚙️ Database"])

    with tab1:
        st.markdown("### 📋 All Registrations")

        if engine is not None:
            try:
                with engine.begin() as conn:
                    result = conn.execute(text("SELECT COUNT(*) FROM registration_form"))
                    count = result.scalar()
                    st.metric("Total Registrations", count)
            except Exception as e:
                st.error(f"Database error: {e}")
                count = 0
        else:
            count = len(st.session_state.get("registration_data", {}))
            st.metric("Total Registrations", count)

        if count > 0:
            if engine is not None:
                try:
                    with engine.begin() as conn:
                        result = conn.execute(
                            text("""
                                SELECT id, first_name, last_name, email, cell, island, settlement, 
                                       created_at, latitude, longitude, location_source
                                FROM registration_form 
                                ORDER BY created_at DESC
                            """)
                        )
                        registrations = result.mappings().fetchall()
                except Exception as e:
                    st.error(f"Error loading data: {e}")
                    registrations = []
            else:
                registrations = list(st.session_state.get("registration_data", {}).values())

            for reg in registrations:
                with st.expander(f"👤 {reg.get('first_name', '')} {reg.get('last_name', '')} - {reg.get('island', '')}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Email:** {reg.get('email', '')}")
                        st.write(f"**Cell:** {reg.get('cell', '')}")
                        st.write(f"**Island:** {reg.get('island', '')}")
                        st.write(f"**Settlement:** {reg.get('settlement', '')}")

                    with col2:
                        st.write(f"**Registered:** {reg.get('created_at', '')}")
                        if reg.get('latitude') and reg.get('longitude'):
                            st.write(f"**Location:** {reg.get('latitude'):.6f}, {reg.get('longitude'):.6f}")
                            st.write(f"**Source:** {reg.get('location_source', 'Unknown')}")

                    if st.button(f"Delete Registration #{reg.get('id', '')}", key=f"del_{reg.get('id', '')}"):
                        if delete_registration(reg.get('id')):
                            st.success("Registration deleted")
                            st.rerun()
                        else:
                            st.error("Failed to delete registration")
        else:
            st.info("No registrations found.")

    with tab2:
        st.markdown("### 🗺️ Registration Locations")

        if engine is not None:
            try:
                with engine.begin() as conn:
                    result = conn.execute(
                        text(
                            "SELECT first_name, last_name, island, settlement, latitude, longitude FROM registration_form WHERE latitude IS NOT NULL AND longitude IS NOT NULL")
                    )
                    locations = result.mappings().fetchall()
            except Exception as e:
                st.error(f"Error loading locations: {e}")
                locations = []
        else:
            locations = [
                reg for reg in st.session_state.get("registration_data", {}).values()
                if reg.get('latitude') and reg.get('longitude')
            ]

        if locations:
            m = folium.Map(location=[25.0343, -77.3963], zoom_start=7)

            for loc in locations:
                if loc.get('latitude') and loc.get('longitude'):
                    popup_text = f"👤 {loc.get('first_name', '')} {loc.get('last_name', '')}<br>📍 {loc.get('island', '')}, {loc.get('settlement', '')}"
                    folium.Marker(
                        [loc.get('latitude'), loc.get('longitude')],
                        popup=popup_text,
                        tooltip=f"{loc.get('first_name', '')} {loc.get('last_name', '')}"
                    ).add_to(m)

            folium_static(m, width=800, height=600)
        else:
            st.info("No location data available.")

    with tab3:
        st.markdown("### ⚙️ Database Management")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Database Type", db_type)

            if st.button("🔄 Initialize Tables", use_container_width=True):
                if initialize_database():
                    st.success("Tables initialized")
                else:
                    st.error("Failed to initialize tables")

            if st.button("🗑️ Clear All Data", use_container_width=True):
                if clear_all_data():
                    st.success("All data cleared")
                    st.rerun()
                else:
                    st.error("Failed to clear data")

        with col2:
            if st.button("📤 Export Data", use_container_width=True):
                export_data()

            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()

    st.divider()

    if st.button("🚪 Logout", type="primary"):
        st.session_state.admin_logged_in = False
        st.session_state.page = "landing"
        st.rerun()


def delete_registration(reg_id):
    """Delete a specific registration"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                result = conn.execute(
                    text("DELETE FROM registration_form WHERE id = :id"),
                    {"id": reg_id}
                )
                return result.rowcount > 0
        except Exception as e:
            st.error(f"Delete error: {e}")
            return False
    else:
        if reg_id in st.session_state.get("registration_data", {}):
            del st.session_state.registration_data[reg_id]
            return True
        return False


def clear_all_data():
    """Clear all registration data"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                conn.execute(text("DELETE FROM registration_form"))
                conn.execute(text("ALTER SEQUENCE registration_form_id_seq RESTART WITH 1"))
            return True
        except Exception as e:
            st.error(f"Clear error: {e}")
            return False
    else:
        st.session_state.registration_data = {}
        return True


def export_data():
    """Export registration data to CSV"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                result = conn.execute(text("SELECT * FROM registration_form"))
                df = pd.DataFrame(result.mappings().fetchall())
        except Exception as e:
            st.error(f"Export error: {e}")
            return
    else:
        data = st.session_state.get("registration_data", {})
        if data:
            df = pd.DataFrame(list(data.values()))
        else:
            st.warning("No data to export")
            return

    if not df.empty:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="nacp_registrations.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data to export")


# =============================
# MAIN APPLICATION ROUTER
# =============================
def main():
    # Sidebar for navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50.png?text=NACP+Bahamas", width=150)
        st.title("Navigation")

        if st.session_state.get("admin_logged_in"):
            st.success(f"🔓 Admin Mode")

        pages = {
            "🏠 Home": "landing",
            "📝 Registration": "registration",
            "🕒 Availability": "availability",
            "📍 Location": "location_confirmation",
            "✅ Confirmation": "final_confirmation",
            "🔐 Admin": "admin_login" if not st.session_state.get("admin_logged_in") else "admin_dashboard"
        }

        for page_name, page_key in pages.items():
            if st.button(page_name, use_container_width=True,
                         type="primary" if st.session_state.page == page_key else "secondary"):
                st.session_state.page = page_key
                st.rerun()

        st.divider()
        st.markdown("### 📊 Session Info")
        st.write(f"Database: **{db_type}**")
        if st.session_state.get("current_registration_id"):
            st.write(f"Current Reg: **#{st.session_state.current_registration_id}**")

        if st.button("🔄 Reset Session", use_container_width=True):
            reset_session()

    # Main content router
    page_handlers = {
        "landing": landing_page,
        "registration": registration_form,
        "availability": availability_form,
        "location_confirmation": location_confirmation_page,
        "final_confirmation": final_confirmation_page,
        "admin_login": admin_login,
        "admin_dashboard": admin_dashboard
    }

    current_page = st.session_state.get("page", "landing")
    handler = page_handlers.get(current_page, landing_page)
    handler()


if __name__ == "__main__":
    main()