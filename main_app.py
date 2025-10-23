# main_app.py - NACP Bahamas Complete Application

import os
import streamlit as st
import pandas as pd
from sqlalchemy import text
from db import connect_with_retries, engine
from geopy.geocoders import Nominatim
import requests
import re
import pydeck as pdk
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import json
import folium
from streamlit_folium import folium_static
import math

# =============================
# RENDER DEPLOYMENT FIX
# =============================
# Render requires binding to the PORT environment variable
if 'RENDER' in os.environ:
    # This ensures the app works on Render
    port = int(os.environ.get('PORT', 10000))
    # Streamlit automatically handles port binding in newer versions
    pass

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
# DATABASE CONNECTION
# =============================
engine = connect_with_retries(retries=5, delay=3)
if engine is None:
    st.error("❌ Unable to connect to the database. Please try again later.")
    st.stop()

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
    "current_island": None
}.items():
    st.session_state.setdefault(key, default)

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

# Extended settlement database with approximate coordinates
SETTLEMENT_COORDINATES = {
    # New Providence
    "Nassau": (25.0582, -77.3450),
    "Cable Beach": (25.0794, -77.3886),
    "Paradise Island": (25.0850, -77.3200),
    "Lyford Cay": (25.0333, -77.5333),
    "Gambier": (25.0000, -77.4667),
    "Adelaide": (25.0000, -77.4833),

    # Abaco
    "Marsh Harbour": (26.5412, -77.0636),
    "Hope Town": (26.5000, -76.9833),
    "Treasure Cay": (26.6667, -77.2833),
    "Great Guana Cay": (26.6833, -77.1333),
    "Man-O-War Cay": (26.6000, -77.0167),
    "Sandy Point": (26.0167, -77.4000),
    "Coopers Town": (26.8667, -77.5167),
    "Cherokee Sound": (26.3333, -77.0333),
    "Green Turtle Cay": (26.7667, -77.3333),

    # Eleuthera
    "Governor's Harbour": (25.2000, -76.2333),
    "Rock Sound": (24.9000, -76.1667),
    "Gregory Town": (25.2167, -76.2333),
    "Tarpum Bay": (24.9833, -76.1667),
    "Hatchet Bay": (25.3500, -76.5167),
    "Current": (25.4167, -76.7833),

    # Grand Bahama
    "Freeport": (26.5333, -78.7000),
    "Lucaya": (26.5167, -78.6333),
    "West End": (26.6833, -78.9833),
    "Eight Mile Rock": (26.5500, -78.8000),

    # Exuma
    "George Town": (23.5167, -75.7833),
    "Rolleville": (23.6667, -75.9333),
    "Black Point": (24.0833, -76.4000),
    "Staniel Cay": (24.1667, -76.4333),

    # Andros
    "Fresh Creek": (24.7000, -77.8333),
    "Nicholl's Town": (25.1500, -78.0000),
    "Congo Town": (24.1667, -77.5833),

    # Long Island
    "Clarence Town": (23.1000, -74.9833),
    "Deadman's Cay": (23.1667, -75.1000),
    "Salt Pond": (23.2500, -75.1333),

    # Add more settlements as needed...
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
            # Try to parse as JSON array
            if data.startswith('[') and data.endswith(']'):
                return json.loads(data)
            # Try to parse as PostgreSQL array format
            elif data.startswith('{') and data.endswith('}'):
                return data[1:-1].split(',')
        except:
            pass

    # If all else fails, return as single item list or empty
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

    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone_str)

    # Format based on length
    if len(digits) == 7:
        return f"(242) {digits[:3]}-{digits[3:]}"
    elif len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        return digits  # Return raw digits if format doesn't match


def validate_phone_number(phone_str):
    """Validate Bahamian phone number format"""
    if not phone_str:
        return False

    digits = re.sub(r'\D', '', phone_str)

    # Bahamian numbers: 242 area code + 7 digits, or 7 digits assuming 242
    if len(digits) == 7:  # Local format without area code
        return True
    elif len(digits) == 10 and digits[:3] == '242':  # Full format with area code
        return True
    elif len(digits) == 11 and digits[0] == '1' and digits[1:4] == '242':  # International format
        return True

    return False


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in kilometers"""
    R = 6371  # Earth radius in km

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def get_island_from_settlement(settlement):
    """Map settlement to island"""
    for island, settlements in ISLAND_SETTLEMENTS.items():
        if settlement in settlements:
            return island
    return "Unknown Island"


def is_location_in_bahamas(lat, lon):
    """Validate if coordinates are within Bahamas boundaries"""
    # Bahamas approximate bounds with some buffer
    bahamas_bounds = {
        'min_lat': 20.0, 'max_lat': 27.8,
        'min_lon': -81.0, 'max_lon': -72.0
    }

    return (bahamas_bounds['min_lat'] <= lat <= bahamas_bounds['max_lat'] and
            bahamas_bounds['min_lon'] <= lon <= bahamas_bounds['max_lon'])


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
# ENHANCED GPS & LOCATION FUNCTIONS
# =============================

def get_high_accuracy_gps_location():
    """Get precise GPS location using browser's high-accuracy geolocation"""
    if not STREAMLIT_JS_AVAILABLE:
        st.error("🚫 GPS not available in this environment. Please use a modern browser with location services enabled.")
        return False

    try:
        with st.spinner("🛰️ Accessing your device's GPS for precise location..."):
            # Use high-accuracy GPS with longer timeout
            loc_data = streamlit_js_eval(
                js_expressions="""
                new Promise((resolve, reject) => {
                    if (!navigator.geolocation) {
                        reject(new Error('Geolocation not supported'));
                        return;
                    }

                    const options = {
                        enableHighAccuracy: true,  // Force GPS accuracy
                        timeout: 30000,           // 30 second timeout
                        maximumAge: 0             // No cache, fresh data
                    };

                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            resolve({
                                coords: {
                                    latitude: position.coords.latitude,
                                    longitude: position.coords.longitude,
                                    accuracy: position.coords.accuracy,
                                    altitude: position.coords.altitude,
                                    altitudeAccuracy: position.coords.altitudeAccuracy,
                                    heading: position.coords.heading,
                                    speed: position.coords.speed
                                },
                                timestamp: position.timestamp
                            });
                        },
                        (error) => {
                            let errorMsg = '';
                            switch(error.code) {
                                case error.PERMISSION_DENIED:
                                    errorMsg = 'Location access denied. Please allow location permissions.';
                                    break;
                                case error.POSITION_UNAVAILABLE:
                                    errorMsg = 'Location information unavailable.';
                                    break;
                                case error.TIMEOUT:
                                    errorMsg = 'Location request timed out.';
                                    break;
                                default:
                                    errorMsg = 'Unknown location error.';
                                    break;
                            }
                            reject(new Error(errorMsg));
                        },
                        options
                    );
                })
                """,
                want_output=True,
                key=f"gps_request_{time.time()}"  # Unique key for each request
            )

        if loc_data and "coords" in loc_data:
            lat = loc_data["coords"]["latitude"]
            lon = loc_data["coords"]["longitude"]
            accuracy = loc_data["coords"].get("accuracy", 0)

            # Validate this is actually in Bahamas
            if not is_location_in_bahamas(lat, lon):
                st.warning(
                    "📍 Location appears outside The Bahamas. Please ensure you're in The Bahamas or manually adjust your location.")
                # Still use it but warn user

            # Store high-precision data
            st.session_state.update({
                "high_accuracy_lat": lat,
                "high_accuracy_lon": lon,
                "latitude": lat,
                "longitude": lon,
                "gps_accuracy": accuracy,
                "gps_altitude": loc_data["coords"].get("altitude"),
                "gps_heading": loc_data["coords"].get("heading"),
                "gps_speed": loc_data["coords"].get("speed"),
                "gps_timestamp": loc_data.get("timestamp"),
                "location_source": "gps"
            })

            # Get precise address using multiple services
            success = get_precise_address_from_coords(lat, lon)

            if success:
                st.success(f"🎯 **Precise GPS Location Acquired!** (Accuracy: ±{accuracy:.0f}m)")
                return True
            else:
                st.warning(
                    "📍 GPS coordinates acquired but address lookup failed. You can proceed with manual address entry.")
                return True

        else:
            st.error("❌ Could not access GPS coordinates. Please ensure location services are enabled.")
            return False

    except Exception as e:
        st.error(f"❌ GPS Error: {str(e)}")
        # Fallback to IP-based location
        return get_enhanced_ip_location()


def get_precise_address_from_coords(lat, lon):
    """Get precise address using multiple geocoding services with Bahamas focus"""
    try:
        with st.spinner("🗺️ Getting precise address details..."):
            # Try multiple services in sequence
            services = [
                ("OpenStreetMap (Nominatim)", get_osm_address),
            ]

            for service_name, service_func in services:
                try:
                    st.info(f"Trying {service_name}...")
                    success = service_func(lat, lon)
                    if success:
                        return True
                except Exception as e:
                    continue

            # If all services fail, create intelligent fallback
            return create_intelligent_fallback_address(lat, lon)

    except Exception as e:
        st.warning(f"Address service temporarily unavailable: {e}")
        return create_intelligent_fallback_address(lat, lon)


def get_osm_address(lat, lon):
    """Get address from OpenStreetMap Nominatim"""
    geolocator = Nominatim(
        user_agent="nacp_bahamas_gov_v2.0",
        timeout=15
    )

    location = geolocator.reverse((lat, lon), language='en', exactly_one=True)

    if location and location.raw:
        address_data = location.raw.get('address', {})

        # Build comprehensive Bahamian address
        address_parts = []

        # Road-level details
        if address_data.get('road'):
            if address_data.get('house_number'):
                address_parts.append(f"{address_data['house_number']} {address_data['road']}")
            else:
                address_parts.append(address_data['road'])

        # Settlement level
        settlement = (address_data.get('village') or
                      address_data.get('town') or
                      address_data.get('city') or
                      address_data.get('suburb'))
        if settlement:
            address_parts.append(settlement)

        # Island level
        island = address_data.get('island') or address_data.get('state')
        if island:
            address_parts.append(island)
            st.session_state.current_island = island

        # Country
        if address_data.get('country'):
            address_parts.append(address_data['country'])

        full_address = ", ".join(address_parts)

        # Store for auto-fill
        st.session_state.update({
            "auto_full_address": full_address,
            "address_components": {
                "house_number": address_data.get('house_number', ''),
                "road": address_data.get('road', ''),
                "settlement": settlement,
                "island": island,
                "postcode": address_data.get('postcode', ''),
                "country": address_data.get('country', ''),
                "raw_address": address_data
            },
            "address_source": "osm"
        })

        return True

    return False


def create_intelligent_fallback_address(lat, lon):
    """Create intelligent address fallback using coordinate analysis"""
    # Determine closest island and settlement
    island_info = find_closest_island_settlement(lat, lon)

    if island_info:
        island, settlement, distance_km = island_info
        address = f"Near {settlement}, {island}, The Bahamas"

        st.session_state.update({
            "auto_full_address": address,
            "address_components": {
                "settlement": settlement,
                "island": island,
                "approximate_distance_km": distance_km,
                "coordinates": f"{lat:.6f}, {lon:.6f}",
                "country": "The Bahamas"
            },
            "address_source": "coordinate_analysis",
            "current_island": island
        })

        st.info(f"📍 Approximate location: {address} (within ~{distance_km:.1f}km)")
        return True

    return False


def find_closest_island_settlement(lat, lon):
    """Find the closest known settlement using comprehensive Bahamian data"""
    closest_settlement = None
    min_distance = float('inf')

    for settlement, (settle_lat, settle_lon) in SETTLEMENT_COORDINATES.items():
        distance = haversine_distance(lat, lon, settle_lat, settle_lon)
        if distance < min_distance:
            min_distance = distance
            closest_settlement = settlement

    # Determine island from settlement
    island = get_island_from_settlement(closest_settlement)

    return (island, closest_settlement, min_distance) if closest_settlement else None


def get_enhanced_ip_location():
    """Enhanced fallback method using multiple IP geolocation services"""
    services = [
        "https://ipapi.co/json/",
        "https://ipinfo.io/json",
        "http://ip-api.com/json/"
    ]

    for service in services:
        try:
            st.info(f"🔍 Trying location service: {service.split('//')[1].split('/')[0]}")
            resp = requests.get(service, timeout=10)
            data = resp.json()

            lat, lon, city, region, country = None, None, "", "", ""

            if "ipapi.co" in service:
                lat = data.get("latitude")
                lon = data.get("longitude")
                city = data.get("city", "")
                region = data.get("region", "")
                country = data.get("country_name", "")

            elif "ipinfo.io" in service:
                loc = data.get("loc")
                if loc and "," in loc:
                    lat, lon = map(float, loc.split(","))
                city = data.get("city", "")
                region = data.get("region", "")
                country = data.get("country", "")

            elif "ip-api.com" in service:
                if data.get("status") == "success":
                    lat = data.get("lat")
                    lon = data.get("lon")
                    city = data.get("city", "")
                    region = data.get("regionName", "")
                    country = data.get("country", "")

            # Validate coordinates (rough Bahamas bounds)
            if lat and lon:
                st.session_state.update({
                    "auto_lat": lat,
                    "auto_lon": lon,
                    "latitude": lat,
                    "longitude": lon,
                    "last_location_check": time.time(),
                    "location_source": "ip"
                })

                # Get detailed address
                get_precise_address_from_coords(lat, lon)

                st.success(f"📍 IP Location detected: {lat:.6f}, {lon:.6f}")
                if city:
                    st.info(f"🌍 Approximate Area: {city}, {region}, {country}")
                return True

        except Exception as e:
            continue

    st.warning("⚠️ Unable to auto-detect location within Bahamas. Please enter manually.")
    return False


def safe_coordinate_format(coord, default_value=0.0):
    """Safely format coordinate values, handling None and invalid types"""
    if coord is None:
        return f"{default_value:.6f}"

    try:
        coord_float = float(coord)
        return f"{coord_float:.6f}"
    except (TypeError, ValueError):
        return f"{default_value:.6f}"


def get_safe_coordinates():
    """Get safe coordinate values with fallbacks"""
    # Fallback coordinates (Nassau, Bahamas as example)
    default_lat = 25.0343
    default_lon = -77.3963

    lat = (st.session_state.get("high_accuracy_lat") or
           st.session_state.get("auto_lat") or
           st.session_state.get("latitude") or
           default_lat)

    lon = (st.session_state.get("high_accuracy_lon") or
           st.session_state.get("auto_lon") or
           st.session_state.get("longitude") or
           default_lon)

    # Ensure they are floats
    try:
        lat = float(lat)
    except (TypeError, ValueError):
        lat = default_lat

    try:
        lon = float(lon)
    except (TypeError, ValueError):
        lon = default_lon

    return lat, lon


def auto_refresh_location():
    """Auto-refresh location if it's older than 30 seconds"""
    last_check = st.session_state.get("last_location_check", 0)
    current_time = time.time()

    if current_time - last_check > 30:  # Refresh every 30 seconds
        if st.session_state.get("auto_lat"):
            st.info("🔄 Refreshing location data...")
            get_precise_address_from_coords(
                st.session_state["auto_lat"],
                st.session_state["auto_lon"]
            )
            st.session_state["last_location_check"] = current_time


def show_island_focused_map():
    """Display a map focused on the specific island with user's location"""

    lat, lon = get_safe_coordinates()

    # Determine which island to focus on
    current_island = st.session_state.get("current_island")
    if current_island and current_island in ISLAND_CENTERS:
        # Use island-specific center and zoom
        center_lat, center_lon = ISLAND_CENTERS[current_island]
        zoom_level = get_island_zoom_level(current_island)
        map_title = f"🗺️ Map of {current_island}"
    else:
        # Fallback to user's coordinates
        center_lat, center_lon = lat, lon
        zoom_level = 15
        map_title = "🗺️ Your Location"

    st.markdown(f"### {map_title}")

    # Map controls
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🎯 Get GPS Location", use_container_width=True):
            get_high_accuracy_gps_location()
            st.rerun()

    with col2:
        map_style = st.selectbox(
            "Map Style",
            ["satellite", "streets", "light", "dark", "outdoors"],
            key="island_map_style"
        )

    # Create Folium map focused on the island
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_level,
        tiles='OpenStreetMap'
    )

    # Add marker for user's location
    folium.Marker(
        [lat, lon],
        popup="Your Location",
        tooltip="Click for details",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

    # Add circle for accuracy if available
    if st.session_state.get("gps_accuracy"):
        accuracy = st.session_state.gps_accuracy
        folium.Circle(
            location=[lat, lon],
            radius=accuracy,
            color='blue',
            fill=True,
            fillOpacity=0.2,
            popup=f"GPS Accuracy: ±{accuracy:.0f}m"
        ).add_to(m)

    # Display the map
    folium_static(m, width=700, height=500)

    # Show location details below the map
    display_current_address(lat, lon)


def display_current_address(lat, lon):
    """Display and auto-update the current address information"""
    st.markdown("#### 📍 Location Details")

    # Create a nice info box for coordinates
    col_coord1, col_coord2, col_accuracy = st.columns([1, 1, 1])

    with col_coord1:
        st.metric("Latitude", f"{lat:.6f}")

    with col_coord2:
        st.metric("Longitude", f"{lon:.6f}")

    with col_accuracy:
        accuracy = st.session_state.get("gps_accuracy", "Unknown")
        if isinstance(accuracy, (int, float)):
            st.metric("Accuracy", f"±{accuracy:.0f}m")
        else:
            st.metric("Accuracy", "Unknown")

    # Display the address in a prominent way
    if "auto_full_address" in st.session_state and st.session_state["auto_full_address"]:
        address = st.session_state["auto_full_address"]

        # Style the address display
        st.markdown("**📬 Detected Address:**")
        st.info(f"**{address}**")

    else:
        st.warning("📍 No address detected. Use GPS or enter manually below.")

        # Quick manual address entry
        with st.expander("🔧 Enter Address Manually", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                manual_road = st.text_input("Street/Road Name", key="manual_road")
                manual_settlement = st.text_input("Settlement/Area", key="manual_settlement")
            with col2:
                manual_island = st.selectbox("Island", list(ISLAND_SETTLEMENTS.keys()), key="manual_island")

            if st.button("✅ Use This Address", key="use_manual_address"):
                if manual_road and manual_settlement:
                    manual_address = f"{manual_road}, {manual_settlement}, {manual_island}, The Bahamas"
                    st.session_state["auto_full_address"] = manual_address
                    st.session_state["address_components"] = {
                        "road": manual_road,
                        "city": manual_settlement,
                        "island": manual_island,
                        "country": "The Bahamas"
                    }
                    st.session_state.current_island = manual_island
                    st.success("✅ Manual address saved!")
                    st.rerun()
                else:
                    st.error("Please enter at least street and settlement information.")

    # Manual coordinate adjustment
    with st.expander("🎯 Adjust Coordinates Manually", expanded=False):
        col_lat, col_lon, col_btn = st.columns([2, 2, 1])
        with col_lat:
            new_lat = st.number_input("Latitude", value=float(lat), format="%.6f", step=0.0001, key="manual_lat")
        with col_lon:
            new_lon = st.number_input("Longitude", value=float(lon), format="%.6f", step=0.0001, key="manual_lon")
        with col_btn:
            st.write("")
            st.write("")
            if st.button("🔄 Update", key="update_coords", use_container_width=True):
                st.session_state.latitude = new_lat
                st.session_state.longitude = new_lon
                get_precise_address_from_coords(new_lat, new_lon)
                st.success("📍 Location updated!")
                st.rerun()


# =============================
# RESET SESSION FUNCTION
# =============================
def reset_session():
    """Clear all session state data"""
    keys_to_reset = [
        "latitude", "longitude", "auto_lat", "auto_lon",
        "auto_island", "auto_settlement", "auto_street",
        "auto_full_address", "auto_postcode", "auto_country",
        "first_name", "last_name", "email", "telephone", "cell",
        "selected_methods", "island_selected", "settlement_selected",
        "street_address", "selected_days", "selected_times",
        "consent_bool", "gps_accuracy", "gps_altitude",
        "last_location_check", "formatted_cell", "formatted_tel",
        "high_accuracy_lat", "high_accuracy_lon", "location_source",
        "address_source", "show_map_first", "gps_heading",
        "gps_speed", "gps_timestamp", "current_island"
    ]
    for key in keys_to_reset:
        st.session_state.pop(key, None)
    st.success("✅ Session reset successfully!")
    st.rerun()


# =============================
# LANDING PAGE (NO MAP)
# =============================
def landing_page():
    st.title("🌾 NACP - National Agricultural Census Pilot Project")
    st.markdown(
        "Welcome to the **National Agricultural Census Pilot Project (NACP)** for The Bahamas.\n\n"
        "This initiative aims to collect accurate agricultural data to better serve our farming communities. "
        "Your participation helps shape the future of agriculture in The Bahamas."
    )

    st.divider()

    # Quick location preview (no map)
    st.markdown("### 📍 Quick Location Setup")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎯 **Enable Location Services**", use_container_width=True, type="primary"):
            with st.spinner("Checking location services..."):
                if get_high_accuracy_gps_location():
                    st.success("Location services ready!")
                else:
                    st.info("Location will be collected in the final step")
            st.rerun()

    with col2:
        if st.button("🌐 **Use IP Location**", use_container_width=True):
            with st.spinner("Detecting approximate location..."):
                get_enhanced_ip_location()
            st.rerun()

    # Show current location status if available
    if st.session_state.get("auto_full_address"):
        st.info(f"📍 **Current Location:** {st.session_state['auto_full_address']}")
    else:
        st.info("📍 **Location services** will be used in the final step to verify your exact location.")

    st.divider()

    # Benefits section
    st.markdown("### 🌟 Why Participate?")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **📊 Accurate Data**  
        Help collect precise agricultural information for better planning and resource allocation.
        """)

    with col2:
        st.markdown("""
        **🏝️ Island-Specific**  
        Location-based data collection ensures resources reach the right communities.
        """)

    with col3:
        st.markdown("""
        **🤝 Community Impact**  
        Your input directly influences agricultural policies and support programs.
        """)

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

**National Agricultural Census Pilot (NACP)** is your opportunity to directly influence how agricultural data is collected, processed, and used. By participating, you help design better, more responsive processes that reflect the realities of the industry.

**Why Join the NACP Pre-Test Programme?**  
As a producer or holder in The Bahamas, your participation ensures that data collection and reporting are tailored to the industry's actual needs. Your input will directly shape the future of agricultural statistics in the country.

**Key Points of Focus:**  
1. Aligning data collection activities with industry needs.  
2. Meeting reporting requirements efficiently.  
3. Working within cost limitations while maximizing impact.  
4. Using the best methods to obtain high-quality, usable data consistently over time, until context-driven changes are necessary."""

    st.markdown("### ℹ️ About the NACP")
    st.text_area("Please read before providing consent:", value=nscp_text, height=300, disabled=True)

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
        # Primary contact - Cell Number
        cell_raw = st.text_input("Cell Number (Primary Contact) *",
                                 key="reg_cell",
                                 placeholder="e.g., 2424567890 or 4567890",
                                 help="Enter 7 digits for local number or include area code")

        # Format the cell number in real-time
        if cell_raw:
            formatted_cell = format_phone_number(cell_raw)
            if formatted_cell != cell_raw:
                st.session_state.formatted_cell = formatted_cell
                st.info(f"Formatted: {formatted_cell}")

        # Alternate contact - Telephone (optional)
        telephone_raw = st.text_input("Alternate Number (Optional)",
                                      key="reg_tel",
                                      placeholder="e.g., 2424567890",
                                      help="Optional landline or alternate number")

        # Format telephone in real-time
        if telephone_raw:
            formatted_tel = format_phone_number(telephone_raw)
            if formatted_tel != telephone_raw:
                st.session_state.formatted_tel = formatted_tel
                st.info(f"Formatted: {formatted_tel}")

    # Address Information
    st.markdown("### 📍 Address Information")

    # Auto-populate from GPS if available
    island_default = ""
    settlement_default = ""
    street_default = ""

    if "address_components" in st.session_state:
        components = st.session_state["address_components"]
        if components.get("city"):
            settlement_default = components["city"]
        elif components.get("island"):
            settlement_default = components["island"]
        if components.get("road"):
            street_default = components["road"]

    col1, col2 = st.columns(2)
    with col1:
        # Island selection with GPS hint
        if "address_components" in st.session_state and st.session_state["address_components"].get("island"):
            gps_island = st.session_state["address_components"]["island"]
            island_selected = st.selectbox(
                "Island *",
                list(ISLAND_SETTLEMENTS.keys()),
                index=list(ISLAND_SETTLEMENTS.keys()).index(gps_island) if gps_island in ISLAND_SETTLEMENTS else 0,
                key="reg_island",
                help=f"GPS detected: {gps_island}"
            )
        else:
            island_selected = st.selectbox(
                "Island *",
                list(ISLAND_SETTLEMENTS.keys()),
                key="reg_island",
                help="Select your island"
            )

        # Dynamic settlement dropdown based on island selection
        settlements = ISLAND_SETTLEMENTS.get(island_selected, [])

        if settlements:
            # Try to pre-select based on GPS data
            default_index = 0
            if settlement_default:
                for i, settlement in enumerate(settlements):
                    if settlement_default.lower() in settlement.lower() or settlement.lower() in settlement_default.lower():
                        default_index = i
                        break

            settlement_selected = st.selectbox(
                "Settlement/District *",
                settlements,
                index=default_index,
                key="reg_settlement",
                help="Select from predefined settlements for your island"
            )
        else:
            settlement_selected = st.text_input(
                "Settlement/District *",
                value=settlement_default,
                key="reg_settlement",
                help="Enter your settlement name"
            )

    with col2:
        street_address = st.text_input(
            "Street Address *",
            value=street_default,
            key="reg_street",
            placeholder="e.g., 123 Main Street, Coral Harbour, Near the school",
            help="Full street address, road name, or area description"
        )

        # Quick address helper
        if st.session_state.get("auto_full_address"):
            st.caption(f"💡 GPS detected: {st.session_state['auto_full_address']}")

        # "Other" settlement option
        if settlements and st.checkbox("My settlement is not in the list", key="other_settlement"):
            settlement_selected = st.text_input(
                "Enter Settlement Name *",
                value=settlement_default,
                key="custom_settlement",
                help="Please provide the correct name of your settlement"
            )

        # Location notice
        st.info("📍 **Precise location** will be verified in the final step using GPS.")

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

    # Validation
    email_valid = True
    cell_valid = True
    telephone_valid = True

    if email and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,4}$", email):
        st.warning("⚠️ Invalid email format.")
        email_valid = False

    # Validate cell number (required)
    if not cell_raw:
        st.warning("⚠️ Cell number is required as primary contact.")
        cell_valid = False
    elif not validate_phone_number(cell_raw):
        st.warning("⚠️ Please enter a valid Bahamian cell number (7 or 10 digits).")
        cell_valid = False

    # Validate telephone (optional but must be valid if provided)
    if telephone_raw and not validate_phone_number(telephone_raw):
        st.warning("⚠️ Please enter a valid telephone number (7 or 10 digits).")
        telephone_valid = False

    # Save button
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

            if not email_valid or not cell_valid or not telephone_valid:
                st.error("⚠️ Please fix validation errors above.")
                return

            if not selected_methods:
                st.error("⚠️ Please select at least one communication method.")
                return

            if not interview_selected:
                st.error("⚠️ Please select at least one interview method.")
                return

            # Format phone numbers before saving
            formatted_cell = format_phone_number(cell_raw)
            formatted_telephone = format_phone_number(telephone_raw) if telephone_raw else None

            # Convert lists to PostgreSQL array literals
            communication_methods = "{" + ",".join(selected_methods) + "}"
            interview_methods = "{" + ",".join(interview_selected) + "}"

            # Save to database
            try:
                with engine.begin() as conn:
                    conn.execute(text("""
                        INSERT INTO registration_form (
                            consent, first_name, last_name, email, telephone, cell,
                            communication_methods, island, settlement, street_address,
                            interview_methods
                        ) VALUES (
                            :consent, :first_name, :last_name, :email, :telephone, :cell,
                            :communication_methods, :island, :settlement, :street_address,
                            :interview_methods
                        )
                    """), {
                        "consent": st.session_state["consent_bool"],
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "telephone": formatted_telephone,
                        "cell": formatted_cell,
                        "communication_methods": communication_methods,
                        "island": island_selected,
                        "settlement": settlement_selected,
                        "street_address": street_address,
                        "interview_methods": interview_methods
                    })
                st.success("✅ Registration saved successfully!")
                st.session_state.page = "availability"
                st.rerun()
            except Exception as e:
                st.error(f"❌ Database error: {e}")


# =============================
# AVAILABILITY FORM
# =============================
def availability_form():
    st.title("🕒 Availability Preferences")
    st.markdown("Please select your preferred days and times for the agricultural census interview.")

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

    # Columns for buttons
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

            try:
                with engine.begin() as conn:
                    conn.execute(text("""
                        UPDATE registration_form
                        SET available_days=:days, available_times=:times
                        WHERE id=(SELECT max(id) FROM registration_form)
                    """), {"days": selected_days, "times": selected_times})

                st.success("✅ Availability saved! Now let's get your precise location.")
                st.session_state.page = "location_confirmation"
                st.rerun()
            except Exception as e:
                st.error(f"❌ Database error: {e}")


# =============================
# LOCATION CONFIRMATION PAGE (WITH MAP)
# =============================
def location_confirmation_page():
    st.title("📍 Confirm Your Location")

    st.markdown("""
    ### 🎯 Final Step: Verify Your Exact Location

    **Why precise location matters:**
    - 🎯 **Accurate agricultural data collection**
    - 📍 **Proper resource allocation to your area**
    - 🗺️ **Island-specific mapping and planning**
    - 🌾 **Localized agricultural support**

    **For best results:**
    - 📱 Use a **smartphone** with GPS capability
    - 📍 **Allow location access** when browser prompts
    - 🌤️ Be **outdoors** or near windows for better GPS signal
    - 🔄 Wait for GPS to achieve **high accuracy** (±10-20m)
    """)

    # High-accuracy GPS button
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🎯 **GET PRECISE GPS LOCATION**",
                     type="primary",
                     use_container_width=True,
                     help="Uses your device's actual GPS hardware for pinpoint accuracy"):
            with st.spinner("🛰️ Accessing GPS satellite data..."):
                if get_high_accuracy_gps_location():
                    st.success("✅ Precise GPS location acquired!")
                    st.balloons()
                    # Auto-proceed to confirmation after short delay
                    time.sleep(2)
                    st.session_state.page = "final_confirmation"
                    st.rerun()

    with col2:
        if st.button("🌐 Use IP Location", use_container_width=True):
            with st.spinner("Getting approximate location..."):
                get_enhanced_ip_location()
            st.rerun()

    st.divider()

    # SHOW THE MAP - Only appears in this final step
    show_island_focused_map()

    st.divider()

    # Navigation
    col_back, col_skip = st.columns(2)
    with col_back:
        if st.button("← Back to Availability"):
            st.session_state.page = "availability"
            st.rerun()
    with col_skip:
        if st.button("⏭️ Skip Location (Not Recommended)", use_container_width=True):
            st.warning("""
            ⚠️ **Agricultural data accuracy may be affected**

            Precise location is crucial for:
            - Proper resource allocation
            - Accurate agricultural planning  
            - Island-specific support programs
            """)
            if st.checkbox("I understand the implications"):
                st.session_state.page = "final_confirmation"
                st.rerun()


# =============================
# FINAL CONFIRMATION PAGE
# =============================
def final_confirmation_page():
    st.title("🎉 Registration Complete!")

    # Show location status prominently
    if st.session_state.get("location_source") == "gps":
        st.success("✅ **Precise GPS Location Recorded**")
        if st.session_state.get("gps_accuracy"):
            st.info(f"📍 **GPS Accuracy:** ±{st.session_state['gps_accuracy']:.0f}m")
    elif st.session_state.get("auto_full_address"):
        st.info("📍 **Approximate Location Recorded**")
    else:
        st.warning("⚠️ **No Location Recorded** - Agricultural data may be less accurate")

    st.markdown(
        "Your registration for the **National Agricultural Census Pilot Project (NACP)** "
        "has been successfully submitted.\n\n"
        "Our team will contact you using your preferred communication method to schedule your interview."
    )

    st.divider()

    # Enhanced registration details with location info
    try:
        with engine.begin() as conn:
            # First update the record with location data if available
            if st.session_state.get("latitude") and st.session_state.get("longitude"):
                conn.execute(text("""
                    UPDATE registration_form 
                    SET latitude=:lat, longitude=:lon 
                    WHERE id=(SELECT max(id) FROM registration_form)
                """), {
                    "lat": st.session_state.get("latitude"),
                    "lon": st.session_state.get("longitude")
                })

            reg = conn.execute(
                text("SELECT * FROM registration_form ORDER BY id DESC LIMIT 1")
            ).mappings().fetchone()

            if reg:
                st.markdown("### 📋 Your Registration Details")
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Name:** {reg['first_name']} {reg['last_name']}")
                    st.markdown(f"**Email:** {reg['email']}")
                    st.markdown(f"**Cell:** {reg['cell']}")
                    if reg['telephone']:
                        st.markdown(f"**Alternate:** {reg['telephone']}")
                    st.markdown(f"**Island:** {reg['island']}")

                with col2:
                    st.markdown(f"**Settlement:** {reg['settlement']}")
                    st.markdown(f"**Street:** {reg['street_address']}")

                    # Location accuracy info
                    if reg.get('latitude') and reg.get('longitude'):
                        accuracy_info = ""
                        if st.session_state.get("gps_accuracy"):
                            accuracy_info = f" (Accuracy: ±{st.session_state['gps_accuracy']:.0f}m)"
                        st.markdown(
                            f"**Location Coordinates:** {reg['latitude']:.6f}, {reg['longitude']:.6f}{accuracy_info}")

                    st.markdown(f"**Communication:** {format_array_for_display(reg.get('communication_methods'))}")
                    st.markdown(f"**Interview Method:** {format_array_for_display(reg.get('interview_methods'))}")

                # Availability
                available_days = format_array_for_display(reg.get('available_days'))
                available_times = format_array_for_display(reg.get('available_times'))

                st.markdown(f"**Available Days:** {available_days}")
                st.markdown(f"**Available Times:** {available_times}")

            else:
                st.warning("No registration found.")

    except Exception as e:
        st.error(f"Error retrieving registration: {e}")

    st.divider()

    if st.button("🏠 Return to Home"):
        reset_session()
        st.session_state.page = "landing"
        st.rerun()


# =============================
# ADMIN LOGIN
# =============================
def admin_login():
    st.title("🔐 Admin Login")
    st.markdown("Please enter your admin credentials to access the dashboard.")

    username = st.text_input("Username", key="admin_user")
    password = st.text_input("Password", type="password", key="admin_pass")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Login", type="primary"):
            if username in ADMIN_USERS and password == ADMIN_USERS[username]:
                st.success("✅ Login successful!")
                st.session_state.admin_logged_in = True
                st.session_state.page = "admin_dashboard"
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

    with col2:
        if st.button("← Back to Home"):
            st.session_state.page = "landing"
            st.rerun()


# =============================
# ADMIN DASHBOARD
# =============================
def admin_dashboard():
    if not st.session_state.get("admin_logged_in"):
        st.warning("⚠️ Please login as admin first.")
        st.session_state.page = "admin_login"
        st.rerun()
        return

    st.title("📊 NACP Admin Dashboard")

    col_logout, col_home = st.columns([1, 5])
    with col_logout:
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.session_state.page = "landing"
            st.rerun()

    st.divider()

    TABLES = ["registration_form"]
    rows_per_page = 20

    for table_name in TABLES:
        st.subheader(f"📄 {table_name.replace('_', ' ').title()} Data")

        try:
            with engine.begin() as conn:
                df = pd.read_sql(text(f"SELECT * FROM {table_name} ORDER BY id DESC"), conn)

            if df.empty:
                st.info("No data found.")
                continue

            # Pagination
            page_key = f"{table_name}_page"
            st.session_state.setdefault(page_key, 0)
            page = st.session_state[page_key]
            total_pages = max(1, (len(df) - 1) // rows_per_page + 1)

            start_idx = page * rows_per_page
            end_idx = start_idx + rows_per_page
            df_page = df.iloc[start_idx:end_idx].copy()

            # Add delete column
            df_page.insert(0, "Delete", False)

            # Data editor
            edited_df = st.data_editor(
                df_page,
                column_config={
                    "Delete": st.column_config.CheckboxColumn("Delete", help="Tick to delete row"),
                    "id": st.column_config.NumberColumn("ID", disabled=True)
                },
                use_container_width=True,
                key=f"editor_{table_name}_{page}"
            )

            # Delete confirmation
            if edited_df["Delete"].any():
                st.warning(f"⚠️ You have selected {edited_df['Delete'].sum()} row(s) to delete.")
                if st.button(f"✅ Confirm Delete Selected from {table_name}", type="primary"):
                    rows_to_delete = edited_df[edited_df["Delete"]]
                    with engine.begin() as conn:
                        for rid in rows_to_delete["id"]:
                            conn.execute(text(f"DELETE FROM {table_name} WHERE id=:id"), {"id": rid})
                    st.success(f"✅ Deleted {len(rows_to_delete)} record(s).")
                    st.rerun()

            # Pagination controls
            col_prev, col_info, col_next = st.columns([1, 2, 1])
            with col_prev:
                if st.button("⬅️ Previous", disabled=(page == 0)):
                    st.session_state[page_key] -= 1
                    st.rerun()
            with col_info:
                st.markdown(f"<center>Page {page + 1} of {total_pages}</center>", unsafe_allow_html=True)
            with col_next:
                if st.button("Next ➡️", disabled=(page >= total_pages - 1)):
                    st.session_state[page_key] += 1
                    st.rerun()

            # Statistics
            if "island" in df.columns:
                st.markdown("### 📊 Registrations by Island")
                st.bar_chart(df["island"].value_counts())

        except Exception as e:
            st.error(f"Error loading data: {e}")

        st.markdown("---")


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