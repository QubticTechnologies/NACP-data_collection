# land_use.py
import streamlit as st
import pandas as pd
import io
from psycopg2.extras import execute_values




import psycopg2

# ---------------- DATABASE CONNECTION ----------------
def get_connection():
    return psycopg2.connect(
        host="localhost",
        dbname="agri_census",
        user="postgres",
        password="sherline10152",
        port=5432
    )

conn = get_connection()





# ---------------- DATABASE FUNCTIONS ----------------

def get_holdings_summary(conn):
    """Fetch summary of all holdings."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT h.id, h.location, h.total_area_acres, COUNT(p.id) AS num_parcels
            FROM land_use h
            LEFT JOIN land_use_parcels p ON h.id = p.land_use_id
            GROUP BY h.id, h.location, h.total_area_acres
            ORDER BY h.id;
        """)
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=["Holding ID", "Location", "Total Area (acres)", "Number of Parcels"])

def get_land_use_data(holding_id, conn):
    """Fetch main info and parcels for a holding."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT total_area_acres, years_agriculture, main_purpose, num_parcels,
                   location, crop_methods
            FROM land_use
            WHERE id = %s;
        """, (holding_id,))
        main_info = cur.fetchone()

        cur.execute("""
            SELECT parcel_no, total_acres, developed_acres, tenure,
                   use_of_land, irrigated_area, land_clearing
            FROM land_use_parcels
            WHERE land_use_id = %s
            ORDER BY parcel_no;
        """, (holding_id,))
        parcels = cur.fetchall()
    return main_info, parcels

def save_land_use(data, conn, holding_id=None):
    """Insert or update a holding and its parcels."""
    try:
        with conn:
            with conn.cursor() as cur:
                if holding_id is None:
                    cur.execute("""
                        INSERT INTO land_use (
                            total_area_acres,
                            years_agriculture,
                            main_purpose,
                            num_parcels,
                            location,
                            crop_methods
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id;
                    """, (
                        data['total_area'],
                        data['years_used'],
                        data['main_purpose'],
                        data['num_parcels'],
                        data['location'],
                        data['crop_methods']
                    ))
                    holding_id = cur.fetchone()[0]
                else:
                    cur.execute("""
                        UPDATE land_use
                        SET total_area_acres=%s,
                            years_agriculture=%s,
                            main_purpose=%s,
                            num_parcels=%s,
                            location=%s,
                            crop_methods=%s
                        WHERE id=%s;
                    """, (
                        data['total_area'],
                        data['years_used'],
                        data['main_purpose'],
                        data['num_parcels'],
                        data['location'],
                        data['crop_methods'],
                        holding_id
                    ))
                    cur.execute("DELETE FROM land_use_parcels WHERE land_use_id=%s;", (holding_id,))

                # Insert parcels
                parcel_values = [
                    (
                        holding_id,
                        p['parcel_no'],
                        p['total_acres'],
                        p['developed_acres'],
                        p['tenure'],
                        p['use_of_land'],
                        p['irrigated_area'],
                        p['land_clearing']
                    )
                    for p in data['parcels']
                ]
                execute_values(cur, """
                    INSERT INTO land_use_parcels (
                        land_use_id,
                        parcel_no,
                        total_acres,
                        developed_acres,
                        tenure,
                        use_of_land,
                        irrigated_area,
                        land_clearing
                    ) VALUES %s;
                """, parcel_values)

                st.success(f"Land Use data saved successfully for holding ID {holding_id} ({'Updated' if holding_id else 'Inserted'}).")
    except Exception as e:
        st.error(f"Error saving Land Use data: {e}")
        conn.rollback()
        raise

# ---------------- VALIDATION FUNCTIONS ----------------

def validate_main_land_use(total_area, years_used, crop_methods, num_parcels, location):
    errors = []
    if total_area <= 0:
        errors.append("Total Area must be greater than 0 acres.")
    if years_used < 0:
        errors.append("Years of agricultural use cannot be negative.")
    if not crop_methods:
        errors.append("At least one Crop Method must be selected.")
    if num_parcels < 1:
        errors.append("Number of Parcels must be at least 1.")
    if not location.strip():
        errors.append("Location cannot be empty.")
    if len(location) > 200:
        errors.append("Location must be 200 characters or less.")
    return errors

def validate_parcels(parcels_df):
    errors = []
    for idx, row in parcels_df.iterrows():
        parcel_no = row["Parcel No."]
        total_acres = row["Total Acres"]
        developed_acres = row["Developed Acres"]
        irrigated_area = row["Irrigated Area (Acres)"]

        if total_acres < 0:
            errors.append(f"Parcel {parcel_no}: Total Acres must be positive.")
        if developed_acres < 0:
            errors.append(f"Parcel {parcel_no}: Developed Acres must be positive.")
        if irrigated_area < 0:
            errors.append(f"Parcel {parcel_no}: Irrigated Area must be positive.")
        if developed_acres > total_acres:
            errors.append(f"Parcel {parcel_no}: Developed Acres cannot exceed Total Acres.")
        if irrigated_area > total_acres:
            st.warning(f"Parcel {parcel_no}: Irrigated Area exceeds Total Acres.")
    return errors

# ---------------- STREAMLIT UI ----------------

st.set_page_config(page_title="Land Use", layout="wide")

st.title("Land Use Section")

# --- Summary Statistics ---
holdings_summary_df = get_holdings_summary(conn)
total_holdings = len(holdings_summary_df)
total_area_all = holdings_summary_df["Total Area (acres)"].sum()
avg_parcels = holdings_summary_df["Number of Parcels"].mean()
max_area = holdings_summary_df["Total Area (acres)"].max()
min_area = holdings_summary_df["Total Area (acres)"].min()

st.subheader("Summary Statistics")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Holdings", total_holdings)
col2.metric("Total Area (acres)", f"{total_area_all:.2f}")
col3.metric("Average Parcels per Holding", f"{avg_parcels:.2f}")
col4.metric("Largest Holding (acres)", f"{max_area:.2f}")
col5.metric("Smallest Holding (acres)", f"{min_area:.2f}")

# --- Search / Filter ---
st.subheader("All Holdings Summary")
search_location = st.text_input("Filter by Location (partial match)")
search_id = st.text_input("Filter by Holding ID (exact match)")

filtered_df = holdings_summary_df.copy()
if search_location.strip():
    filtered_df = filtered_df[filtered_df["Location"].str.contains(search_location.strip(), case=False)]
if search_id.strip():
    if search_id.strip().isdigit():
        filtered_df = filtered_df[filtered_df["Holding ID"] == int(search_id.strip())]
    else:
        st.warning("Holding ID filter must be a number.")

st.dataframe(filtered_df, use_container_width=True)

# --- Export Buttons ---
csv_buffer = io.StringIO()
filtered_df.to_csv(csv_buffer, index=False)
csv_data = csv_buffer.getvalue()

excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
    filtered_df.to_excel(writer, index=False, sheet_name="Holdings Summary")

excel_buffer.seek(0)

col_csv, col_excel = st.columns(2)
with col_csv:
    st.download_button("Download CSV", data=csv_data, file_name="holdings_summary.csv", mime="text/csv")
with col_excel:
    st.download_button("Download Excel", data=excel_buffer, file_name="holdings_summary.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- Select Holding for Edit ---
holding_options = {f"{row['Location']} (ID {row['Holding ID']})": row['Holding ID'] 
                   for _, row in filtered_df.iterrows()}
selected_holding_label = st.selectbox("Select a holding to edit", ["-- New Holding --"] + list(holding_options.keys()))

if selected_holding_label != "-- New Holding --":
    holding_id = holding_options[selected_holding_label]
    main_info, parcels_data = get_land_use_data(holding_id, conn)
    total_area, years_used, main_purpose, num_parcels, location, crop_methods = main_info
    parcels_df = pd.DataFrame(parcels_data, columns=[
        "Parcel No.", "Total Acres", "Developed Acres",
        "Tenure of Land", "Use of Land", "Irrigated Area (Acres)", "Land Clearing Methods"
    ])
    st.session_state.parcels_df = parcels_df
else:
    holding_id = None
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

# --- Land Use Form Fields ---
total_area = st.number_input("Total Area of Holding (acres)", min_value=0.0, value=total_area if holding_id else 0.0, step=0.01)
years_used = st.number_input("Years Land Used for Agriculture", min_value=0.0, value=years_used if holding_id else 0.0, step=0.01)
main_purpose = st.radio("Main Purpose of Holding", ["For Sale Only/Commercial", "Mainly Sale with Some Consumption",
                                                    "For Consumption Only/Subsistence", "Mainly Consumption with Some Sale"],
                        index=["For Sale Only/Commercial","Mainly Sale with Some Consumption","For Consumption Only/Subsistence",
                               "Mainly Consumption with Some Sale"].index(main_purpose) if holding_id else 0)
num_parcels = st.number_input("Number of Parcels", min_value=1, value=num_parcels if holding_id else 1, step=1)
location = st.text_input("Exact Location of Holding (max 200 chars)", max_chars=200, value=location if holding_id else "")
crop_methods = st.multiselect("Crop Methods Used", ["Tunnel", "Open Field", "Net house", "Greenhouse", "Netting", "Other"],
                              default=crop_methods if holding_id else [])

# --- Parcels Table ---
st.subheader("Parcels Table")
edited_df = st.data_editor(st.session_state.parcels_df, num_rows="dynamic")

# --- Submit Button ---
if st.button("Submit Land Use Section"):
    main_errors = validate_main_land_use(total_area, years_used, crop_methods, num_parcels, location)
    parcel_errors = validate_parcels(edited_df)
    all_errors = main_errors + parcel_errors

    if all_errors:
        for error in all_errors:
            st.error(error)
    else:
        # Map ENUMs
        tenure_map = {"Privately Owned": "privately_owned",
                      "Generational/Commonage": "generational_commonage",
                      "Privately Leased/Rented": "privately_leased_rented",
                      "Crown Leased/Rented": "crown_leased_rented",
                      "Squatting on Private Land": "squatting_private_land",
                      "Squatting on Crown Land": "squatting_crown_land",
                      "Borrowed": "borrowed",
                      "Other": "other"}
        use_land_map = {"Temporary Crops": "temporary_crops",
                        "Temporary Meadows and Pastures": "temporary_meadows_pastures",
                        "Temporary Fallow": "temporary_fallow",
                        "Permanent Crops": "permanent_crops",
                        "Permanent Meadows and Pastures": "permanent_meadows_pastures",
                        "Forest & Other Wooded Land": "forest_wooded_land",
                        "Wetland": "wetland",
                        "Farm Buildings & Farmyards": "farm_buildings_yards",
                        "Other": "other"}
        land_clearing_map = {"Regenerative": "regenerative",
                             "Hand Clearing": "hand_clearing",
                             "Slash and burn": "slash_burn",
                             "Small machine": "small_machine",
                             "Large machine": "large_machine"}

        parcels_list = []
        for _, row in edited_df.iterrows():
            parcels_list.append({
                "parcel_no": row["Parcel No."],
                "total_acres": row["Total Acres"],
                "developed_acres": row["Developed Acres"],
                "tenure": tenure_map[row["Tenure of Land"]],
                "use_of_land": use_land_map[row["Use of Land"]],
                "irrigated_area": row["Irrigated Area (Acres)"],
                "land_clearing": land_clearing_map[row["Land Clearing Methods"]]
            })

        data = {"total_area": total_area,
                "years_used": years_used,
                "main_purpose": main_purpose,
                "num_parcels": num_parcels,
                "location": location,
                "crop_methods": crop_methods,
                "parcels": parcels_list}

        save_land_use(data, conn, holding_id)
