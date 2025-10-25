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
# DATABASE CONNECTION WITH FALLBACK
# =============================
@st.cache_resource(show_spinner=False)
def get_database_connection():
    """Create database connection with multiple fallback options"""
    connection_strings = [
        # Primary connection string
        os.environ.get('DATABASE_URL'),
        # Fallback for local development
        "postgresql://postgres:postgres@localhost:5432/nacp_bahamas",
        # SQLite fallback
        "sqlite:///nacp_bahamas.db"
    ]

    for connection_string in connection_strings:
        if connection_string:
            try:
                # Handle PostgreSQL URL format for SQLAlchemy
                if connection_string.startswith('postgres://'):
                    connection_string = connection_string.replace('postgres://', 'postgresql://', 1)

                engine = create_engine(connection_string, pool_pre_ping=True)

                # Test connection
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))

                st.success(
                    f"✅ Connected to database: {connection_string.split('@')[-1] if '@' in connection_string else 'local SQLite'}")
                return engine
            except Exception as e:
                st.warning(f"⚠️ Connection failed for {connection_string}: {e}")
                continue

    st.error("❌ All database connection attempts failed. Using in-memory storage.")
    return None


# Initialize database connection
engine = get_database_connection()

# =============================
# STREAMLIT_JS_EVAL FALLBACK
# =============================
try:
    from streamlit_js_eval import get_geolocation, streamlit_js_eval

    STREAMLIT_JS_AVAILABLE = True
except ImportError:
    STREAMLIT_JS_AVAILABLE = False
    st.warning("⚠️ streamlit_js_eval not available - using fallback location methods")

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
    "gps_altitude": None,
    "address_components": {},
    "map_counter": 0,
    "last_location_check": 0,
    "formatted_cell": "",
    "formatted_tel": "",
    "high_accuracy_lat": None,
    "high_accuracy_lon": None,
    "location_source": None,
    "address_source": None,
    "show_map_first": False,
    "gps_heading": None,
    "gps_speed": None,
    "gps_timestamp": None,
    "current_island": None,
    "registration_data": {},  # In-memory storage fallback
    "current_registration_id": None,  # Track the current registration
    "database_initialized": False,  # Track if DB is properly set up
    "map_click_lat": None,  # Store map click coordinates
    "map_click_lon": None,
    "manual_coordinates": False  # Track if using manual coordinates
}.items():
    st.session_state.setdefault(key, default)


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
        # First, create the basic table structure
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

        # Now try to add the new columns in separate transactions
        additional_columns = [
            ("gps_accuracy", "DECIMAL(10, 2)"),
            ("location_source", "VARCHAR(50)")
        ]

        for column_name, column_type in additional_columns:
            try:
                with engine.begin() as conn:
                    conn.execute(
                        text(f"ALTER TABLE registration_form ADD COLUMN IF NOT EXISTS {column_name} {column_type}"))
            except Exception as column_error:
                st.warning(f"⚠️ Could not add column {column_name}: {column_error}")
                # Continue with other columns even if one fails

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
            # First try the complete insert with all columns
            with engine.begin() as conn:
                result = conn.execute(text("""
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
                """), data)

                registration_id = result.scalar()
                st.session_state.current_registration_id = registration_id
                return True

        except Exception as e:
            # If complete insert fails, try basic insert without new columns
            st.warning(f"⚠️ Standard insert failed, trying fallback: {e}")
            try:
                with engine.begin() as conn:
                    result = conn.execute(text("""
                        INSERT INTO registration_form (
                            consent, first_name, last_name, email, telephone, cell,
                            communication_methods, island, settlement, street_address,
                            interview_methods, available_days, available_times,
                            latitude, longitude
                        ) VALUES (
                            :consent, :first_name, :last_name, :email, :telephone, :cell,
                            :communication_methods, :island, :settlement, :street_address,
                            :interview_methods, :available_days, :available_times,
                            :latitude, :longitude
                        ) RETURNING id
                    """), {
                        "consent": data["consent"],
                        "first_name": data["first_name"],
                        "last_name": data["last_name"],
                        "email": data["email"],
                        "telephone": data["telephone"],
                        "cell": data["cell"],
                        "communication_methods": data["communication_methods"],
                        "island": data["island"],
                        "settlement": data["settlement"],
                        "street_address": data["street_address"],
                        "interview_methods": data["interview_methods"],
                        "available_days": data["available_days"],
                        "available_times": data["available_times"],
                        "latitude": data["latitude"],
                        "longitude": data["longitude"]
                    })

                    registration_id = result.scalar()
                    st.session_state.current_registration_id = registration_id
                    st.info("✅ Registration saved (basic fields only)")
                    return True
            except Exception as fallback_error:
                st.error(f"❌ Database save error: {fallback_error}")
                return False
    else:
        # Fallback to session state storage
        registration_id = len(st.session_state.get("registration_data", {})) + 1
        if "registration_data" not in st.session_state:
            st.session_state.registration_data = {}

        # Add ID to the data for consistency
        data['id'] = registration_id
        st.session_state.registration_data[registration_id] = data
        st.session_state.current_registration_id = registration_id
        st.warning("⚠️ Using temporary storage (database unavailable)")
        return True


def update_registration_location(registration_id, lat, lon, accuracy=None, source=None):
    """Update location data for a specific registration"""
    if engine is not None:
        try:
            # First try complete update with all columns
            with engine.begin() as conn:
                result = conn.execute(text("""
                    UPDATE registration_form 
                    SET latitude = :lat, longitude = :lon, 
                        gps_accuracy = :accuracy, location_source = :source
                    WHERE id = :id
                """), {
                    "lat": lat,
                    "lon": lon,
                    "accuracy": accuracy,
                    "source": source,
                    "id": registration_id
                })
                if result.rowcount > 0:
                    return True
                return False

        except Exception as e:
            # If complete update fails, try basic location update only
            try:
                with engine.begin() as conn:
                    result = conn.execute(text("""
                        UPDATE registration_form 
                        SET latitude = :lat, longitude = :lon
                        WHERE id = :id
                    """), {
                        "lat": lat,
                        "lon": lon,
                        "id": registration_id
                    })
                if result.rowcount > 0:
                    st.info("✅ Location saved (coordinates only)")
                    return True
                return False
            except Exception as fallback_error:
                st.error(f"❌ Location update error: {fallback_error}")
                return False
    else:
        # Update session state storage
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
                    ).mappings().fetchone()
                    return result
            except Exception as e:
                st.error(f"❌ Database read error: {e}")
                return None
        else:
            # Fallback to session state storage
            return st.session_state.get("registration_data", {}).get(registration_id)

    # Fallback: get the most recent registration
    if engine is not None:
        try:
            with engine.begin() as conn:
                result = conn.execute(
                    text("SELECT * FROM registration_form ORDER BY id DESC LIMIT 1")
                ).mappings().fetchone()
                return result
        except Exception as e:
            st.error(f"❌ Database read error: {e}")
            return None
    else:
        # Fallback to session state storage
        registration_data = st.session_state.get("registration_data", {})
        if registration_data:
            latest_id = max(registration_data.keys())
            return registration_data[latest_id]
        return None


# =============================
# ADMIN CREDENTIALS
# =============================
ADMIN_USERS = {"admin": "admin123"}

# =============================
# ISLAND-SETTLEMENT DATABASE
# =============================
ISLAND_SETTLEMENTS = {
    "New Providence": [
        "Nassau", "Cable Beach", "Paradise Island", "South Beach", "Lyford Cay",
        "Old Fort Bay", "Love Beach", "Western Esplanade", "Gambier", "Adelaide"
    ],
    "Grand Bahama": [
        "Freeport", "Lucaya", "West End", "Eight Mile Rock", "Hunter's",
        "Pinder's Point", "McLean's Town", "Sweetings Cay", "High Rock"
    ],
    "Abaco": [
        "Marsh Harbour", "Treasure Cay", "Hope Town", "Man-O-War Cay", "Great Guana Cay",
        "Cherokee Sound", "Sandy Point", "Crossing Rocks", "Green Turtle Cay", "Coopers Town"
    ],
    "Eleuthera": [
        "Governor's Harbour", "Rock Sound", "Tarpum Bay", "Palmetto Point", "Hatchet Bay",
        "Gregory Town", "James Cistern", "Current", "Wemyss Bight", "Green Castle"
    ],
    "Exuma": [
        "George Town", "Rolleville", "Mount Thompson", "Barraterre", "Black Point",
        "Staniel Cay", "Farmer's Hill", "Steventon", "Moss Town", "Williams Town"
    ],
    "Andros": [
        "Fresh Creek", "Nicholl's Town", "Staniard Creek", "Congo Town", "Mastic Point",
        "San Andros", "The Bluff", "Little Harbour", "Red Bays", "Behring Point"
    ],
    "Long Island": [
        "Clarence Town", "Deadman's Cay", "Salt Pond", "Stella Maris", "Simms",
        "Burnt Ground", "Graves", "Petty's", "Scrub Hill", "McKann's"
    ],
    "Cat Island": [
        "Arthur's Town", "The Bight", "Orange Creek", "Port Howe", "Old Bight",
        "Smith's Bay", "Knowles", "Bennet's Harbour", "McQueen's"
    ],
    "Acklins": [
        "Spring Point", "Snug Corner", "Lovely Bay", "Mason's Bay", "Salina Point",
        "Delectable Bay", "Binnacle Hill", "Crooked Settlement"
    ],
    "Crooked Island": [
        "Colonel Hill", "Landrail Point", "Cabbage Hill", "French Wells", "Bird Rock",
        "Albert Town", "Marls", "Duncan Town"
    ],
    "Bimini": [
        "Alice Town", "Bailey Town", "Porgy Bay", "North Bimini", "South Bimini"
    ],
    "Berry Islands": [
        "Great Harbour Cay", "Chub Cay", "Bullocks Harbour", "Sugar Beach", "Little Whale Cay"
    ],
    "Inagua": [
        "Matthew Town", "Main Town", "The Salt Pond", "Northeast Point"
    ],
    "Mayaguana": [
        "Abraham's Bay", "Pirate's Well", "Betsy Bay", "Upper Bay"
    ],
    "Ragged Island": [
        "Duncan Town", "Ragged Island Settlement"
    ],
    "San Salvador": [
        "Cockburn Town", "United Estates", "Sugar Loaf", "Pigeon Creek", "Bonefish Bay"
    ],
    "Rum Cay": [
        "Port Nelson", "Black Rock", "The Harbor", "Conch Shell Bay"
    ]
}

# Island center coordinates for map focusing
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
        "New Providence": 12,
        "Grand Bahama": 11,
        "Abaco": 10,
        "Eleuthera": 10,
        "Exuma": 10,
        "Andros": 9,
        "Long Island": 10,
        "Cat Island": 10,
        "Acklins": 11,
        "Crooked Island": 11,
        "Bimini": 12,
        "Berry Islands": 11,
        "Inagua": 10,
        "Mayaguana": 11,
        "Ragged Island": 12,
        "San Salvador": 11,
        "Rum Cay": 12
    }
    return zoom_levels.get(island, 10)


# =============================
# LOCATION FUNCTIONS
# =============================
def get_high_accuracy_gps_location():
    """Get precise GPS location using browser's high-accuracy geolocation"""
    if not STREAMLIT_JS_AVAILABLE:
        st.error("🚫 GPS not available in this environment. Please use a modern browser with location services enabled.")
        return False

    try:
        with st.spinner("🛰️ Accessing your device's GPS for precise location..."):
            loc_data = streamlit_js_eval(
                js_expressions="""
                new Promise((resolve, reject) => {
                    if (!navigator.geolocation) {
                        reject(new Error('Geolocation not supported'));
                        return;
                    }

                    const options = {
                        enableHighAccuracy: true,
                        timeout: 30000,
                        maximumAge: 0
                    };

                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            resolve({
                                coords: {
                                    latitude: position.coords.latitude,
                                    longitude: position.coords.longitude,
                                    accuracy: position.coords.accuracy
                                }
                            });
                        },
                        (error) => {
                            reject(new Error('Location access denied or unavailable'));
                        },
                        options
                    );
                })
                """,
                want_output=True,
                key=f"gps_request_{time.time()}"
            )

        if loc_data and "coords" in loc_data:
            lat = loc_data["coords"]["latitude"]
            lon = loc_data["coords"]["longitude"]
            accuracy = loc_data["coords"].get("accuracy", 0)

            # Update session state
            st.session_state.update({
                "latitude": lat,
                "longitude": lon,
                "gps_accuracy": accuracy,
                "location_source": "gps",
                "manual_coordinates": False
            })

            # Save location to current registration
            registration_id = st.session_state.get("current_registration_id")
            if registration_id:
                if update_registration_location(registration_id, lat, lon, accuracy, "gps"):
                    st.success(f"🎯 **Precise GPS Location Acquired and Saved!** (Accuracy: ±{accuracy:.0f}m)")
                else:
                    st.success(f"🎯 **Precise GPS Location Acquired!** (Accuracy: ±{accuracy:.0f}m)")
                    st.warning("⚠️ Location saved in session but not in database")
            else:
                st.success(f"🎯 **Precise GPS Location Acquired!** (Accuracy: ±{accuracy:.0f}m)")
                st.warning("⚠️ No active registration found to save location")

            return True
        else:
            st.error("❌ Could not access GPS coordinates. Please ensure location services are enabled.")
            return False

    except Exception as e:
        st.error(f"❌ GPS Error: {str(e)}")
        return False


def get_enhanced_ip_location():
    """Enhanced fallback method using IP geolocation"""
    try:
        st.info("🔍 Detecting approximate location...")
        resp = requests.get("https://ipapi.co/json/", timeout=10)
        data = resp.json()

        lat = data.get("latitude")
        lon = data.get("longitude")

        if lat and lon:
            # Update session state
            st.session_state.update({
                "latitude": lat,
                "longitude": lon,
                "location_source": "ip",
                "manual_coordinates": False
            })

            # Save location to current registration
            registration_id = st.session_state.get("current_registration_id")
            if registration_id:
                if update_registration_location(registration_id, lat, lon, None, "ip"):
                    st.success(f"📍 **IP Location Detected and Saved!** {lat:.6f}, {lon:.6f}")
                else:
                    st.success(f"📍 IP Location detected: {lat:.6f}, {lon:.6f}")
                    st.warning("⚠️ Location saved in session but not in database")
            else:
                st.success(f"📍 IP Location detected: {lat:.6f}, {lon:.6f}")
                st.warning("⚠️ No active registration found to save location")

            return True
        else:
            st.warning("⚠️ Unable to detect location via IP")
            return False

    except Exception as e:
        st.warning("⚠️ Unable to auto-detect location. Please enter manually.")
        return False


def get_safe_coordinates():
    """Get safe coordinate values with fallbacks"""
    default_lat = 25.0343  # Nassau
    default_lon = -77.3963

    # Use map click coordinates first, then other sources
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

    # Create interactive Folium map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_level,
        tiles='OpenStreetMap'
    )

    # Add marker for current location
    if st.session_state.get("map_click_lat") and st.session_state.get("map_click_lon"):
        # Show the clicked location
        folium.Marker(
            [st.session_state.map_click_lat, st.session_state.map_click_lon],
            popup="Selected Location",
            tooltip="Your selected location - Click to confirm",
            icon=folium.Icon(color='green', icon='ok-sign')
        ).add_to(m)
    elif st.session_state.get("latitude") and st.session_state.get("longitude"):
        # Show current detected location
        folium.Marker(
            [lat, lon],
            popup="Current Location",
            tooltip="Current detected location - Click map to change",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    # Add click handler
    m.add_child(folium.LatLngPopup())

    # Display the interactive map
    map_data = st_folium(m, width=700, height=500, key=f"interactive_map_{st.session_state.map_counter}")

    # Handle map clicks
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

    # Current coordinates display
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

    # Manual coordinate input
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

    # Clear coordinates
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
    keys_to_keep = ["registration_data", "database_initialized"]  # Keep registration data and DB status
    keys_to_reset = [key for key in st.session_state.keys() if key not in keys_to_keep]

    for key in keys_to_reset:
        st.session_state.pop(key, None)

    st.success("✅ Session reset successfully!")
    st.rerun()


# =============================
# LANDING PAGE
# =============================
def landing_page():
    st.title("🌾 NACP - National Agricultural Census Pilot Project")
    st.markdown(
        "Welcome to the **National Agricultural Census Pilot Project (NACP)** for The Bahamas.\n\n"
        "This initiative aims to collect accurate agricultural data to better serve our farming communities. "
        "Your participation helps shape the future of agriculture in The Bahamas."
    )

    # Database status
    if engine is None:
        st.warning("⚠️ Running in offline mode - data will be stored temporarily in browser")
    elif not st.session_state.get("database_initialized"):
        if st.button("🔄 Initialize Database"):
            if initialize_database():
                st.rerun()

    st.divider()

    # Quick location preview
    st.markdown("### 📍 Quick Location Setup")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎯 **Enable Location Services**", use_container_width=True, type="primary"):
            get_high_accuracy_gps_location()
            st.rerun()
    with col2:
        if st.button("🌐 **Use IP Location**", use_container_width=True):
            get_enhanced_ip_location()
            st.rerun()

    st.divider()

    # Navigation buttons
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


# =============================
# REGISTRATION FORM
# =============================
def registration_form():
    st.title("🌱 Registration Form")

    # NACP Introduction
    nscp_text = """The Government of The Bahamas, through the Ministry of Agriculture and Marine Resources and its agencies, is committed to delivering timely, relevant, and effective support to producers. However, when agricultural data and producers' needs are misaligned, the effectiveness of these efforts diminishes.

**National Agricultural Census Pilot (NACP)** is your opportunity to directly influence how agricultural data is collected, processed, and used. By participating, you help design better, more responsive processes that reflect the realities of the industry."""

    st.markdown("### ℹ️ About the NACP")
    st.text_area("Please read before providing consent:", value=nscp_text, height=200, disabled=True)

    st.divider()

    # Consent
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

    # Personal Information
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

    # Address Information
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

    # Communication Preferences
    st.markdown("### 💬 Preferred Communication Methods")
    comm_methods = ["WhatsApp", "Phone Call", "Email", "Text Message"]
    selected_methods = []
    cols = st.columns(4)
    for i, method in enumerate(comm_methods):
        with cols[i]:
            if st.checkbox(method, key=f"comm_{method}"):
                selected_methods.append(method)

    # Interview Method
    st.markdown("### 🗣️ Preferred Interview Method")
    interview_methods = ["In-person Interview", "Phone Interview", "Self Reporting"]
    interview_selected = []
    cols = st.columns(3)
    for i, method in enumerate(interview_methods):
        with cols[i]:
            if st.checkbox(method, key=f"interview_{method}"):
                interview_selected.append(method)

    st.divider()

    # Validation and Save
    col_back, col_save = st.columns([1, 2])
    with col_back:
        if st.button("← Back to Home"):
            st.session_state.page = "landing"
            st.rerun()

    with col_save:
        if st.button("💾 Save & Continue to Availability", type="primary", use_container_width=True):
            # Validation
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

            # Format phone numbers
            formatted_cell = format_phone_number(cell_raw)
            formatted_telephone = format_phone_number(telephone_raw) if telephone_raw else None

            # Prepare data for saving
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

            # Save registration data
            if save_registration_data(registration_data):
                st.success("✅ Registration information saved successfully!")
                st.session_state.page = "availability"
                st.rerun()
            else:
                st.error("❌ Failed to save registration. Please try again.")


# =============================
# AVAILABILITY FORM
# =============================
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

            # Update availability in the current registration
            registration_id = st.session_state.get("current_registration_id")
            if registration_id:
                # For database storage
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

                # Also update session state if using fallback
                if registration_id in st.session_state.get("registration_data", {}):
                    st.session_state.registration_data[registration_id]['available_days'] = selected_days
                    st.session_state.registration_data[registration_id]['available_times'] = selected_times

                st.success("✅ Availability information saved successfully!")
                st.session_state.page = "location_confirmation"
                st.rerun()
            else:
                st.error("❌ No registration found. Please start over.")


# =============================
# LOCATION CONFIRMATION PAGE
# =============================
def location_confirmation_page():
    st.title("📍 Confirm Your Location")

    st.markdown("""
    ### 🎯 Final Step: Verify Your Exact Location

    **Why precise location matters:**
    - 🎯 **Accurate agricultural data collection**
    - 📍 **Proper resource allocation to your area**
    - 🗺️ **Island-specific mapping and planning**

    **Choose your method:**
    - 🗺️ **Click on the map** below to select your exact location
    - 🎯 **Use GPS** for precise coordinates
    - 🌐 **Use IP** for approximate location
    - ✏️ **Enter manually** if you know your coordinates
    """)

    # Location acquisition methods
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎯 **GET GPS LOCATION**", use_container_width=True, type="primary"):
            get_high_accuracy_gps_location()
            st.rerun()
    with col2:
        if st.button("🌐 **USE IP LOCATION**", use_container_width=True):
            get_enhanced_ip_location()
            st.rerun()
    with col3:
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

    # Show interactive map
    show_interactive_map()

    st.divider()

    # Show coordinate controls
    show_coordinate_controls()

    st.divider()

    # Save and navigation
    col_back, col_save, col_continue = st.columns([1, 1, 1])

    with col_back:
        if st.button("← Back to Availability"):
            st.session_state.page = "availability"
            st.rerun()

    with col_save:
        if st.session_state.get("latitude") and st.session_state.get("longitude"):
            if st.button("💾 Save Location", type="primary", use_container_width=True):
                if save_current_location_to_registration():
                    st.success("✅ Location saved to your registration!")
                else:
                    st.error("❌ Failed to save location. Please try again.")
        else:
            st.button("💾 Save Location", disabled=True, use_container_width=True,
                      help="Get a location first to save")

    with col_continue:
        if st.button("✅ Continue to Confirmation", type="primary", use_container_width=True):
            # Ensure location is saved before proceeding
            if st.session_state.get("latitude") and st.session_state.get("longitude"):
                save_current_location_to_registration()
                st.session_state.page = "final_confirmation"
                st.rerun()
            else:
                st.warning("⚠️ Please set your location before continuing")


# =============================
# FINAL CONFIRMATION PAGE
# =============================
def final_confirmation_page():
    st.title("🎉 Registration Complete!")

    # SUCCESS MESSAGE
    st.success("✅ **All information saved! Thank you for completing your registration.**")

    # Show location status
    reg = get_latest_registration()
    if reg:
        if reg.get('latitude') and reg.get('longitude'):
            source = reg.get('location_source', 'manual')
            source_display = {
                'gps': '🎯 GPS',
                'ip': '🌐 IP',
                'map_click': '🗺️ Map Selection',
                'manual': '✏️ Manual Entry'
            }
            st.success(f"✅ **Location Recorded** ({source_display.get(source, 'Unknown')})")

            if source == 'gps' and reg.get('gps_accuracy'):
                st.info(f"📍 **GPS Accuracy:** ±{reg['gps_accuracy']:.0f}m")

            st.markdown(f"**Coordinates:** {reg['latitude']:.6f}, {reg['longitude']:.6f}")

            # Show mini map
            try:
                lat = float(reg['latitude'])
                lon = float(reg['longitude'])
                m = folium.Map(location=[lat, lon], zoom_start=15)
                folium.Marker([lat, lon], popup="Your Location").add_to(m)
                st.markdown("**📍 Your location on map:**")
                folium_static(m, width=400, height=300)
            except:
                pass
        else:
            st.warning("⚠️ **No Location Recorded**")

    st.markdown(
        "Your registration for the **National Agricultural Census Pilot Project (NACP)** "
        "has been successfully submitted.\n\n"
        "Our team will contact you using your preferred communication method to schedule your interview."
    )

    st.divider()

    # Display registration details
    if reg:
        st.markdown("### 📋 Your Registration Details")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Name:** {reg['first_name']} {reg['last_name']}")
            st.markdown(f"**Email:** {reg['email']}")
            st.markdown(f"**Cell:** {reg['cell']}")
            if reg.get('telephone'):
                st.markdown(f"**Alternate:** {reg['telephone']}")
            st.markdown(f"**Island:** {reg['island']}")

        with col2:
            st.markdown(f"**Settlement:** {reg['settlement']}")
            st.markdown(f"**Street:** {reg['street_address']}")
            st.markdown(f"**Communication:** {format_array_for_display(reg.get('communication_methods'))}")
            st.markdown(f"**Interview Method:** {format_array_for_display(reg.get('interview_methods'))}")

        # Availability
        available_days = format_array_for_display(reg.get('available_days'))
        available_times = format_array_for_display(reg.get('available_times'))

        st.markdown(f"**Available Days:** {available_days}")
        st.markdown(f"**Available Times:** {available_times}")

    st.divider()

    if st.button("🏠 Return to Home"):
        reset_session()
        st.session_state.page = "landing"
        st.rerun()


# =============================
# ADMIN PAGES
# =============================
def admin_login():
    st.title("🔐 Admin Login")
    username = st.text_input("Username", key="admin_user")
    password = st.text_input("Password", type="password", key="admin_pass")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Login", type="primary"):
            if username in ADMIN_USERS and password == ADMIN_USERS[username]:
                st.session_state.admin_logged_in = True
                st.session_state.page = "admin_dashboard"
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
    with col2:
        if st.button("← Back to Home"):
            st.session_state.page = "landing"
            st.rerun()


def admin_dashboard():
    if not st.session_state.get("admin_logged_in"):
        st.warning("⚠️ Please login as admin first.")
        st.session_state.page = "admin_login"
        st.rerun()
        return

    st.title("📊 NACP Admin Dashboard")

    if st.button("Logout"):
        st.session_state.admin_logged_in = False
        st.session_state.page = "landing"
        st.rerun()

    st.divider()

    if engine is None:
        st.warning("⚠️ Database unavailable - showing temporary registration data")
        reg_data = st.session_state.get("registration_data", {})
        if reg_data:
            df = pd.DataFrame.from_dict(reg_data, orient='index')
            # Show location data in admin view
            if 'latitude' in df.columns and 'longitude' in df.columns:
                st.markdown("### 📍 Location Data")
                location_df = df[
                    ['first_name', 'last_name', 'latitude', 'longitude', 'location_source', 'gps_accuracy']].copy()
                st.dataframe(location_df)
            st.dataframe(df)
        else:
            st.info("No registration data available")
    else:
        try:
            with engine.begin() as conn:
                df = pd.read_sql(text("SELECT * FROM registration_form ORDER BY id DESC"), conn)

            if not df.empty:
                # Show location data
                if 'latitude' in df.columns and 'longitude' in df.columns:
                    st.markdown("### 📍 Location Data")
                    location_df = df[
                        ['first_name', 'last_name', 'latitude', 'longitude', 'location_source', 'gps_accuracy']].copy()
                    location_df = location_df[location_df['latitude'].notna() & location_df['longitude'].notna()]
                    if not location_df.empty:
                        st.dataframe(location_df)
                    else:
                        st.info("No location data available")

                st.markdown("### 📋 All Registrations")
                st.dataframe(df)

                # Statistics
                st.markdown("### 📊 Registrations by Island")
                st.bar_chart(df["island"].value_counts())

                # Location statistics
                location_count = df[df['latitude'].notna() & df['longitude'].notna()].shape[0]
                st.markdown(f"**Registrations with Location Data:** {location_count}/{len(df)}")

            else:
                st.info("No registration data found")
        except Exception as e:
            st.error(f"Error loading data: {e}")


# =============================
# PAGE ROUTING
# =============================
page_map = {
    "landing": landing_page,
    "registration": registration_form,
    "availability": availability_form,
    "location_confirmation": location_confirmation_page,
    "final_confirmation": final_confirmation_page,
    "admin_login": admin_login,
    "admin_dashboard": admin_dashboard
}

# Execute current page
current_page = st.session_state.get("page", "landing")
page_function = page_map.get(current_page, landing_page)
page_function()