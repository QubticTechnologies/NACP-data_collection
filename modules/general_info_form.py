# census_app/modules/general_info_form.py
import streamlit as st
from datetime import date
from sqlalchemy import text
from census_app.db import engine

# Optional: import streamlit_javascript for browser geolocation
try:
    from streamlit_javascript import st_javascript
    JS_ENABLED = True
except ImportError:
    JS_ENABLED = False

# List of islands in the Bahamas
ISLANDS = [
    "New Providence", "Grand Bahama", "Abaco", "Acklins", "Andros", "Berry Islands",
    "Bimini", "Cat Island", "Crooked Island", "Eleuthera", "Exuma",
    "Inagua", "Long Island", "Mayaguana", "Ragged Island", "Rum Cay", "San Salvador"
]

def general_info_form(holder_id=None):
    st.subheader("📋 General Information Form")

    if holder_id is None:
        st.error("❌ holder_id is missing. Cannot show General Information form.")
        return False

    # --- Fetch holder info from DB ---
    holder_name_default = ""
    holding_id_default = ""
    latitude_input_default = ""
    longitude_input_default = ""
    with engine.begin() as conn:
        holder_info = conn.execute(
            text("SELECT holder_id, name, farm_id, latitude, longitude FROM holders WHERE holder_id = :hid"),
            {"hid": holder_id}
        ).mappings().fetchone()
        if holder_info:
            holder_name_default = holder_info["name"]
            holding_id_default = holder_info["farm_id"]
            latitude_input_default = holder_info["latitude"]
            longitude_input_default = holder_info["longitude"]

    # --- Auto-fetch coordinates via JS if available ---
    if JS_ENABLED and (not latitude_input_default or not longitude_input_default):
        coords = st_javascript("navigator.geolocation.getCurrentPosition(pos => pos.coords)")
        if coords:
            latitude_input_default = coords.get("latitude", "")
            longitude_input_default = coords.get("longitude", "")

    with st.form(f"general_info_form_{holder_id}"):
        # --- Basic Info ---
        holding_id_input = st.text_input("Holding 10-digit ID", value=holding_id_default)
        interview_date_input = st.date_input("Interview Date", value=date.today())
        respondent_name_input = st.text_input("Respondent Name")
        respondent_phone_input = st.text_input("Respondent Phone")
        respondent_email_input = st.text_input("Respondent Email")

        # --- Holder Confirmation ---
        is_holder_input = st.checkbox("Are you (one of) the holder(s)?", value=True)
        holder_name_input = st.text_input("Holder Name", value=holder_name_default)
        holder_phone_input = st.text_input("Holder Phone (N/A if not applicable)")
        holding_name_input = st.text_input("Holding Name (if applicable)")
        holding_phone_input = st.text_input("Holding Phone (e.g. (242) 999-9999)")

        # --- Location ---
        st.markdown("### 📍 Location Information")
        island_input = st.selectbox("Island", ISLANDS)
        area_city_input = st.text_input("Area/City (official name)")
        subdivision_input = st.text_input("Subdivision")
        city_province_input = st.text_input("City/Province/Settlement")
        latitude_input = st.text_input("Latitude", value=latitude_input_default)
        longitude_input = st.text_input("Longitude", value=longitude_input_default)
        address_street_input = st.text_input("Street Address")
        address_po_input = st.text_input("P.O. Box", value="N-59195")

        # --- Legal Status ---
        st.markdown("### 🏠 Legal Status of Holder")
        legal_status_input = st.radio("Legal Status", ["Household", "Non-Household"])
        household_status_input = None
        nonhouse_status_input = None

        if legal_status_input == "Household":
            household_status_input = st.radio("Select Household Type", ["Individual", "Joint-Family", "Joint-Partnership"])
        else:
            nonhouse_status_input = st.radio(
                "Select Non-Household Type",
                ["Corporation", "Government Institution", "Educational Institution", "Church", "Cooperative", "Other"]
            )

        # --- Submit Button ---
        submitted = st.form_submit_button("💾 Save & Go to Survey")

        if submitted:
            # --- Validate required fields ---
            required_fields = {
                "Holding ID": holding_id_input,
                "Respondent Name": respondent_name_input,
                "Holder Name": holder_name_input,
                "Island": island_input,
                "Area/City": area_city_input,
                "City/Province": city_province_input,
                "Street Address": address_street_input,
                "Legal Status": legal_status_input
            }
            missing_fields = [k for k, v in required_fields.items() if not v]
            if missing_fields:
                st.error(f"⚠️ Please fill all required fields: {', '.join(missing_fields)}")
                return False

            # --- Save to DB ---
            with engine.begin() as conn:
                query = text("""
                    INSERT INTO general_information (
                        holder_id, holding_id, interview_date, respondent_name,
                        respondent_phone, respondent_email, is_holder,
                        holder_name, holder_phone, holding_name, holding_phone,
                        island, area, subdivision, city, latitude,
                        longitude, address_street, address_po, legal_status
                    )
                    VALUES (
                        :holder_id, :holding_id, :interview_date, :respondent_name,
                        :respondent_phone, :respondent_email, :is_holder,
                        :holder_name, :holder_phone, :holding_name, :holding_phone,
                        :island, :area, :subdivision, :city, :latitude,
                        :longitude, :address_street, :address_po, :legal_status
                    )
                """)
                conn.execute(query, {
                    "holder_id": holder_id,
                    "holding_id": holding_id_input,
                    "interview_date": interview_date_input,
                    "respondent_name": respondent_name_input,
                    "respondent_phone": respondent_phone_input,
                    "respondent_email": respondent_email_input,
                    "is_holder": is_holder_input,
                    "holder_name": holder_name_input,
                    "holder_phone": holder_phone_input,
                    "holding_name": holding_name_input,
                    "holding_phone": holding_phone_input,
                    "island": island_input,
                    "area": area_city_input,
                    "subdivision": subdivision_input,
                    "city": city_province_input,
                    "latitude": latitude_input,
                    "longitude": longitude_input,
                    "address_street": address_street_input,
                    "address_po": address_po_input,
                    "legal_status": legal_status_input
                })

            st.success("✅ General Information saved successfully. Proceed to survey.")
            return True

    return False
