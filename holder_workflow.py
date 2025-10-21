import streamlit as st
import pandas as pd
from census_app.holding_labour import holding_labour_form
from census_app.land_use import save_land_use, validate_main_land_use, validate_parcels
from census_app.agricultural_machinery import agricultural_machinery_section
#from census_app.holder_info import holding_info_section
#from census_app.livestock import livestock_section

SECTION_MAP = {
    1: "holder information",
    2: "household information",
    3: "holding labour",
    4: "holding permanent labour",
    5: "agricultural machinery"
}

def render_holder_section():
    """Render the current section based on st.session_state['current_section']"""
    current_section = st.session_state.get("current_section", 1)
    st.subheader(f"Step {current_section}: {SECTION_MAP[current_section]}")
    holder_id = st.session_state.get("user_id")

    # ---------------- LABOUR ----------------
    if current_section == 1:
        holding_labour_form(holder_id)

    # ---------------- LAND USE ----------------
    elif current_section == 2:
        if "parcels_df" not in st.session_state:
            st.session_state.parcels_df = pd.DataFrame({
                "Parcel No.": [1],
                "Total Acres": [0.0],
                "Developed Acres": [0.0],
                "Tenure of Land": ["Privately Owned"],
                "Use of Land": ["Temporary Crops"],
                "Irrigated Area (Acres)": [0.0],
                "Land Clearing Methods": ["Regenerative"]
            })

        total_area = st.number_input("Total Area of Holding (acres)", min_value=0.0,
                                     value=st.session_state.get("total_area", 0.0), step=0.01)
        years_used = st.number_input("Years Land Used for Agriculture", min_value=0.0,
                                     value=st.session_state.get("years_used", 0.0), step=0.01)
        main_purpose = st.radio(
            "Main Purpose of Holding",
            ["For Sale Only/Commercial", "Mainly Sale with Some Consumption",
             "For Consumption Only/Subsistence", "Mainly Consumption with Some Sale"],
            index=st.session_state.get("main_purpose_idx", 0)
        )
        num_parcels = st.number_input("Number of Parcels", min_value=1,
                                      value=st.session_state.get("num_parcels", 1), step=1)
        location = st.text_input("Exact Location of Holding (max 200 chars)",
                                 max_chars=200, value=st.session_state.get("location", ""))
        crop_methods = st.multiselect(
            "Crop Methods Used",
            ["Tunnel", "Open Field", "Net house", "Greenhouse", "Netting", "Other"],
            default=st.session_state.get("crop_methods", [])
        )

        st.subheader("Parcels Table")
        edited_df = st.experimental_data_editor(st.session_state.parcels_df, num_rows="dynamic")

        if st.button("Save Land Use Data"):
            main_errors = validate_main_land_use(total_area, years_used, crop_methods, num_parcels, location)
            parcel_errors = validate_parcels(edited_df)
            all_errors = main_errors + parcel_errors

            if all_errors:
                for error in all_errors:
                    st.error(error)
            else:
                save_land_use({
                    "total_area": total_area,
                    "years_used": years_used,
                    "main_purpose": main_purpose,
                    "num_parcels": num_parcels,
                    "location": location,
                    "crop_methods": crop_methods,
                    "parcels": edited_df.to_dict(orient="records")
                }, None, holding_id=holder_id)
                st.success("✅ Land use data saved!")

    # ---------------- LIVESTOCK ----------------
    elif current_section == 3:
        livestock_section(holder_id)

    # ---------------- AGRICULTURAL MACHINERY ----------------
    elif current_section == 4:
        agricultural_machinery_section(holder_id)

    # ---------------- CROPS ----------------
    elif current_section == 5:
        crops_section(holder_id)

    # ---------------- Navigation Buttons ----------------
    col_back, col_next = st.columns(2)
    with col_back:
        if current_section > 1:
            if st.button("⬅ Back Section"):
                st.session_state.current_section -= 1
                st.stop()  # triggers rerun
    with col_next:
        if current_section < len(SECTION_MAP):
            if st.button("Next Section ➡"):
                st.session_state.current_section += 1
                st.stop()  # triggers rerun
        else:
            st.info("✅ Last section. Submit all data when done.")
