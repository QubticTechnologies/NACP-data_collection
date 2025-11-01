# main_app.py - NACP Bahamas Complete Application

# Complete self-contained version with all features

# Fully Updated Version with All Enhancements


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
from datetime import datetime, timedelta
import io




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

                
                engine = create_engine(connection_string, pool_pre_ping=True, connect_args={
                    'connect_timeout': 10,
                    'keepalives': 1,
                    'keepalives_idle': 30,
                    'keepalives_interval': 10,
                    'keepalives_count': 5
                })
                
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                
                db_type = "PostgreSQL" if "postgresql" in connection_string else "SQLite"
                


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
st.set_page_config(

    page_title="NACP Bahamas", 

    page_title="NACP Bahamas",

    layout="wide",
    page_icon="🌾",
    initial_sidebar_state="collapsed"
)

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
    "manual_coordinates": False,
    "selected_registrations": [],
    "manual_settlement": "",
    "edit_mode": False,
    "registration_confirmed": False,
    "reg_street": "",
    "show_thank_you": False,
    "last_registration_id": None,
    "export_data": None
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


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None



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



def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None



# =============================
# REVERSE GEOCODING FUNCTIONS
# =============================
def get_address_from_coordinates(lat, lon):
    """Get street address from coordinates using OpenStreetMap Nominatim"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"

        
        headers = {
            'User-Agent': 'NACP Bahamas Agricultural Census/1.0'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if 'error' not in data:
            address = data.get('display_name', '')
            address_components = data.get('address', {})
            


        headers = {
            'User-Agent': 'NACP Bahamas Agricultural Census/1.0'
        }

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        if 'error' not in data:
            address = data.get('display_name', '')
            address_components = data.get('address', {})


            # Build a formatted address for The Bahamas
            road = address_components.get('road', '')
            house_number = address_components.get('house_number', '')
            suburb = address_components.get('suburb', '')
            neighbourhood = address_components.get('neighbourhood', '')

            city = address_components.get('city', '') or address_components.get('town', '') or address_components.get('village', '')
            
            # Create formatted address
            formatted_parts = []
            

            city = address_components.get('city', '') or address_components.get('town', '') or address_components.get(
                'village', '')

            # Create formatted address
            formatted_parts = []


            if house_number:
                formatted_parts.append(house_number)
            if road:
                formatted_parts.append(road)
            if suburb:
                formatted_parts.append(suburb)
            if neighbourhood and neighbourhood != suburb:
                formatted_parts.append(neighbourhood)
            if city:
                formatted_parts.append(city)

            



            if formatted_parts:
                formatted_address = ", ".join(formatted_parts)
                return formatted_address
            else:
                return address

            
        return f"Near {lat:.6f}, {lon:.6f}"
        
    except Exception as e:
        return f"Near {lat:.6f}, {lon:.6f}"



        return f"Near {lat:.6f}, {lon:.6f}"

    except Exception as e:
        return f"Near {lat:.6f}, {lon:.6f}"



def auto_detect_and_fill_address():
    """Automatically detect and fill address when coordinates are set"""
    lat = st.session_state.get("latitude")
    lon = st.session_state.get("longitude")

    
    if not lat or not lon:
        return False
    
    try:
        address = get_address_from_coordinates(lat, lon)
        


    if not lat or not lon:
        return False

    try:
        address = get_address_from_coordinates(lat, lon)


        if address and address != f"Near {lat:.6f}, {lon:.6f}":
            # Update the street address field in session state
            st.session_state.reg_street = address
            return True
        else:
            return False

            
    except Exception as e:
        return False



    except Exception as e:
        return False



def auto_fill_address_from_coordinates():
    """Automatically fill address fields based on current coordinates"""
    lat = st.session_state.get("latitude")
    lon = st.session_state.get("longitude")

    
    if not lat or not lon:
        st.warning("⚠️ No coordinates available. Please set your location first.")
        return False
    
    try:
        with st.spinner("🔄 Detecting address from your location..."):
            address = get_address_from_coordinates(lat, lon)
            
            if address and address != f"Near {lat:.6f}, {lon:.6f}":
                # Update the street address field in session state
                st.session_state.reg_street = address
                


    if not lat or not lon:
        st.warning("⚠️ No coordinates available. Please set your location first.")
        return False

    try:
        with st.spinner("🔄 Detecting address from your location..."):
            address = get_address_from_coordinates(lat, lon)

            if address and address != f"Near {lat:.6f}, {lon:.6f}":
                # Update the street address field in session state
                st.session_state.reg_street = address


                st.success(f"📍 **Address detected:** {address}")
                return True
            else:
                st.warning("⚠️ Could not detect specific address. Please enter manually.")
                return False
                



    except Exception as e:
        st.error("❌ Failed to detect address. Please enter manually.")
        return False





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
            # First, check if the table exists
            if db_type == "PostgreSQL":
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'registration_form'
                    )
                """))
                table_exists = result.scalar()
            else:
                # SQLite
                result = conn.execute(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='registration_form'
                """))
                table_exists = result.fetchone() is not None
            


    if st.session_state.get("database_initialized"):
        return True

    try:
        with engine.begin() as conn:
            # First, check if the table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'registration_form'
                )
            """))
            table_exists = result.scalar()


            if table_exists:
                # Table exists, check if confirmed column exists
                try:
                    conn.execute(text("SELECT confirmed FROM registration_form LIMIT 1"))
                except Exception:
                    # Column doesn't exist, add it
                    conn.execute(text("ALTER TABLE registration_form ADD COLUMN confirmed BOOLEAN DEFAULT FALSE"))
                    st.info("✅ Added 'confirmed' column to existing table")
            else:
                # Create new table with confirmed column

                if db_type == "PostgreSQL":
                    conn.execute(text("""
                        CREATE TABLE registration_form (
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
                            confirmed BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                else:
                    # SQLite
                    conn.execute(text("""
                        CREATE TABLE registration_form (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            consent BOOLEAN NOT NULL,
                            first_name VARCHAR(100) NOT NULL,
                            last_name VARCHAR(100) NOT NULL,
                            email VARCHAR(150) NOT NULL,
                            telephone VARCHAR(20),
                            cell VARCHAR(20) NOT NULL,
                            communication_methods TEXT,
                            island VARCHAR(100) NOT NULL,
                            settlement VARCHAR(100) NOT NULL,
                            street_address TEXT NOT NULL,
                            interview_methods TEXT,
                            available_days TEXT,
                            available_times TEXT,
                            latitude DECIMAL(10, 8),
                            longitude DECIMAL(11, 8),
                            gps_accuracy DECIMAL(10, 2),
                            location_source VARCHAR(50),
                            confirmed BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
        
        st.session_state.database_initialized = True
        st.success("✅ Database initialized successfully")
        return True
        

                conn.execute(text("""
                    CREATE TABLE registration_form (
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
                        confirmed BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))

        st.session_state.database_initialized = True
        st.success("✅ Database initialized successfully")
        return True


    except Exception as e:
        st.error(f"❌ Database initialization error: {e}")
        return False





def restore_tables():
    """Restore database tables (recreate if missing)"""
    if engine is None:
        st.error("❌ No database connection available")
        return False

        
    try:
        with engine.begin() as conn:
            # Check if table exists
            if db_type == "PostgreSQL":
                result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'registration_form'
                    )
                """))
                table_exists = result.scalar()
            else:
                result = conn.execute(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='registration_form'
                """))
                table_exists = result.fetchone() is not None
            


    try:
        with engine.begin() as conn:
            # Check if table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'registration_form'
                )
            """))
            table_exists = result.scalar()


            if table_exists:
                # Table exists, check if confirmed column exists
                try:
                    conn.execute(text("SELECT confirmed FROM registration_form LIMIT 1"))
                    st.info("✅ Table 'registration_form' already exists with confirmed column")
                except Exception:
                    # Column doesn't exist, add it
                    conn.execute(text("ALTER TABLE registration_form ADD COLUMN confirmed BOOLEAN DEFAULT FALSE"))
                    st.success("✅ Added 'confirmed' column to existing table")
            else:
                # Recreate table with confirmed column

                if db_type == "PostgreSQL":
                    conn.execute(text("""
                        CREATE TABLE registration_form (
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
                            confirmed BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                else:
                    conn.execute(text("""
                        CREATE TABLE registration_form (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            consent BOOLEAN NOT NULL,
                            first_name VARCHAR(100) NOT NULL,
                            last_name VARCHAR(100) NOT NULL,
                            email VARCHAR(150) NOT NULL,
                            telephone VARCHAR(20),
                            cell VARCHAR(20) NOT NULL,
                            communication_methods TEXT,
                            island VARCHAR(100) NOT NULL,
                            settlement VARCHAR(100) NOT NULL,
                            street_address TEXT NOT NULL,
                            interview_methods TEXT,
                            available_days TEXT,
                            available_times TEXT,
                            latitude DECIMAL(10, 8),
                            longitude DECIMAL(11, 8),
                            gps_accuracy DECIMAL(10, 2),
                            location_source VARCHAR(50),
                            confirmed BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                st.success("✅ Table 'registration_form' restored successfully with confirmed column")
            
            st.session_state.database_initialized = True
            return True
        
                conn.execute(text("""
                    CREATE TABLE registration_form (
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
                        confirmed BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                st.success("✅ Table 'registration_form' restored successfully with confirmed column")

            st.session_state.database_initialized = True
            return True


    except Exception as e:
        st.error(f"❌ Table restoration error: {e}")
        return False





def fix_database_schema():
    """Fix database schema by adding missing columns"""
    if engine is None:
        return False

        



    try:
        with engine.begin() as conn:
            # Check if confirmed column exists
            try:
                conn.execute(text("SELECT confirmed FROM registration_form LIMIT 1"))
            except Exception:
                # Column doesn't exist, add it
                conn.execute(text("ALTER TABLE registration_form ADD COLUMN confirmed BOOLEAN DEFAULT FALSE"))
                st.success("✅ Added missing 'confirmed' column to database")
                return True

            
            st.info("✅ Database schema is up to date")
            return True
            


            st.info("✅ Database schema is up to date")
            return True


    except Exception as e:
        st.error(f"❌ Schema fix error: {e}")
        return False





def check_database_schema():
    """Check and fix database schema on startup"""
    if engine is None:
        return False

        



    try:
        with engine.begin() as conn:
            # Check if confirmed column exists
            conn.execute(text("SELECT confirmed FROM registration_form LIMIT 1"))
        return True
    except Exception:
        # Column doesn't exist, try to fix it
        return fix_database_schema()


# Initialize database on startup
if st.session_state.get("page") == "landing" and engine is not None and not st.session_state.get("database_initialized"):


# Initialize database on startup
if st.session_state.get("page") == "landing" and engine is not None and not st.session_state.get(
        "database_initialized"):

    initialize_database()

# Add schema check after database initialization
if engine is not None and st.session_state.get("database_initialized"):
    check_database_schema()





# =============================
# DATA STORAGE FUNCTIONS
# =============================
def save_registration_data(data):
    """Save registration data to database or session state as fallback"""
    if engine is not None:
        try:

            # Convert arrays to appropriate format for database
            if db_type == "PostgreSQL":
                sql = """
                    INSERT INTO registration_form (
                        consent, first_name, last_name, email, telephone, cell,
                        communication_methods, island, settlement, street_address,
                        interview_methods, available_days, available_times, 
                        latitude, longitude, gps_accuracy, location_source, confirmed
                    ) VALUES (
                        :consent, :first_name, :last_name, :email, :telephone, :cell,
                        :communication_methods, :island, :settlement, :street_address,
                        :interview_methods, :available_days, :available_times, 
                        :latitude, :longitude, :gps_accuracy, :location_source, :confirmed
                    ) RETURNING id
                """
            else:
                # SQLite - convert arrays to JSON strings
                sql = """
                    INSERT INTO registration_form (
                        consent, first_name, last_name, email, telephone, cell,
                        communication_methods, island, settlement, street_address,
                        interview_methods, available_days, available_times, 
                        latitude, longitude, gps_accuracy, location_source, confirmed
                    ) VALUES (
                        :consent, :first_name, :last_name, :email, :telephone, :cell,
                        :communication_methods, :island, :settlement, :street_address,
                        :interview_methods, :available_days, :available_times, 
                        :latitude, :longitude, :gps_accuracy, :location_source, :confirmed
                    )
                """
            
            # Prepare data for insertion
            insert_data = {
                "consent": data["consent"],
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "email": data["email"],
                "telephone": data["telephone"],
                "cell": data["cell"],
                "communication_methods": data["communication_methods"] if db_type == "PostgreSQL" else json.dumps(data["communication_methods"]),
                "island": data["island"],
                "settlement": data["settlement"],
                "street_address": data["street_address"],
                "interview_methods": data["interview_methods"] if db_type == "PostgreSQL" else json.dumps(data["interview_methods"]),
                "available_days": data["available_days"] if db_type == "PostgreSQL" else json.dumps(data["available_days"]),
                "available_times": data["available_times"] if db_type == "PostgreSQL" else json.dumps(data["available_times"]),
                "latitude": data["latitude"],
                "longitude": data["longitude"],
                "gps_accuracy": data["gps_accuracy"],
                "location_source": data["location_source"],
                "confirmed": False
            }
            
            with engine.begin() as conn:
                if db_type == "PostgreSQL":
                    result = conn.execute(text(sql), insert_data)
                    registration_id = result.scalar()
                else:
                    result = conn.execute(text(sql), insert_data)
                    registration_id = result.lastrowid
                
                st.session_state.current_registration_id = registration_id
                st.session_state.last_registration_id = registration_id
                return True
                

            sql = """
                INSERT INTO registration_form (
                    consent, first_name, last_name, email, telephone, cell,
                    communication_methods, island, settlement, street_address,
                    interview_methods, available_days, available_times, 
                    latitude, longitude, gps_accuracy, location_source, confirmed
                ) VALUES (
                    :consent, :first_name, :last_name, :email, :telephone, :cell,
                    :communication_methods, :island, :settlement, :street_address,
                    :interview_methods, :available_days, :available_times, 
                    :latitude, :longitude, :gps_accuracy, :location_source, :confirmed
                ) RETURNING id
            """

            with engine.begin() as conn:
                result = conn.execute(text(sql), {
                    **data,
                    "confirmed": False  # Initially not confirmed
                })
                registration_id = result.scalar()
                st.session_state.current_registration_id = registration_id
                st.session_state.last_registration_id = registration_id
                return True


        except Exception as e:
            st.error(f"❌ Database save error: {e}")
            return False
    else:
        registration_id = len(st.session_state.get("registration_data", {})) + 1
        if "registration_data" not in st.session_state:
            st.session_state.registration_data = {}

        



        data['id'] = registration_id
        data['confirmed'] = False
        st.session_state.registration_data[registration_id] = data
        st.session_state.current_registration_id = registration_id
        st.session_state.last_registration_id = registration_id
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

                    row = result.mappings().fetchone()
                    if row and db_type != "PostgreSQL":
                        # Convert JSON strings back to arrays for SQLite
                        row = dict(row)
                        for field in ['communication_methods', 'interview_methods', 'available_days', 'available_times']:
                            if row.get(field):
                                try:
                                    row[field] = json.loads(row[field])
                                except:
                                    row[field] = []
                    return row

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

                row = result.mappings().fetchone()
                if row and db_type != "PostgreSQL":
                    # Convert JSON strings back to arrays for SQLite
                    row = dict(row)
                    for field in ['communication_methods', 'interview_methods', 'available_days', 'available_times']:
                        if row.get(field):
                            try:
                                row[field] = json.loads(row[field])
                            except:
                                row[field] = []
                return row

                return result.mappings().fetchone()

        except Exception as e:
            return None
    else:
        registration_data = st.session_state.get("registration_data", {})
        if registration_data:
            latest_id = max(registration_data.keys())
            return registration_data[latest_id]
        return None





def get_all_registrations():
    """Get all registrations for admin selection"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                result = conn.execute(
                    text("SELECT * FROM registration_form ORDER BY id DESC")
                )

                rows = result.mappings().fetchall()
                if db_type != "PostgreSQL":
                    # Convert JSON strings back to arrays for SQLite
                    processed_rows = []
                    for row in rows:
                        row_dict = dict(row)
                        for field in ['communication_methods', 'interview_methods', 'available_days', 'available_times']:
                            if row_dict.get(field):
                                try:
                                    row_dict[field] = json.loads(row_dict[field])
                                except:
                                    row_dict[field] = []
                        processed_rows.append(row_dict)
                    return processed_rows
                return rows
                return result.mappings().fetchall()

        except Exception as e:
            st.error(f"Error loading registrations: {e}")
            return []
    else:
        return list(st.session_state.get("registration_data", {}).values())





def confirm_registration(registration_id):
    """Mark a registration as confirmed"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                result = conn.execute(
                    text("UPDATE registration_form SET confirmed = TRUE WHERE id = :id"),
                    {"id": registration_id}
                )
                return result.rowcount > 0
        except Exception as e:
            st.error(f"Confirmation error: {e}")
            return False
    else:
        if registration_id in st.session_state.get("registration_data", {}):
            st.session_state.registration_data[registration_id]['confirmed'] = True
            return True
        return False





def update_registration_data(registration_id, data):
    """Update registration data in database"""
    if engine is not None:
        try:

            # Convert arrays to appropriate format
            if db_type == "PostgreSQL":
                update_data = {
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
                    "id": registration_id
                }
            else:
                update_data = {
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "email": data["email"],
                    "telephone": data["telephone"],
                    "cell": data["cell"],
                    "communication_methods": json.dumps(data["communication_methods"]),
                    "island": data["island"],
                    "settlement": data["settlement"],
                    "street_address": data["street_address"],
                    "interview_methods": json.dumps(data["interview_methods"]),
                    "available_days": json.dumps(data["available_days"]),
                    "available_times": json.dumps(data["available_times"]),
                    "id": registration_id
                }
            


            with engine.begin() as conn:
                result = conn.execute(text("""
                    UPDATE registration_form 
                    SET first_name = :first_name, last_name = :last_name, email = :email,
                        telephone = :telephone, cell = :cell, communication_methods = :communication_methods,
                        island = :island, settlement = :settlement, street_address = :street_address,
                        interview_methods = :interview_methods, available_days = :available_days,
                        available_times = :available_times
                    WHERE id = :id

                """), update_data)

                """), {**data, "id": registration_id})

                return result.rowcount > 0
        except Exception as e:
            st.error(f"Update error: {e}")
            return False
    else:
        if registration_id in st.session_state.get("registration_data", {}):
            st.session_state.registration_data[registration_id].update(data)
            return True
        return False




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

            # AUTO-DETECT ADDRESS WHEN COORDINATES ARE SET
            auto_detect_and_fill_address()

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

        



        # AUTO-DETECT ADDRESS WHEN COORDINATES ARE SET
        auto_detect_and_fill_address()
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

            st.success(f"📍 **Location selected!** Coordinates: {map_data['last_clicked']['lat']:.6f}, {map_data['last_clicked']['lng']:.6f}")
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

            



            # AUTO-DETECT ADDRESS WHEN MANUAL COORDINATES ARE SET
            auto_detect_and_fill_address()
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
            st.session_state.reg_street = ""
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
# PAGE FUNCTIONS - COMPLETE VERSION
=======

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
        # Store previous island selection to detect changes
        previous_island = st.session_state.get("current_island")

        



        island_selected = st.selectbox(
            "Island *",
            list(ISLAND_SETTLEMENTS.keys()),
            key="reg_island"
        )

        
        # Update current island in session state
        st.session_state.current_island = island_selected
        

        # Update current island in session state
        st.session_state.current_island = island_selected


        # If island changed, update map view for later use
        if previous_island != island_selected:
            st.session_state.map_counter += 1  # Force map refresh for later pages
            if island_selected in ISLAND_CENTERS:
                center_lat, center_lon = ISLAND_CENTERS[island_selected]
                st.session_state.latitude = center_lat
                st.session_state.longitude = center_lon
                st.session_state.location_source = "island_center"

        settlements = ISLAND_SETTLEMENTS.get(island_selected, [])
        # Add "Other" option to settlements
        settlement_options = settlements + ["Other"]

        



        settlement_selected = st.selectbox(
            "Settlement/District *",
            settlement_options,
            key="reg_settlement"
        )

        



        # Show manual input if "Other" is selected
        if settlement_selected == "Other":
            manual_settlement = st.text_input(
                "Enter Settlement Name *",
                value=st.session_state.get("manual_settlement", ""),
                key="manual_settlement_input",
                placeholder="Enter your settlement name"
            )
            if manual_settlement:
                settlement_selected = manual_settlement
                st.session_state.manual_settlement = manual_settlement
        else:
            st.session_state.manual_settlement = ""

    with col2:
        # Auto-fill street address if coordinates are available
        auto_detected_address = ""
        if st.session_state.get("latitude") and st.session_state.get("longitude"):
            auto_detected_address = get_address_from_coordinates(

                st.session_state.latitude, 
                st.session_state.longitude
            )
        

                st.session_state.latitude,
                st.session_state.longitude
            )


        street_address = st.text_input(
            "Street Address *",
            value=st.session_state.get("reg_street", auto_detected_address),
            key="reg_street",
            placeholder="e.g., 123 Main Street, Coral Harbour"
        )

        



        # Show auto-detection status
        if st.session_state.get("latitude") and st.session_state.get("longitude"):
            if auto_detected_address and auto_detected_address != f"Near {st.session_state.latitude:.6f}, {st.session_state.longitude:.6f}":
                st.caption(f"📍 Address auto-detected from your location")
            else:
                st.caption("📍 Set your location first to auto-detect address")

    # REMOVED: The interactive map section from registration
    # Only show a simple location info message instead
    st.markdown("### 📍 Location Setup")
    st.info("""
    **Your location will be set in the next step.** 
    After saving your basic information, you'll be able to:
    - 🗺️ Click on an interactive map to set your exact location
    - 🌐 Use automatic location detection  
    - ✏️ Enter coordinates manually
    - 🏠 Auto-detect your street address from coordinates
    """)

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
            # Validation
            if not all([first_name, last_name, cell_raw, email, island_selected, settlement_selected, street_address]):
                st.error("⚠️ Please complete all required fields marked with *")
                return

            if settlement_selected == "Other" and not st.session_state.get("manual_settlement"):
                st.error("⚠️ Please enter your settlement name")
                return

            if not validate_phone_number(cell_raw):
                st.error("⚠️ Please enter a valid Bahamian cell number (7 or 10 digits).")
                return

            if telephone_raw and not validate_phone_number(telephone_raw):
                st.error("⚠️ Please enter a valid telephone number (7 or 10 digits).")
                return

            if not validate_email(email):
                st.error("⚠️ Please enter a valid email address.")
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
    # Security check: Prevent access if no current registration
    registration_id = st.session_state.get("current_registration_id")
    if not registration_id:
        st.error("❌ No active registration found. Please start a new registration.")
        if st.button("🏠 Back to Home"):
            st.session_state.page = "landing"
            st.rerun()
        return

    



    # Additional check: If registration is already confirmed, redirect
    reg = get_latest_registration()
    if reg and reg.get('confirmed'):
        st.error("✅ This registration has already been confirmed and submitted.")
        st.info("Your registration is complete. Please start a new registration if needed.")
        if st.button("🏠 Back to Home"):
            st.session_state.page = "landing"
            st.rerun()
        return

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

                            # Update availability data
                            if db_type == "PostgreSQL":
                                conn.execute(text("""
                                    UPDATE registration_form 
                                    SET available_days = :days, available_times = :times
                                    WHERE id = :id
                                """), {
                                    "days": selected_days,
                                    "times": selected_times,
                                    "id": registration_id
                                })
                            else:
                                conn.execute(text("""
                                    UPDATE registration_form 
                                    SET available_days = :days, available_times = :times
                                    WHERE id = :id
                                """), {
                                    "days": json.dumps(selected_days),
                                    "times": json.dumps(selected_times),
                                    "id": registration_id
                                })
                    except Exception as e:
                        st.error(f"❌ Database update error: {e}")
                        return
                
                if registration_id in st.session_state.get("registration_data", {}):
                    st.session_state.registration_data[registration_id]['available_days'] = selected_days
                    st.session_state.registration_data[registration_id]['available_times'] = selected_times
                

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
    # Security check: Prevent access if no current registration
    registration_id = st.session_state.get("current_registration_id")
    if not registration_id:
        st.error("❌ No active registration found. Please start a new registration.")
        if st.button("🏠 Back to Home"):
            st.session_state.page = "landing"
            st.rerun()
        return

    



    # Additional check: If registration is already confirmed, redirect
    reg = get_latest_registration()
    if reg and reg.get('confirmed'):
        st.error("✅ This registration has already been confirmed and submitted.")
        st.info("Your registration is complete. Please start a new registration if needed.")
        if st.button("🏠 Back to Home"):
            st.session_state.page = "landing"
            st.rerun()
        return

    st.title("📍 Confirm Your Location")

    st.markdown("""
    ### 🎯 Set Your Exact Location

    



    **Choose your method:**
    - 🗺️ **Click on the map** below to select your exact location
    - 🌐 **Use IP** for approximate location  
    - ✏️ **Enter manually** if you know your coordinates
    - 🏠 **Auto-detect address** from your coordinates
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
            st.session_state.reg_street = ""
            st.success("✅ Location cleared!")
            st.rerun()

    st.divider()

    show_interactive_map()

    st.divider()

    show_coordinate_controls()

    st.divider()

    # UPDATED: Auto-address detection section (now shows status instead of requiring button click)
    if st.session_state.get("latitude") and st.session_state.get("longitude"):
        st.markdown("### 🏠 Auto-Detected Address")

        
        # Show current coordinates
        st.info(f"**Current Coordinates:** {st.session_state.latitude:.6f}, {st.session_state.longitude:.6f}")
        
        # Show detected address status
        detected_address = get_address_from_coordinates(
            st.session_state.latitude, 
            st.session_state.longitude
        )
        
        if detected_address and detected_address != f"Near {st.session_state.latitude:.6f}, {st.session_state.longitude:.6f}":
            st.success(f"**✅ Address Auto-Detected:** {detected_address}")
            st.caption("This address has been automatically filled in your registration.")
            


        # Show current coordinates
        st.info(f"**Current Coordinates:** {st.session_state.latitude:.6f}, {st.session_state.longitude:.6f}")

        # Show detected address status
        detected_address = get_address_from_coordinates(
            st.session_state.latitude,
            st.session_state.longitude
        )

        if detected_address and detected_address != f"Near {st.session_state.latitude:.6f}, {st.session_state.longitude:.6f}":
            st.success(f"**✅ Address Auto-Detected:** {detected_address}")
            st.caption("This address has been automatically filled in your registration.")


            # Show the current value from session state (what will be used in registration)
            if st.session_state.get("reg_street"):
                st.info(f"**Street Address Field:** {st.session_state.reg_street}")
        else:

            st.warning("⚠️ Could not detect specific address from these coordinates. Please enter manually in the registration form.")

            st.warning(
                "⚠️ Could not detect specific address from these coordinates. Please enter manually in the registration form.")


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


def edit_registration_form(reg):
    """Allow candidates to edit their registration before final submission"""
    st.markdown("### ✏️ Edit Your Registration")
    


def edit_registration_form(reg):
    """Allow candidates to edit their registration before final submission"""
    st.markdown("### ✏️ Edit Your Registration")


    with st.form("edit_registration"):
        st.markdown("#### 👤 Personal Information")
        col1, col2 = st.columns(2)

        with col1:
            first_name = st.text_input("First Name *", value=reg.get('first_name', ''), key="edit_fname")
            last_name = st.text_input("Last Name *", value=reg.get('last_name', ''), key="edit_lname")
            email = st.text_input("Email *", value=reg.get('email', ''), key="edit_email")

        with col2:
            # Extract digits from formatted phone number for editing
            cell_digits = re.sub(r'\D', '', reg.get('cell', ''))
            cell_raw = st.text_input("Cell Number (Primary Contact) *",
                                     value=cell_digits,
                                     key="edit_cell",
                                     placeholder="e.g., 2424567890 or 4567890")

            



            telephone_digits = re.sub(r'\D', '', reg.get('telephone', '')) if reg.get('telephone') else ""
            telephone_raw = st.text_input("Alternate Number (Optional)",
                                          value=telephone_digits,
                                          key="edit_tel",
                                          placeholder="e.g., 2424567890")

        st.markdown("#### 📍 Address Information")
        col1, col2 = st.columns(2)
        with col1:
            # Store previous island selection to detect changes
            previous_island = st.session_state.get("current_island")

            
            island_selected = st.selectbox(
                "Island *",
                list(ISLAND_SETTLEMENTS.keys()),
                index=list(ISLAND_SETTLEMENTS.keys()).index(reg.get('island', 'New Providence')) if reg.get('island') in ISLAND_SETTLEMENTS else 0,
                key="edit_island"
            )
            
            # Update current island in session state
            st.session_state.current_island = island_selected
            


            island_selected = st.selectbox(
                "Island *",
                list(ISLAND_SETTLEMENTS.keys()),
                index=list(ISLAND_SETTLEMENTS.keys()).index(reg.get('island', 'New Providence')) if reg.get(
                    'island') in ISLAND_SETTLEMENTS else 0,
                key="edit_island"
            )

            # Update current island in session state
            st.session_state.current_island = island_selected


            # If island changed, update map view
            if previous_island != island_selected:
                st.session_state.map_counter += 1  # Force map refresh
                if island_selected in ISLAND_CENTERS:
                    center_lat, center_lon = ISLAND_CENTERS[island_selected]
                    st.session_state.latitude = center_lat
                    st.session_state.longitude = center_lon
                    st.session_state.location_source = "island_center"

            settlements = ISLAND_SETTLEMENTS.get(island_selected, [])
            settlement_options = settlements + ["Other"]

            
            current_settlement = reg.get('settlement', '')
            settlement_index = settlement_options.index(current_settlement) if current_settlement in settlement_options else 0
            


            current_settlement = reg.get('settlement', '')
            settlement_index = settlement_options.index(
                current_settlement) if current_settlement in settlement_options else 0


            settlement_selected = st.selectbox(
                "Settlement/District *",
                settlement_options,
                index=settlement_index,
                key="edit_settlement"
            )

            



            if settlement_selected == "Other":
                manual_settlement = st.text_input(
                    "Enter Settlement Name *",
                    value=current_settlement if current_settlement not in settlements else "",
                    key="edit_manual_settlement",
                    placeholder="Enter your settlement name"
                )
                if manual_settlement:
                    settlement_selected = manual_settlement

        with col2:
            street_address = st.text_input(
                "Street Address *",
                value=reg.get('street_address', ''),
                key="edit_street",
                placeholder="e.g., 123 Main Street, Coral Harbour"
            )

        # REMOVED: The interactive map section from edit registration
        st.markdown("#### 📍 Location Information")
        st.info("""
        **Location editing is available in the location confirmation step.** 
        You can update your precise location after saving these changes.
        """)

        st.markdown("#### 💬 Preferred Communication Methods")
        comm_methods = ["WhatsApp", "Phone Call", "Email", "Text Message"]
        current_comm_methods = safe_convert_array_data(reg.get('communication_methods'))
        selected_methods = []
        cols = st.columns(4)
        for i, method in enumerate(comm_methods):
            with cols[i]:
                if st.checkbox(method, value=method in current_comm_methods, key=f"edit_comm_{method}"):
                    selected_methods.append(method)

        st.markdown("#### 🗣️ Preferred Interview Method")
        interview_methods = ["In-person Interview", "Phone Interview", "Self Reporting"]
        current_interview_methods = safe_convert_array_data(reg.get('interview_methods'))
        interview_selected = []
        cols = st.columns(3)
        for i, method in enumerate(interview_methods):
            with cols[i]:
                if st.checkbox(method, value=method in current_interview_methods, key=f"edit_interview_{method}"):
                    interview_selected.append(method)

        st.markdown("#### 🕒 Availability Preferences")
        st.markdown("##### 📅 Preferred Days")
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        current_days = safe_convert_array_data(reg.get('available_days'))
        selected_days = []
        cols = st.columns(7)
        for i, day in enumerate(days):
            with cols[i]:
                if st.checkbox(day[:3], value=day in current_days, key=f"edit_day_{day}"):
                    selected_days.append(day)

        st.markdown("##### ⏰ Preferred Time Slots")
        time_slots = ["Morning (7-10am)", "Midday (11-1pm)", "Afternoon (2-5pm)", "Evening (6-8pm)"]
        current_times = safe_convert_array_data(reg.get('available_times'))
        selected_times = []
        cols = st.columns(4)
        for i, time_slot in enumerate(time_slots):
            with cols[i]:
                if st.checkbox(time_slot, value=time_slot in current_times, key=f"edit_time_{time_slot}"):
                    selected_times.append(time_slot)

        col1, col2 = st.columns(2)
        with col1:
            save_edit = st.form_submit_button("💾 Save Changes", use_container_width=True)
        with col2:
            cancel_edit = st.form_submit_button("❌ Cancel Edit", use_container_width=True, type="secondary")

        if save_edit:
            # Validation
            if not all([first_name, last_name, cell_raw, email, island_selected, settlement_selected, street_address]):
                st.error("⚠️ Please complete all required fields marked with *")
                return

            if settlement_selected == "Other" and not manual_settlement:
                st.error("⚠️ Please enter your settlement name")
                return

            if not validate_phone_number(cell_raw):
                st.error("⚠️ Please enter a valid Bahamian cell number (7 or 10 digits).")
                return

            if telephone_raw and not validate_phone_number(telephone_raw):
                st.error("⚠️ Please enter a valid telephone number (7 or 10 digits).")
                return

            if not validate_email(email):
                st.error("⚠️ Please enter a valid email address.")
                return

            if not selected_methods:
                st.error("⚠️ Please select at least one communication method.")
                return

            if not interview_selected:
                st.error("⚠️ Please select at least one interview method.")
                return

            if not selected_days or not selected_times:
                st.error("⚠️ Please select at least one day and one time slot.")
                return

            # Format phone numbers
            formatted_cell = format_phone_number(cell_raw)
            formatted_telephone = format_phone_number(telephone_raw) if telephone_raw else None

            # Update registration data
            registration_id = st.session_state.get("current_registration_id")
            if registration_id:
                update_data = {
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
                    "available_days": selected_days,
                    "available_times": selected_times
                }

                if update_registration_data(registration_id, update_data):
                    st.session_state.edit_mode = False
                    st.success("✅ Changes saved successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to save changes. Please try again.")

        if cancel_edit:
            st.session_state.edit_mode = False
            st.rerun()


def final_confirmation_page():
    # Security check: Prevent access if no current registration or already confirmed
    registration_id = st.session_state.get("current_registration_id")
    


def final_confirmation_page():
    # Security check: Prevent access if no current registration or already confirmed
    registration_id = st.session_state.get("current_registration_id")


    # Get the registration data - try multiple ways
    reg = None
    if registration_id:
        reg = get_latest_registration()

    
    # If we don't have reg but registration_confirmed is True, try to get the latest registration
    if not reg and st.session_state.get("registration_confirmed"):
        reg = get_latest_registration()
    


    # If we don't have reg but registration_confirmed is True, try to get the latest registration
    if not reg and st.session_state.get("registration_confirmed"):
        reg = get_latest_registration()


    # Additional security: If registration is already confirmed, show thank you message
    if reg and reg.get('confirmed'):
        # SHOW PERSONALIZED THANK YOU MESSAGE FOR ALREADY CONFIRMED REGISTRATIONS
        user_name = f"{reg.get('first_name', '')} {reg.get('last_name', '')}".strip()
        user_island = reg.get('island', 'The Bahamas')

        
        st.balloons()
        st.success("🎉 **Registration Already Confirmed and Submitted!**")
        
        st.markdown(f"""
        ### 🙏 Thank You for Your Participation, {user_name}!
        
        **Dear {user_name},**
        
        Your registration from **{user_island}** has already been confirmed and submitted successfully.
        
        On behalf of the **Ministry of Agriculture and Marine Resources** and the entire **National Agricultural Census Pilot (NACP)** team, 
        we extend our heartfelt gratitude for your participation in this important initiative.
        
        ### Your Contribution Matters
        
        Thank you for being an essential part of building a more resilient and prosperous agricultural future for The Bahamas. 
        
        With sincere appreciation,
        
=======

        st.balloons()
        st.success("🎉 **Registration Already Confirmed and Submitted!**")

        st.markdown(f"""
        ### 🙏 Thank You for Your Participation, {user_name}!

        **Dear {user_name},**

        Your registration from **{user_island}** has already been confirmed and submitted successfully.

        On behalf of the **Ministry of Agriculture and Marine Resources** and the entire **National Agricultural Census Pilot (NACP)** team, 
        we extend our heartfelt gratitude for your participation in this important initiative.

        ### Your Contribution Matters

        Thank you for being an essential part of building a more resilient and prosperous agricultural future for The Bahamas. 

        With sincere appreciation,


        **The NACP Team**  
        *Ministry of Agriculture and Marine Resources*  
        *Government of The Bahamas*
        """)

        if st.button("🏠 Back to Home"):
            st.session_state.page = "landing"
            st.session_state.registration_confirmed = False
            st.session_state.edit_mode = False
            st.session_state.current_registration_id = None
            st.rerun()
        return

    if not registration_id and not st.session_state.get("registration_confirmed"):
        st.error("❌ No active registration found. Please start a new registration.")
        if st.button("🏠 Back to Home"):
            st.session_state.page = "landing"
            st.rerun()
        return

    st.title("🎉 Registration Complete!")

    



    if not reg:
        st.error("❌ No registration data found. Please start over.")
        if st.button("🏠 Back to Home"):
            st.session_state.page = "landing"
            st.rerun()
        return

    # Check if we're in edit mode
    if st.session_state.get("edit_mode"):
        st.info("✏️ **Edit Mode** - You can modify your information below")
        edit_registration_form(reg)
        return

    # Check if registration is confirmed
    if not st.session_state.get("registration_confirmed"):
        # Show registration summary for review BEFORE confirmation
        st.success("✅ **All information saved! Please review your details below.**")

        



        if reg.get('latitude') and reg.get('longitude'):
            source = reg.get('location_source', 'manual')
            source_display = {
                'gps': '🎯 GPS',

                'ip': '🌐 IP', 

                'ip': '🌐 IP',

                'map_click': '🗺️ Map',
                'manual': '✏️ Manual',
                'unknown': '❓ Unknown'
            }
            st.success(f"📍 **Location saved via {source_display.get(source, 'manual')}**")

        
        st.markdown("### 📋 Registration Summary")
        
        col1, col2 = st.columns(2)
        


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
            


            st.markdown("#### 🕒 Availability")
            st.write(f"**Days:** {format_array_for_display(reg.get('available_days'))}")
            st.write(f"**Times:** {format_array_for_display(reg.get('available_times'))}")


            if reg.get('latitude') and reg.get('longitude'):
                st.markdown("#### 📍 Location")
                st.write(f"**Coordinates:** {reg.get('latitude'):.6f}, {reg.get('longitude'):.6f}")
                st.write(f"**Source:** {source_display.get(source, 'Unknown')}")

        st.divider()

        
        # Edit and Confirm buttons
        col1, col2, col3 = st.columns(3)
        


        # Edit and Confirm buttons
        col1, col2, col3 = st.columns(3)

>>>>>>> dbc111f (Initial commit of cleaned census_app)
        with col1:
            if st.button("✏️ Edit Information", use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()

        



        with col2:
            if st.button("✅ Confirm Submission", type="primary", use_container_width=True):
                if confirm_registration(registration_id):
                    st.session_state.registration_confirmed = True
                    # Don't clear current_registration_id immediately - keep it for the thank you message
                    st.success("🎉 **Registration confirmed and submitted!**")
                    st.rerun()
                else:
                    st.error("❌ Failed to confirm registration. Please try again.")

        



        with col3:
            if st.button("🗺️ View Location", use_container_width=True):
                st.session_state.page = "location_confirmation"
                st.rerun()

    



    else:
        # THIS IS WHERE THE PERSONALIZED THANK YOU MESSAGE APPEARS AFTER CONFIRMATION
        user_name = f"{reg.get('first_name', '')} {reg.get('last_name', '')}".strip()
        user_island = reg.get('island', 'The Bahamas')

        
        st.balloons()  # Add celebration effect
        
        st.success("🎉 **Registration Confirmed and Submitted!**")
        
        st.markdown(f"""
        ### 🙏 Thank You for Your Participation, {user_name}!
        
        **Dear {user_name},**
        
        On behalf of the **Ministry of Agriculture and Marine Resources** and the entire **National Agricultural Census Pilot (NACP)** team, 
        we extend our heartfelt gratitude for taking the time to complete your registration from **{user_island}**.
        
        ### Your Contribution Matters
        
        By participating in this important initiative, you are directly helping to:
        
=======

        st.balloons()  # Add celebration effect

        st.success("🎉 **Registration Confirmed and Submitted!**")

        st.markdown(f"""
        ### 🙏 Thank You for Your Participation, {user_name}!

        **Dear {user_name},**

        On behalf of the **Ministry of Agriculture and Marine Resources** and the entire **National Agricultural Census Pilot (NACP)** team, 
        we extend our heartfelt gratitude for taking the time to complete your registration from **{user_island}**.

        ### Your Contribution Matters

        By participating in this important initiative, you are directly helping to:


        🌱 **Shape agricultural policies** that support farmers across The Bahamas  
        📊 **Provide accurate data** for better resource allocation and planning  
        🏝️ **Strengthen food security** in our island nation  
        🤝 **Build stronger communities** through improved agricultural support

        
        ### What Happens Next?
        
        - Your information has been **securely stored** in our system
        - You will be contacted based on your preferred communication methods: **{format_array_for_display(reg.get('communication_methods'))}**
        - Our team will reach out during your preferred times: **{format_array_for_display(reg.get('available_days'))}** - **{format_array_for_display(reg.get('available_times'))}**
        
        ### Your Voice Makes a Difference
        
        Thank you for being an essential part of building a more resilient and prosperous agricultural future for The Bahamas. 
        Farmers like you are the foundation of our nation's food security and economic growth.
        
        With sincere appreciation,
        


        ### What Happens Next?

        - Your information has been **securely stored** in our system
        - You will be contacted based on your preferred communication methods: **{format_array_for_display(reg.get('communication_methods'))}**
        - Our team will reach out during your preferred times: **{format_array_for_display(reg.get('available_days'))}** - **{format_array_for_display(reg.get('available_times'))}**

        ### Your Voice Makes a Difference

        Thank you for being an essential part of building a more resilient and prosperous agricultural future for The Bahamas. 
        Farmers like you are the foundation of our nation's food security and economic growth.

        With sincere appreciation,


        **The NACP Team**  
        *Ministry of Agriculture and Marine Resources*  
        *Government of The Bahamas*  
        *Building a Stronger Agricultural Future Together*
        """)

        st.divider()

        



        # Add a nice visual element
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Registration Status", "✅ Complete")
        with col2:
            st.metric("Location", f"📍 {user_island}")
        with col3:
            st.metric("Thank You", "🌟 Appreciated")

        
        st.divider()
        
        col1, col2 = st.columns(2)
        

        st.divider()

        col1, col2 = st.columns(2)


        with col1:
            if st.button("🏠 Return to Homepage", use_container_width=True, type="primary"):
                # Now clear the registration data when going back to home
                st.session_state.page = "landing"
                st.session_state.registration_confirmed = False
                st.session_state.edit_mode = False
                st.session_state.current_registration_id = None
                st.rerun()

        



        with col2:
            if st.button("📝 Register Another Person", use_container_width=True):
                reset_session()
                st.session_state.page = "registration"
                st.rerun()


def admin_login():
    st.title("🔐 Admin Portal")
    
    st.markdown("### Administrator Login")
    
    col1, col2 = st.columns(2)
    


def admin_login():
    st.title("🔐 Admin Portal")

    st.markdown("### Administrator Login")

    col1, col2 = st.columns(2)


    with col1:
        username = st.text_input("Username", key="admin_user")
    with col2:
        password = st.text_input("Password", type="password", key="admin_pass")

    
    col1, col2, col3 = st.columns([2, 1, 2])
    


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
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Registrations", "🗺️ Map View", "⚙️ Database", "🗑️ Delete Management"])
    
    with tab1:
        st.markdown("### 📋 All Registrations")
        


    st.title("📊 Admin Dashboard")

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Registrations", "🗺️ Map View", "⚙️ Database", "🗑️ Delete Management"])

    with tab1:
        st.markdown("### 📋 All Registrations")


        if engine is not None:
            try:
                with engine.begin() as conn:
                    result = conn.execute(text("SELECT COUNT(*) FROM registration_form"))
                    count = result.scalar()
                    st.metric("Total Registrations", count)

                    
                    result_confirmed = conn.execute(text("SELECT COUNT(*) FROM registration_form WHERE confirmed = TRUE"))


                    result_confirmed = conn.execute(
                        text("SELECT COUNT(*) FROM registration_form WHERE confirmed = TRUE"))

                    confirmed_count = result_confirmed.scalar()
                    st.metric("Confirmed Registrations", confirmed_count)
            except Exception as e:
                st.error(f"Database error: {e}")
                count = 0
                confirmed_count = 0
        else:
            count = len(st.session_state.get("registration_data", {}))

            confirmed_count = len([r for r in st.session_state.get("registration_data", {}).values() if r.get('confirmed')])
            st.metric("Total Registrations", count)
            st.metric("Confirmed Registrations", confirmed_count)
        
        if count > 0:
            registrations = get_all_registrations()
            

            confirmed_count = len(
                [r for r in st.session_state.get("registration_data", {}).values() if r.get('confirmed')])
            st.metric("Total Registrations", count)
            st.metric("Confirmed Registrations", confirmed_count)

        if count > 0:
            if engine is not None:
                try:
                    with engine.begin() as conn:
                        result = conn.execute(
                            text("""
                                SELECT id, first_name, last_name, email, cell, island, settlement, 
                                       created_at, latitude, longitude, location_source, confirmed
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


            # Table with delete checkboxes
            if registrations:
                # Create a DataFrame for selection
                df_data = []
                for reg in registrations:
                    df_data.append({
                        "Delete": False,
                        "ID": reg.get('id'),
                        "Name": f"{reg.get('first_name', '')} {reg.get('last_name', '')}",
                        "Email": reg.get('email', ''),
                        "Cell": reg.get('cell', ''),
                        "Island": reg.get('island', ''),
                        "Settlement": reg.get('settlement', ''),
                        "Confirmed": "✅" if reg.get('confirmed') else "❌",
                        "Location": "📍" if reg.get('latitude') else "❓",
                        "Created": reg.get('created_at', ''),
                        "Source": reg.get('location_source', 'unknown')
                    })

                
                df = pd.DataFrame(df_data)
                


                df = pd.DataFrame(df_data)


                # Display the dataframe with selection
                edited_df = st.data_editor(
                    df,
                    column_config={
                        "Delete": st.column_config.CheckboxColumn(
                            "Delete",
                            help="Select to delete",
                            default=False,
                        ),
                        "Confirmed": st.column_config.TextColumn("Status"),
                        "Location": st.column_config.TextColumn("GPS")
                    },
                    hide_index=True,
                    use_container_width=True
                )

                
                # Get selected rows for deletion
                selected_rows = edited_df[edited_df["Delete"] == True]
                


                # Get selected rows for deletion
                selected_rows = edited_df[edited_df["Delete"] == True]


                if not selected_rows.empty:
                    st.warning(f"⚠️ {len(selected_rows)} registration(s) selected for deletion")
                    if st.button("🗑️ Delete Selected", type="secondary"):
                        deleted_count = 0
                        for _, row in selected_rows.iterrows():
                            if delete_registration(row["ID"]):
                                deleted_count += 1

                        



                        if deleted_count > 0:
                            st.success(f"✅ Successfully deleted {deleted_count} registration(s)")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete registrations")

                



                # Show detailed view
                st.markdown("### 👤 Registration Details")
                selected_id = st.selectbox(
                    "Select registration to view details:",
                    options=[r.get('id') for r in registrations],

                    format_func=lambda x: f"ID {x}: {next((f'{r.get('first_name')} {r.get('last_name')}' for r in registrations if r.get('id') == x), 'Unknown')}"
                )
                

                    format_func=lambda
                        x: f"ID {x}: {next((f'{r.get('first_name')} {r.get('last_name')}' for r in registrations if r.get('id') == x), 'Unknown')}"
                )


                if selected_id:
                    selected_reg = next((r for r in registrations if r.get('id') == selected_id), None)
                    if selected_reg:
                        col1, col2 = st.columns(2)

                        
                        with col1:
                            st.markdown("#### Personal Information")
                            st.write(f"**Name:** {selected_reg.get('first_name', '')} {selected_reg.get('last_name', '')}")


                        with col1:
                            st.markdown("#### Personal Information")
                            st.write(
                                f"**Name:** {selected_reg.get('first_name', '')} {selected_reg.get('last_name', '')}")

                            st.write(f"**Email:** {selected_reg.get('email', '')}")
                            st.write(f"**Cell:** {selected_reg.get('cell', '')}")
                            if selected_reg.get('telephone'):
                                st.write(f"**Telephone:** {selected_reg.get('telephone', '')}")

                            



                            st.markdown("#### Address")
                            st.write(f"**Island:** {selected_reg.get('island', '')}")
                            st.write(f"**Settlement:** {selected_reg.get('settlement', '')}")
                            st.write(f"**Street:** {selected_reg.get('street_address', '')}")

                        
                        with col2:
                            st.markdown("#### Preferences")
                            st.write(f"**Communication:** {format_array_for_display(selected_reg.get('communication_methods'))}")
                            st.write(f"**Interview:** {format_array_for_display(selected_reg.get('interview_methods'))}")
                            st.write(f"**Days:** {format_array_for_display(selected_reg.get('available_days'))}")
                            st.write(f"**Times:** {format_array_for_display(selected_reg.get('available_times'))}")
                            
                            st.markdown("#### Location Data")
                            if selected_reg.get('latitude') and selected_reg.get('longitude'):
                                st.write(f"**Coordinates:** {selected_reg.get('latitude'):.6f}, {selected_reg.get('longitude'):.6f}")

                        with col2:
                            st.markdown("#### Preferences")
                            st.write(
                                f"**Communication:** {format_array_for_display(selected_reg.get('communication_methods'))}")
                            st.write(
                                f"**Interview:** {format_array_for_display(selected_reg.get('interview_methods'))}")
                            st.write(f"**Days:** {format_array_for_display(selected_reg.get('available_days'))}")
                            st.write(f"**Times:** {format_array_for_display(selected_reg.get('available_times'))}")

                            st.markdown("#### Location Data")
                            if selected_reg.get('latitude') and selected_reg.get('longitude'):
                                st.write(
                                    f"**Coordinates:** {selected_reg.get('latitude'):.6f}, {selected_reg.get('longitude'):.6f}")

                                st.write(f"**Source:** {selected_reg.get('location_source', 'unknown')}")
                                if selected_reg.get('gps_accuracy'):
                                    st.write(f"**Accuracy:** {selected_reg.get('gps_accuracy')}m")
                            else:
                                st.write("**Coordinates:** Not set")

                            
                            st.write(f"**Created:** {selected_reg.get('created_at', 'Unknown')}")
                            st.write(f"**Confirmed:** {'✅ Yes' if selected_reg.get('confirmed') else '❌ No'}")
            


                            st.write(f"**Created:** {selected_reg.get('created_at', 'Unknown')}")
                            st.write(f"**Confirmed:** {'✅ Yes' if selected_reg.get('confirmed') else '❌ No'}")


            else:
                st.info("📭 No registrations found")
        else:
            st.info("📭 No registrations in the system")

    
    with tab2:
        st.markdown("### 🗺️ Registration Map View")
        
        located_registrations = []


    with tab2:
        st.markdown("### 🗺️ Registration Map View")


        if engine is not None:
            try:
                with engine.begin() as conn:
                    result = conn.execute(
                        text("""
                            SELECT first_name, last_name, island, settlement, street_address,
                                   latitude, longitude, location_source, confirmed
                            FROM registration_form 
                            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
                        """)
                    )
                    located_registrations = result.mappings().fetchall()
            except Exception as e:
                st.error(f"Error loading location data: {e}")

        else:
            located_registrations = [
                r for r in st.session_state.get("registration_data", {}).values() 
                if r.get('latitude') and r.get('longitude')
            ]
        
        if located_registrations:
            # Create map centered on The Bahamas
            m = folium.Map(location=[25.0343, -77.3963], zoom_start=7, tiles='OpenStreetMap')
               
                located_registrations = []
        else:
            located_registrations = [
                r for r in st.session_state.get("registration_data", {}).values()
                if r.get('latitude') and r.get('longitude')
            ]

        if located_registrations:
            # Create map centered on The Bahamas
            m = folium.Map(location=[25.0343, -77.3963], zoom_start=7, tiles='OpenStreetMap')


            # Add markers for each registration
            for reg in located_registrations:
                lat = reg.get('latitude')
                lon = reg.get('longitude')

                



                if lat and lon:
                    # Different colors for confirmed vs unconfirmed
                    color = 'green' if reg.get('confirmed') else 'blue'
                    icon = 'ok-sign' if reg.get('confirmed') else 'info-sign'

                    



                    popup_text = f"""
                    <b>{reg.get('first_name', '')} {reg.get('last_name', '')}</b><br>
                    <i>{reg.get('island', '')}, {reg.get('settlement', '')}</i><br>
                    {reg.get('street_address', '')}<br>
                    Status: {'✅ Confirmed' if reg.get('confirmed') else '❌ Pending'}
                    """

                    



                    folium.Marker(
                        [lat, lon],
                        popup=folium.Popup(popup_text, max_width=300),
                        tooltip=f"{reg.get('first_name', '')} {reg.get('last_name', '')}",
                        icon=folium.Icon(color=color, icon=icon)
                    ).add_to(m)

            
            # Display the map
            folium_static(m, width=800, height=600)
            
            st.markdown("#### 📊 Location Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Located Registrations", len(located_registrations))
            
            with col2:
                confirmed_located = len([r for r in located_registrations if r.get('confirmed')])
                st.metric("Confirmed & Located", confirmed_located)
            


            # Display the map
            folium_static(m, width=800, height=600)

            st.markdown("#### 📊 Location Statistics")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Located Registrations", len(located_registrations))

            with col2:
                confirmed_located = len([r for r in located_registrations if r.get('confirmed')])
                st.metric("Confirmed & Located", confirmed_located)


            with col3:
                sources = {}
                for reg in located_registrations:
                    source = reg.get('location_source', 'unknown')
                    sources[source] = sources.get(source, 0) + 1

                
                if sources:
                    main_source = max(sources.items(), key=lambda x: x[1])
                    st.metric("Main Source", f"{main_source[0]} ({main_source[1]})")
        
        else:
            st.info("🗺️ No registrations with location data available")
    
    with tab3:
        st.markdown("### ⚙️ Database Management")
        
        col1, col2 = st.columns(2)
        


                if sources:
                    main_source = max(sources.items(), key=lambda x: x[1])
                    st.metric("Main Source", f"{main_source[0]} ({main_source[1]})")

        else:
            st.info("🗺️ No registrations with location data available")

    with tab3:
        st.markdown("### ⚙️ Database Management")

        col1, col2 = st.columns(2)


        with col1:
            st.markdown("#### Database Status")
            if engine is None:
                st.error("❌ No database connection")
                st.write("**Mode:** In-memory storage only")
            else:
                st.success(f"✅ Connected to {db_type}")
                st.write(f"**Type:** {db_type}")

                



                if db_type == "PostgreSQL":
                    if "render.com" in str(engine.url):
                        st.write("**Host:** Render PostgreSQL")
                    else:
                        st.write("**Host:** Local PostgreSQL")
                else:
                    st.write("**Host:** SQLite file")

            



            # Database statistics
            if engine is not None:
                try:
                    with engine.begin() as conn:
                        result = conn.execute(text("SELECT COUNT(*) FROM registration_form"))
                        total_count = result.scalar()

                        
                        result_confirmed = conn.execute(text("SELECT COUNT(*) FROM registration_form WHERE confirmed = TRUE"))
                        confirmed_count = result_confirmed.scalar()
                        
                        result_located = conn.execute(text("SELECT COUNT(*) FROM registration_form WHERE latitude IS NOT NULL"))
                        located_count = result_located.scalar()
                    
                    st.metric("Total Records", total_count)
                    st.metric("Confirmed", confirmed_count)
                    st.metric("With Location", located_count)
                    
                except Exception as e:
                    st.error(f"Error getting statistics: {e}")
        
        with col2:
            st.markdown("#### Maintenance Actions")
            


                        result_confirmed = conn.execute(
                            text("SELECT COUNT(*) FROM registration_form WHERE confirmed = TRUE"))
                        confirmed_count = result_confirmed.scalar()

                        result_located = conn.execute(
                            text("SELECT COUNT(*) FROM registration_form WHERE latitude IS NOT NULL"))
                        located_count = result_located.scalar()

                    st.metric("Total Records", total_count)
                    st.metric("Confirmed", confirmed_count)
                    st.metric("With Location", located_count)

                except Exception as e:
                    st.error(f"Error getting statistics: {e}")

        with col2:
            st.markdown("#### Maintenance Actions")


            if st.button("🔄 Initialize/Restore Tables", use_container_width=True):
                if restore_tables():
                    st.success("✅ Tables restored successfully")
                else:
                    st.error("❌ Failed to restore tables")

            



            if st.button("🔧 Fix Schema", use_container_width=True):
                if fix_database_schema():
                    st.success("✅ Schema fixed successfully")
                else:
                    st.error("❌ Failed to fix schema")

            
            if st.button("📤 Export Data", use_container_width=True):
                export_data()
            

            if st.button("📤 Export Data", use_container_width=True):
                export_data()


            if st.button("🧹 Clear All Data", use_container_width=True, type="secondary"):
                st.warning("⚠️ This will delete ALL registration data permanently!")
                if st.checkbox("I understand this action cannot be undone"):
                    if clear_all_data():
                        st.success("✅ All data cleared successfully")
                        st.rerun()
                    else:
                        st.error("❌ Failed to clear data")

    
    with tab4:
        st.markdown("### 🗑️ Delete Management")
        
        st.warning("⚠️ **Danger Zone** - Use with caution!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Delete by Criteria")
            


    with tab4:
        st.markdown("### 🗑️ Delete Management")

        st.warning("⚠️ **Danger Zone** - Use with caution!")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Delete by Criteria")


            delete_option = st.selectbox(
                "Select deletion criteria:",
                [
                    "Select...",
                    "Unconfirmed registrations only",
                    "Registrations without location data",
                    "Registrations older than...",
                    "All registrations"
                ]
            )

            
            if delete_option == "Registrations older than...":
                days_old = st.number_input("Delete registrations older than (days):", min_value=1, value=7)
            
            if st.button("🗑️ Delete by Criteria", type="secondary", use_container_width=True):
                if delete_option != "Select...":
                    count = delete_registrations_by_criteria(delete_option, days_old if 'days_old' in locals() else None)


            if delete_option == "Registrations older than...":
                days_old = st.number_input("Delete registrations older than (days):", min_value=1, value=7)

            if st.button("🗑️ Delete by Criteria", type="secondary", use_container_width=True):
                if delete_option != "Select...":
                    count = delete_registrations_by_criteria(delete_option,
                                                             days_old if 'days_old' in locals() else None)

                    if count is not None:
                        if count > 0:
                            st.success(f"✅ Deleted {count} registration(s)")
                            st.rerun()
                        else:
                            st.info("ℹ️ No registrations matched the criteria")
                else:
                    st.error("❌ Please select deletion criteria")
        
        with col2:
            st.markdown("#### Quick Actions")
            


        with col2:
            st.markdown("#### Quick Actions")


            if st.button("🗑️ Delete All Unconfirmed", use_container_width=True, type="secondary"):
                count = delete_registrations_by_criteria("Unconfirmed registrations only")
                if count is not None and count > 0:
                    st.success(f"✅ Deleted {count} unconfirmed registration(s)")
                    st.rerun()
                else:
                    st.info("ℹ️ No unconfirmed registrations found")

            



            if st.button("🗑️ Delete Without Location", use_container_width=True, type="secondary"):
                count = delete_registrations_by_criteria("Registrations without location data")
                if count is not None and count > 0:
                    st.success(f"✅ Deleted {count} registration(s) without location")
                    st.rerun()
                else:
                    st.info("ℹ️ No registrations without location data")

    
    st.divider()
    


    st.divider()


    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.admin_logged_in = False
        st.session_state.page = "landing"
        st.success("✅ Logged out successfully")
        st.rerun()




def delete_registration(registration_id):
    """Delete a specific registration"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                result = conn.execute(
                    text("DELETE FROM registration_form WHERE id = :id"),
                    {"id": registration_id}
                )
                return result.rowcount > 0
        except Exception as e:
            st.error(f"Delete error: {e}")
            return False
    else:
        if registration_id in st.session_state.get("registration_data", {}):
            del st.session_state.registration_data[registration_id]
            return True
        return False





def delete_registrations_by_criteria(criteria, days_old=None):
    """Delete registrations based on criteria"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                if criteria == "Unconfirmed registrations only":
                    result = conn.execute(text("DELETE FROM registration_form WHERE confirmed = FALSE"))
                elif criteria == "Registrations without location data":

                    result = conn.execute(text("DELETE FROM registration_form WHERE latitude IS NULL OR longitude IS NULL"))
                elif criteria == "Registrations older than...":
                    if days_old:
                        if db_type == "PostgreSQL":
                            result = conn.execute(
                                text("DELETE FROM registration_form WHERE created_at < NOW() - INTERVAL ':days days'"),
                                {"days": days_old}
                            )
                        else:
                            result = conn.execute(
                                text("DELETE FROM registration_form WHERE created_at < datetime('now', '-' || :days || ' days')"),
                                {"days": days_old}
                            )
                    result = conn.execute(
                        text("DELETE FROM registration_form WHERE latitude IS NULL OR longitude IS NULL"))
                elif criteria == "Registrations older than...":
                    if days_old:
                        result = conn.execute(
                            text("DELETE FROM registration_form WHERE created_at < NOW() - INTERVAL ':days days'"),
                            {"days": days_old}
                        )

                    else:
                        return None
                elif criteria == "All registrations":
                    result = conn.execute(text("DELETE FROM registration_form"))
                else:
                    return None

                



                return result.rowcount
        except Exception as e:
            st.error(f"Bulk delete error: {e}")
            return None
    else:
        # For in-memory storage
        registration_data = st.session_state.get("registration_data", {})
        initial_count = len(registration_data)

        
        if criteria == "Unconfirmed registrations only":
            st.session_state.registration_data = {
                k: v for k, v in registration_data.items() 


        if criteria == "Unconfirmed registrations only":
            st.session_state.registration_data = {
                k: v for k, v in registration_data.items()

                if v.get('confirmed', False)
            }
        elif criteria == "Registrations without location data":
            st.session_state.registration_data = {

                k: v for k, v in registration_data.items() 

                k: v for k, v in registration_data.items()

                if v.get('latitude') and v.get('longitude')
            }
        elif criteria == "All registrations":
            st.session_state.registration_data = {}

        
        return initial_count - len(st.session_state.get("registration_data", {}))



        return initial_count - len(st.session_state.get("registration_data", {}))



def clear_all_data():
    """Clear all registration data"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                result = conn.execute(text("DELETE FROM registration_form"))
                return True
        except Exception as e:
            st.error(f"Clear all error: {e}")
            return False
    else:
        st.session_state.registration_data = {}
        return True


def export_data():
    """Export registration data to CSV"""
    registrations = get_all_registrations()
    if not registrations:
        st.info("📭 No data to export")
        return False
    


def export_data():
    """Export registration data to CSV"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                result = conn.execute(text("SELECT * FROM registration_form"))
                registrations = result.mappings().fetchall()
        except Exception as e:
            st.error(f"Export error: {e}")
            return False
    else:
        registrations = list(st.session_state.get("registration_data", {}).values())

    if not registrations:
        st.info("📭 No data to export")
        return False


    # Convert to DataFrame
    df_data = []
    for reg in registrations:
        df_data.append({
            "ID": reg.get('id'),
            "First Name": reg.get('first_name', ''),
            "Last Name": reg.get('last_name', ''),
            "Email": reg.get('email', ''),
            "Cell": reg.get('cell', ''),
            "Telephone": reg.get('telephone', ''),
            "Communication Methods": format_array_for_display(reg.get('communication_methods')),
            "Island": reg.get('island', ''),
            "Settlement": reg.get('settlement', ''),
            "Street Address": reg.get('street_address', ''),
            "Interview Methods": format_array_for_display(reg.get('interview_methods')),
            "Available Days": format_array_for_display(reg.get('available_days')),
            "Available Times": format_array_for_display(reg.get('available_times')),
            "Latitude": reg.get('latitude'),
            "Longitude": reg.get('longitude'),
            "GPS Accuracy": reg.get('gps_accuracy'),
            "Location Source": reg.get('location_source', ''),
            "Confirmed": reg.get('confirmed', False),
            "Created At": reg.get('created_at', '')
        })

    
    df = pd.DataFrame(df_data)
    
    # Generate CSV
    csv = df.to_csv(index=False)
    


    df = pd.DataFrame(df_data)

    # Generate CSV
    csv = df.to_csv(index=False)


    # Create download button
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"nacp_registrations_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True
    )

    
    return True



    return True



# =============================
# MAIN APPLICATION
# =============================
def main():
    # Initialize database if needed
    if engine is not None and not st.session_state.get("database_initialized"):
        initialize_database()

    



    # Page routing
    pages = {
        "landing": landing_page,
        "registration": registration_form,
        "availability": availability_form,
        "location_confirmation": location_confirmation_page,
        "final_confirmation": final_confirmation_page,
        "admin_login": admin_login,
        "admin_dashboard": admin_dashboard
    }

    
    current_page = st.session_state.get("page", "landing")
    


    current_page = st.session_state.get("page", "landing")


    # Display the current page
    if current_page in pages:
        pages[current_page]()
    else:
        st.session_state.page = "landing"
        st.rerun()

    


    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
        <i>National Agricultural Census Pilot Project (NACP) - Ministry of Agriculture and Marine Resources - Government of The Bahamas</i>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()



