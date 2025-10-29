# main_app.py - NACP Bahamas Complete Application

import streamlit as st
import pandas as pd
from sqlalchemy import text
from db import connect_with_retries, engine
from geopy.geocoders import Nominatim
import requests
import re
import pydeck as pdk
from streamlit_js_eval import get_geolocation, streamlit_js_eval
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import json

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
    "last_location_check": 0
}.items():
    st.session_state.setdefault(key, default)

# =============================
# ADMIN CREDENTIALS
# =============================
ADMIN_USERS = {"admin": "admin123"}


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


# =============================
# ENHANCED GPS & LOCATION FUNCTIONS
# =============================

def get_browser_location():
    """Get high-accuracy GPS location from browser using HTML5 Geolocation API"""
    try:
        st.info("📍 Requesting GPS access from your browser...")

        # Use streamlit_js_eval for better geolocation
        loc_data = streamlit_js_eval(
            js_expressions="""
            new Promise((resolve) => {
                if (!navigator.geolocation) {
                    resolve(null);
                } else {
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            resolve({
                                coords: {
                                    latitude: position.coords.latitude,
                                    longitude: position.coords.longitude,
                                    accuracy: position.coords.accuracy,
                                    altitude: position.coords.altitude
                                }
                            });
                        },
                        (error) => {
                            resolve(null);
                        },
                        {
                            enableHighAccuracy: true,
                            timeout: 15000,
                            maximumAge: 0
                        }
                    );
                }
            })
            """,
            want_output=True
        )

        if loc_data and "coords" in loc_data:
            lat = loc_data["coords"]["latitude"]
            lon = loc_data["coords"]["longitude"]
            accuracy = loc_data["coords"].get("accuracy", "Unknown")
            altitude = loc_data["coords"].get("altitude", "N/A")

            # Store in session state
            st.session_state["auto_lat"] = lat
            st.session_state["auto_lon"] = lon
            st.session_state["latitude"] = lat
            st.session_state["longitude"] = lon
            st.session_state["gps_accuracy"] = accuracy
            st.session_state["gps_altitude"] = altitude
            st.session_state["last_location_check"] = time.time()

            # Get detailed street address from coordinates
            get_detailed_address_from_coords(lat, lon)

            st.success(f"✅ **GPS Location Acquired!**")
            st.info(f"📍 Coordinates: `{lat:.6f}, {lon:.6f}`\n"
                    f"🎯 Accuracy: ±{accuracy:.0f}m\n"
                    f"⛰️ Altitude: {altitude}m")
            return True
        else:
            st.warning("⚠️ Could not access GPS. Falling back to IP-based location...")
            return get_enhanced_ip_location()

    except Exception as e:
        st.error(f"❌ Browser GPS Error: {e}")
        return get_enhanced_ip_location()


def get_enhanced_ip_location():
    """Enhanced fallback method using multiple IP geolocation services"""
    services = [
        "https://ipinfo.io/json",
        "https://ipapi.co/json/",
        "http://ip-api.com/json/"
    ]

    lat, lon, city, region, country = None, None, "", "", ""

    for service in services:
        try:
            st.info(f"🔍 Trying location service: {service.split('//')[1].split('/')[0]}")
            resp = requests.get(service, timeout=5)
            data = resp.json()

            if "ipinfo.io" in service:
                loc = data.get("loc")
                if loc:
                    lat, lon = map(float, loc.split(","))
                    city = data.get("city", "")
                    region = data.get("region", "")
                    country = data.get("country", "")
                    break
            elif "ipapi.co" in service:
                lat = data.get("latitude")
                lon = data.get("longitude")
                city = data.get("city", "")
                region = data.get("region", "")
                country = data.get("country_name", "")
                if lat and lon:
                    break
            elif "ip-api.com" in service:
                lat = data.get("lat")
                lon = data.get("lon")
                city = data.get("city", "")
                region = data.get("region", "")
                country = data.get("country", "")
                if lat and lon:
                    break
        except:
            continue

    if lat and lon:
        st.session_state["auto_lat"] = lat
        st.session_state["auto_lon"] = lon
        st.session_state["latitude"] = lat
        st.session_state["longitude"] = lon
        st.session_state["last_location_check"] = time.time()

        # Get detailed address
        get_detailed_address_from_coords(lat, lon)

        st.success(f"📍 IP Location detected: {lat:.6f}, {lon:.6f}")
        if city:
            st.info(f"🌍 Approximate Area: {city}, {region}, {country}")
        st.warning("💡 For better accuracy, allow GPS access when prompted.")
        return True

    st.warning("⚠️ Unable to auto-detect location. Please enter manually.")
    return False


def get_detailed_address_from_coords(lat, lon):
    """Get comprehensive address information using multiple geocoding services"""
    try:
        # Show loading state
        with st.spinner("🔄 Getting address details..."):
            # Try Nominatim first (OpenStreetMap)
            geolocator = Nominatim(user_agent="nacp_bahamas_app_v1.0")
            location = geolocator.reverse((lat, lon), language='en', exactly_one=True, timeout=10)

            if location and location.raw:
                address_data = location.raw.get('address', {})

                # Build comprehensive address
                address_parts = []

                # House number and street
                if address_data.get('house_number') and address_data.get('road'):
                    address_parts.append(f"{address_data['house_number']} {address_data['road']}")
                elif address_data.get('road'):
                    address_parts.append(address_data['road'])

                # Neighborhood
                if address_data.get('suburb'):
                    address_parts.append(address_data['suburb'])

                # City/town/village
                city = address_data.get('city') or address_data.get('town') or address_data.get('village')
                if city:
                    address_parts.append(city)

                # State and postcode
                if address_data.get('state'):
                    address_parts.append(address_data['state'])
                if address_data.get('postcode'):
                    address_parts.append(address_data['postcode'])

                # Country
                if address_data.get('country'):
                    address_parts.append(address_data['country'])

                full_address = ", ".join(address_parts)

                # Store detailed address components
                st.session_state["auto_full_address"] = full_address
                st.session_state["address_components"] = {
                    "house_number": address_data.get('house_number', ''),
                    "road": address_data.get('road', ''),
                    "neighborhood": address_data.get('suburb', ''),
                    "city": city,
                    "state": address_data.get('state', ''),
                    "postcode": address_data.get('postcode', ''),
                    "country": address_data.get('country', ''),
                    "country_code": address_data.get('country_code', '')
                }
                return True

    except (GeocoderTimedOut, GeocoderServiceError) as e:
        st.warning(f"⚠️ Geocoding service slow, using fallback: {e}")
    except Exception as e:
        st.warning(f"⚠️ Address lookup failed: {e}")

    # Fallback: Simple coordinates-based address
    st.session_state["auto_full_address"] = f"Near {lat:.6f}, {lon:.6f}"
    st.session_state["address_components"] = {
        "coordinates": f"{lat:.6f}, {lon:.6f}"
    }
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

    lat = (st.session_state.get("auto_lat") or
           st.session_state.get("latitude") or
           default_lat)

    lon = (st.session_state.get("auto_lon") or
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
        if st.session_state.get("auto_lat") and st.session_state.get("auto_lon"):
            st.info("🔄 Refreshing location data...")
            get_detailed_address_from_coords(
                st.session_state["auto_lat"],
                st.session_state["auto_lon"]
            )
            st.session_state["last_location_check"] = current_time


def show_enhanced_readable_map():
    """Display enhanced, readable interactive map with auto-updating address"""

    # Get safe coordinates with proper fallbacks
    lat, lon = get_safe_coordinates()

    # Auto-refresh location data
    auto_refresh_location()

    st.markdown("### 🗺️ Interactive Location Map")

    # Map controls in a compact layout
    col_controls1, col_controls2, col_controls3 = st.columns([2, 1, 1])

    with col_controls1:
        # Quick location actions
        sub_col1, sub_col2, sub_col3 = st.columns(3)
        with sub_col1:
            if st.button("🎯 Get GPS", key="quick_gps", use_container_width=True):
                get_browser_location()
                st.rerun()
        with sub_col2:
            if st.button("🌐 IP Location", key="quick_ip", use_container_width=True):
                get_enhanced_ip_location()
                st.rerun()
        with sub_col3:
            if st.button("🔄 Refresh", key="quick_refresh", use_container_width=True):
                if st.session_state.get("auto_lat"):
                    get_detailed_address_from_coords(
                        st.session_state["auto_lat"],
                        st.session_state["auto_lon"]
                    )
                st.rerun()

    with col_controls2:
        map_style = st.selectbox(
            "Style",
            ["satellite-streets", "light", "dark", "streets", "outdoors"],
            index=0,
            key="enhanced_map_style"
        )

    with col_controls3:
        map_zoom = st.slider("Zoom", 10, 20, 16, key="enhanced_map_zoom")

    # Create a more readable map with better visualization
    view_state = pdk.ViewState(
        latitude=lat,
        longitude=lon,
        zoom=map_zoom,
        pitch=50,  # Slight tilt for better readability
        bearing=0
    )

    # Enhanced marker layer with better visibility
    marker_layer = pdk.Layer(
        "ScatterplotLayer",
        data=pd.DataFrame([{
            "lat": lat,
            "lon": lon,
            "radius": 80,
            "color": [255, 0, 0, 200]
        }]),
        get_position=["lon", "lat"],
        get_color="color",
        get_radius="radius",
        pickable=True,
        stroked=True,
        filled=True,
        line_width_min_pixels=3,
        line_color=[255, 255, 255]
    )

    # Add accuracy circle if GPS data available
    layers = [marker_layer]
    if st.session_state.get("gps_accuracy"):
        accuracy = st.session_state.gps_accuracy
        if isinstance(accuracy, (int, float)) and accuracy > 0:
            circle_layer = pdk.Layer(
                "ScatterplotLayer",
                data=pd.DataFrame([{
                    "lat": lat,
                    "lon": lon,
                    "radius": max(accuracy, 20)  # Minimum 20m radius for visibility
                }]),
                get_position=["lon", "lat"],
                get_color=[0, 100, 255, 20],
                get_radius="radius",
                pickable=False
            )
            layers = [circle_layer, marker_layer]

    # Create the deck with better tooltips
    deck = pdk.Deck(
        map_style=f"mapbox://styles/mapbox/{map_style}-v11",
        initial_view_state=view_state,
        layers=layers,
        tooltip={
            "html": """
                <b>📍 Your Location</b><br/>
                Lat: {lat:.6f}<br/>
                Lon: {lon:.6f}
            """,
            "style": {
                "backgroundColor": "#1f77b4",
                "color": "white",
                "fontSize": "14px",
                "padding": "10px",
                "borderRadius": "5px"
            }
        }
    )

    # Display the map
    st.pydeck_chart(deck)

    # Real-time address display with auto-update
    display_current_address(lat, lon)

    # Manual coordinate adjustment (only in registration form)
    if st.session_state.get("page") == "registration":
        display_coordinate_adjustment(lat, lon)


def display_current_address(lat, lon):
    """Display and auto-update the current address information"""
    st.markdown("#### 📍 Current Location Details")

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

        # Show address components if available for form auto-fill
        if "address_components" in st.session_state:
            components = st.session_state["address_components"]
            if components.get("road") or components.get("city"):
                st.caption("💡 This address will auto-fill the form below")

    else:
        st.warning("📍 No address detected. Use GPS or enter manually below.")

    # Last update time
    last_check = st.session_state.get("last_location_check")
    if last_check:
        last_update = time.strftime('%H:%M:%S', time.localtime(last_check))
        st.caption(f"🕒 Last updated: {last_update}")


def display_coordinate_adjustment(lat, lon):
    """Display manual coordinate adjustment controls"""
    st.markdown("#### 🎯 Fine-tune Location")

    with st.expander("Adjust Coordinates Manually", expanded=False):
        col_lat, col_lon, col_btn = st.columns([2, 2, 1])

        with col_lat:
            new_lat = st.number_input(
                "Latitude",
                value=float(lat),
                format="%.6f",
                step=0.0001,
                key="manual_latitude",
                help="Adjust latitude coordinate"
            )

        with col_lon:
            new_lon = st.number_input(
                "Longitude",
                value=float(lon),
                format="%.6f",
                step=0.0001,
                key="manual_longitude",
                help="Adjust longitude coordinate"
            )

        with col_btn:
            st.write("")
            st.write("")
            if st.button("🔄 Update", key="update_manual_coords", use_container_width=True):
                st.session_state.latitude = new_lat
                st.session_state.longitude = new_lon
                with st.spinner("Updating address..."):
                    get_detailed_address_from_coords(new_lat, new_lon)
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
        "last_location_check"
    ]
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
        "Please provide your location information to begin registration or access the admin portal."
    )

    st.divider()

    # Enhanced location detection with better layout
    st.markdown("### 📍 Get Your Location")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🎯 **Use GPS** (Most Accurate)", use_container_width=True, type="primary"):
            get_browser_location()
            st.rerun()
    with col2:
        if st.button("🌐 **Use IP Location** (Fallback)", use_container_width=True):
            get_enhanced_ip_location()
            st.rerun()
    with col3:
        if st.button("🔄 **Clear Location**", use_container_width=True):
            for key in ["auto_lat", "auto_lon", "latitude", "longitude", "auto_full_address"]:
                st.session_state.pop(key, None)
            st.success("Location cleared!")
            st.rerun()

    st.divider()

    # Show enhanced readable map
    show_enhanced_readable_map()

    st.markdown("---")

    # Navigation buttons
    st.markdown("### 🚀 Next Steps")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("➡️ **Start Registration**", use_container_width=True, type="primary"):
            st.session_state.page = "registration"
            st.rerun()
    with col_b:
        if st.button("🔐 **Admin Portal**", use_container_width=True):
            st.session_state.page = "admin_login"
            st.rerun()
    with col_c:
        if st.button("♻️ **Reset Session**", use_container_width=True):
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

    # Show enhanced map in registration form
    show_enhanced_readable_map()

    # Personal Information
    st.markdown("### 👤 Personal Information")
    col1, col2 = st.columns(2)

    with col1:
        first_name = st.text_input("First Name *", key="reg_fname")
        last_name = st.text_input("Last Name *", key="reg_lname")
        email = st.text_input("Email *", key="reg_email")

    with col2:
        telephone = st.text_input("Telephone Number * (format: (242) 456-4567)", key="reg_tel")
        cell = st.text_input("Cell Number (optional)", key="reg_cell")

    # Validation
    email_valid = True
    phone_valid = True

    if email and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,4}$", email):
        st.warning("⚠️ Invalid email format.")
        email_valid = False

    if telephone and not re.match(r"^\(\d{3}\) \d{3}-\d{4}$", telephone):
        st.warning("⚠️ Phone number must be in format (242) 456-4567")
        phone_valid = False

    # Address Information - Auto-populated from GPS
    st.markdown("### 📍 Address Information")
    ISLANDS = [
        "New Providence", "Grand Bahama", "Abaco", "Acklins", "Andros",
        "Berry Islands", "Bimini", "Cat Island", "Crooked Island",
        "Eleuthera", "Exuma", "Inagua", "Long Island", "Mayaguana",
        "Ragged Island", "Rum Cay", "San Salvador"
    ]

    # Auto-populate from GPS if available
    island_default = ""
    settlement_default = ""
    street_default = ""

    if "address_components" in st.session_state:
        components = st.session_state["address_components"]
        if components.get("city"):
            settlement_default = components["city"]
        if components.get("road"):
            street_default = components["road"]

    col1, col2 = st.columns(2)
    with col1:
        island_selected = st.selectbox(
            "Island *",
            ISLANDS,
            key="reg_island"
        )
        settlement_selected = st.text_input("Settlement/District *", value=settlement_default, key="reg_settlement")

    with col2:
        street_address = st.text_input("Street Address *", value=street_default, key="reg_street")

        # Quick address helper
        if st.session_state.get("auto_full_address"):
            st.caption(f"💡 GPS detected: {st.session_state['auto_full_address']}")

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

    # Save button
    col_back, col_save = st.columns([1, 2])
    with col_back:
        if st.button("← Back to Home"):
            st.session_state.page = "landing"
            st.rerun()

    with col_save:
        if st.button("💾 Save & Continue", type="primary", use_container_width=True):
            # Validation
            if not all([first_name, last_name, telephone, email, island_selected, settlement_selected, street_address]):
                st.error("⚠️ Please complete all required fields marked with *")
                return

            if not email_valid or not phone_valid:
                st.error("⚠️ Please fix validation errors above.")
                return

            if not selected_methods:
                st.error("⚠️ Please select at least one communication method.")
                return

            if not interview_selected:
                st.error("⚠️ Please select at least one interview method.")
                return

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
                        "communication_methods": communication_methods,
                        "island": island_selected,
                        "settlement": settlement_selected,
                        "street_address": street_address,
                        "interview_methods": interview_methods,
                        "latitude": st.session_state.get("latitude"),
                        "longitude": st.session_state.get("longitude")
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
        if st.button("← Back"):
            st.session_state.page = "registration"
            st.rerun()

    with col_save:
        if st.button("💾 Save Availability", type="primary"):
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

                st.success("✅ Availability saved successfully!")
                st.session_state.page = "confirmation"
                st.rerun()
            except Exception as e:
                st.error(f"❌ Database error: {e}")


# =============================
# FIXED CONFIRMATION PAGE
# =============================
def confirmation_page():
    st.title("🎉 Thank You for Registering!")
    st.markdown(
        "Your registration for the **National Agricultural Census Pilot Project (NACP)** "
        "has been successfully submitted.\n\n"
        "Our team will contact you using your preferred communication method to schedule your interview."
    )

    st.divider()

    # Display registration details
    try:
        with engine.begin() as conn:
            reg = conn.execute(
                text("SELECT * FROM registration_form ORDER BY id DESC LIMIT 1")
            ).mappings().fetchone()

            if reg:
                st.markdown("### 📋 Your Registration Details")
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Name:** {reg['first_name']} {reg['last_name']}")
                    st.markdown(f"**Email:** {reg['email']}")
                    st.markdown(f"**Phone:** {reg['telephone']}")
                    st.markdown(f"**Island:** {reg['island']}")

                with col2:
                    st.markdown(f"**Settlement:** {reg['settlement']}")
                    st.markdown(f"**Street:** {reg['street_address']}")
                    st.markdown(f"**Communication:** {format_array_for_display(reg.get('communication_methods'))}")
                    st.markdown(f"**Interview Method:** {format_array_for_display(reg.get('interview_methods'))}")

                # Safely display availability data
                available_days = format_array_for_display(reg.get('available_days'))
                available_times = format_array_for_display(reg.get('available_times'))

                st.markdown(f"**Available Days:** {available_days}")
                st.markdown(f"**Available Times:** {available_times}")

                # Display coordinates if available
                if reg.get('latitude') and reg.get('longitude'):
                    st.markdown(f"**Location Coordinates:** {reg['latitude']:.6f}, {reg['longitude']:.6f}")
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
    "confirmation": confirmation_page,
    "admin_login": admin_login,
    "admin_dashboard": admin_dashboard
}

# Execute current page
current_page = st.session_state.get("page", "landing")
page_function = page_map.get(current_page, landing_page)
page_function()