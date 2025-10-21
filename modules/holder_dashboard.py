import streamlit as st
import pandas as pd
import requests
from sqlalchemy import text
from streamlit_js_eval import get_geolocation
from datetime import date
from census_app.db import engine
from census_app.config import HOLDERS_TABLE, TOTAL_SURVEY_SECTIONS
from census_app.modules.holder_information_form import holder_information_form
from census_app.modules.survey_sections import show_regular_survey_section
from census_app.helpers import calculate_age

# Optional: PyDeck for enhanced maps
try:
    import pydeck as pdk
    PYDECK_AVAILABLE = True
except ImportError:
    PYDECK_AVAILABLE = False

# Optional labour survey
try:
    from census_app.modules.holding_labour_form import run_holding_labour_survey
except ImportError:
    run_holding_labour_survey = None


# -------------------------------------------------------
# CACHED REVERSE GEOCODE FUNCTION
# -------------------------------------------------------
@st.cache_data(ttl=3600)
def reverse_geocode(lat, lon):
    """Reverse geocode coordinates to human-readable address (cached 1 hour)."""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        headers = {"User-Agent": "AgriCensusApp/1.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            address = data.get("display_name", "Address not found")
            details = data.get("address", {})
            return address, details
    except Exception:
        return "Address lookup failed", {}
    return "Unable to fetch address", {}


# -------------------------------------------------------
# HOLDER LOCATION WIDGET
# -------------------------------------------------------
def holder_location_widget(holder_id):
    st.subheader("📍 Farm Location")
    st.info("🎯 Click 'Auto Detect Location' for best accuracy, or enter coordinates manually.")

    # Responsive styling
    st.markdown("""
    <style>
    .stButton>button { width: 100%; margin-top: 0.5rem; }
    .stNumberInput>div>input { font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

    # Fetch stored coordinates
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT latitude, longitude FROM holders WHERE holder_id=:hid"),
            {"hid": holder_id}
        ).fetchone()

    # Default to Nassau, Bahamas if no location stored
    stored_lat = result[0] if result and result[0] is not None else 25.0343
    stored_lon = result[1] if result and result[1] is not None else -77.3963

    # Session state initialization
    if f"holder_lat_{holder_id}" not in st.session_state:
        st.session_state[f"holder_lat_{holder_id}"] = stored_lat
    if f"holder_lon_{holder_id}" not in st.session_state:
        st.session_state[f"holder_lon_{holder_id}"] = stored_lon

    current_lat = st.session_state[f"holder_lat_{holder_id}"]
    current_lon = st.session_state[f"holder_lon_{holder_id}"]

    # ------------------ Map Preview ------------------
    st.markdown("#### 🗺️ Current Location Preview")
    if PYDECK_AVAILABLE:
        view_state = pdk.ViewState(latitude=current_lat, longitude=current_lon, zoom=16, pitch=45)
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
    else:
        st.map(pd.DataFrame([[current_lat, current_lon]], columns=["lat", "lon"]), zoom=15)

    # ------------------ Location Controls ------------------
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

                        st.session_state[f"holder_lat_{holder_id}"] = detected_lat
                        st.session_state[f"holder_lon_{holder_id}"] = detected_lon

                        st.success("✅ GPS Lock Acquired!")
                        st.info(f"📍 Coordinates: `{detected_lat:.6f}, {detected_lon:.6f}`\n"
                                f"🎯 Accuracy: ±{accuracy}m | ⛰️ Altitude: {altitude}m")

                        address, _ = reverse_geocode(detected_lat, detected_lon)
                        st.success(f"📬 **Detected Address:**\n{address}")
                        st.rerun()
                    else:
                        st.error("⚠️ Could not access GPS. Please enable location services in your browser.")
                        st.info("💡 Make sure you clicked 'Allow' when prompted for location access.")
                except Exception as e:
                    st.error(f"❌ GPS Error: {e}")

    with col_btn2:
        if st.button("🔄 Reset to Saved", key=f"reset_loc_btn_{holder_id}"):
            st.session_state[f"holder_lat_{holder_id}"] = stored_lat
            st.session_state[f"holder_lon_{holder_id}"] = stored_lon
            st.rerun()

    st.divider()

    # ------------------ Manual Coordinate Entry ------------------
    st.markdown("#### ✏️ Manual Coordinate Entry")
    col1, col2 = st.columns(2)
    with col1:
        manual_lat = st.number_input("Latitude", value=float(current_lat), min_value=-90.0, max_value=90.0,
                                     step=0.000001, format="%.6f", key=f"lat_input_{holder_id}")
    with col2:
        manual_lon = st.number_input("Longitude", value=float(current_lon), min_value=-180.0, max_value=180.0,
                                     step=0.000001, format="%.6f", key=f"lon_input_{holder_id}")

    if st.button("📍 Update Preview", key=f"update_preview_{holder_id}"):
        st.session_state[f"holder_lat_{holder_id}"] = manual_lat
        st.session_state[f"holder_lon_{holder_id}"] = manual_lon
        st.rerun()
    # Auto-correct longitude if positive (Bahamas fix)
    if current_lon > 0 and 70 <= current_lon <= 80:
        current_lon = -abs(current_lon)

    # ------------------ Reverse Geocode ------------------
    st.markdown("#### 🏠 Street Address")
    street_address, address_details = reverse_geocode(current_lat, current_lon)
    formatted_address = street_address

    st.text_area("Current Address (auto-detected)", value=formatted_address, height=80,
                 disabled=True, help="This address is automatically generated from your coordinates")

    # ------------------ External Map Links ------------------
    col_map1, col_map2, col_map3 = st.columns(3)
    st.markdown(
        f"[🗺️ Google Maps](https://www.google.com/maps?q={current_lat},{current_lon}) | "
        f"[🌍 OpenStreetMap](https://www.openstreetmap.org/?mlat={current_lat}&mlon={current_lon}&zoom=17) | "
        f"[🍎 Apple Maps](http://maps.apple.com/?ll={current_lat},{current_lon})"
    )

    st.divider()

    # ------------------ Save Coordinates ------------------
    col_save1, col_save2 = st.columns([2, 1])
    with col_save1:
        if st.button("💾 Save Farm Location", key=f"save_loc_btn_{holder_id}", type="primary"):
            # ✅ Step 1: Auto-correct longitude for Bahamas (if positive)
            if current_lon > 0 and 70 <= current_lon <= 80:
                current_lon = -abs(current_lon)
                st.info("ℹ️ Longitude adjusted automatically for Western Hemisphere (Bahamas).")

            # ✅ Step 2: Validate coordinates
            if -90 <= current_lat <= 90 and -180 <= current_lon <= 180:
                if abs(current_lat - 25.0343) < 0.0001 and abs(current_lon + 77.3963) < 0.0001:
                    st.warning(
                        "⚠️ You are still at the default location (Nassau). Please set the correct farm coordinates.")
                else:
                    try:
                        with engine.begin() as conn:
                            conn.execute(
                                text("UPDATE holders SET latitude=:lat, longitude=:lon WHERE holder_id=:hid"),
                                {"lat": current_lat, "lon": current_lon, "hid": holder_id}
                            )
                        st.success("✅ Farm location saved successfully!")
                    except Exception as e:
                        st.error(f"❌ Failed to save location: {e}")
            else:
                st.error("❌ Invalid coordinates. Please check your latitude and longitude values.")

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

    # ------------------ Precision Info ------------------
    with st.expander("📊 Location Precision Info"):
        st.markdown(f"""
        **Coordinate Precision Guide:**
        - 6 decimal places = ~0.11 meters ✅
        - 5 decimal places = ~1.1 meters
        - 4 decimal places = ~11 meters

        **Your Current Coordinates:**
        - Latitude: `{current_lat:.6f}`
        - Longitude: `{current_lon:.6f}`
        """)


# -------------------------------------------------------
# HOLDER DASHBOARD
# -------------------------------------------------------
def holder_dashboard():
    """Main dashboard for holder users."""
    if "user" not in st.session_state or st.session_state["user"] is None:
        st.error("You must be logged in to access the dashboard.")
        return

    user_id = st.session_state["user"]["id"]

    # Fetch holders
    try:
        with engine.connect() as conn:
            holders = conn.execute(
                text(f"SELECT * FROM {HOLDERS_TABLE} WHERE owner_id=:uid ORDER BY holder_id"),
                {"uid": user_id}
            ).mappings().all()
    except Exception as e:
        st.error(f"Error fetching holders: {e}")
        return

    if not holders:
        st.info("You have no registered holders yet.")
        if st.button("➕ Add First Holder"):
            with engine.begin() as conn:
                result = conn.execute(
                    text("INSERT INTO holders (owner_id, name) VALUES (:uid, :name)"),
                    {"uid": user_id, "name": "New Holder"}
                )
                new_holder_id = result.lastrowid
            st.success("✅ Holder created successfully!")
            st.rerun()
        return

    selected_holder = next((h for h in holders if h["holder_id"] == holder_id), None)
    if not selected_holder:
        st.warning(f"⚠️ Holder ID {holder_id} not found. Defaulting to first holder.")
        selected_holder = holders[0]

    st.sidebar.markdown(f"<h4 style='text-align:center;font-weight:bold;'>{selected_holder['name']}</h4>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    # Location confirmation
    st.header("🌾 Farm Location Confirmation")
    holder_location_widget(selected_holder["holder_id"])

    # Survey section
    st.subheader("📋 Survey Section")
    current_section = st.session_state.get("next_survey_section", 1)
    if current_section <= TOTAL_SURVEY_SECTIONS:
        show_regular_survey_section(section_id=current_section, holder_id=selected_holder["holder_id"])
    elif run_holding_labour_survey:
        run_holding_labour_survey(holder_id=selected_holder["holder_id"])

    # Holder info (age)
    try:
        with engine.connect() as conn:
            dob_row = conn.execute(
                text(f"SELECT date_of_birth FROM {HOLDERS_TABLE} WHERE holder_id=:hid"),
                {"hid": selected_holder["holder_id"]}
            ).scalar()
        if dob_row:
            if isinstance(dob_row, str):
                dob_row = date.fromisoformat(dob_row)
            st.sidebar.info(f"🎂 Age: {calculate_age(dob_row)} years")
    except Exception as e:
        st.sidebar.warning(f"Could not fetch holder age: {e}")

    # Holder actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✏️ Edit Holder Info", key=f"edit_holder_{selected_holder['holder_id']}"):
            holder_information_form(selected_holder["holder_id"])
    with col3:
        if st.button("➕ Add New Holder", key=f"add_new_holder_{selected_holder['holder_id']}"):
            with engine.begin() as conn:
                result = conn.execute(
                    text("INSERT INTO holders (owner_id, name) VALUES (:uid, :name)"),
                    {"uid": user_id, "name": "New Holder"}
                )
                new_holder_id = result.lastrowid
            holder_information_form(new_holder_id)

    # Logout
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", key=f"logout_{selected_holder['holder_id']}"):
        st.session_state.clear()
        st.success("👋 Logged out successfully.")
        st.rerun()


# -------------------------------------------------------
# AGENT DASHBOARD (Placeholder)
# -------------------------------------------------------
def agent_dashboard():
    """Dashboard for agent users."""
    st.header("🕵️ Agent Dashboard")
    st.info("Agent dashboard functionality coming soon...")
