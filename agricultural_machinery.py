# agricultural_machinery.py
import streamlit as st
import psycopg2
from psycopg2.extras import execute_values

# ---------------- DATABASE CONNECTION ----------------
def get_connection():
    """Return a psycopg2 connection to PostgreSQL."""
    return psycopg2.connect(
        host="localhost",
        dbname="agri_census",
        user="postgres",
        password="yourpassword",
        port=5432
    )

# ---------------- SAVE TO DATABASE ----------------
def save_to_db(machinery_data):
    """Insert machinery data into the agricultural_machinery table."""
    conn = get_connection()
    cur = conn.cursor()

    insert_query = """
        INSERT INTO agricultural_machinery
        (holder_id, has_item, equipment_name, quantity_new, quantity_used, quantity_out_of_service, source)
        VALUES %s
    """

    values = [
        (
            row["holder_id"],
            row["has_item"],
            row["equipment_name"],
            row["quantity_new"],
            row["quantity_used"],
            row["quantity_out_of_service"],
            row["source"],
        )
        for row in machinery_data
    ]

    execute_values(cur, insert_query, values)
    conn.commit()
    cur.close()
    conn.close()

# ---------------- AGRICULTURAL MACHINERY SECTION ----------------
def agricultural_machinery_section(holder_id):
    """Display the Agricultural Machinery form and save to DB."""
    st.subheader("Agricultural Machinery")
    st.markdown(
        "**For the items listed below, report the number of machinery and equipment on the holdings on July 31, 2025.**"
    )

    # Predefined equipment rows
    equipment_list = [
        "Small Engine Machines (e.g. pole-saw, push mower, weed wacker, auger etc.)",
        "Tractors (below 100 horsepower)",
        "Tractors (100 horsepower or greater)",
        "Sprayers and dusters",
        "Trucks (including pickups)",
        "Cars / Jeeps / Station Wagons",
        "Other (specify 1)",
        "Other (specify 2)",
        "Other (specify 3)"
    ]

    machinery_data = []

    # Streamlit form for submission
    with st.form("machinery_form"):
        for idx, equipment in enumerate(equipment_list, start=1):
            st.markdown(f"### {idx}. {equipment}")

            col1, col2, col3, col4, col5 = st.columns([1, 3, 1, 1, 1])

            # Yes / No
            with col1:
                has_item = st.radio(
                    "",
                    ["Y", "N"],
                    horizontal=True,
                    key=f"has_{equipment}"
                )

            # Equipment Name (editable only for "Other" rows)
            with col2:
                if "Other" in equipment:
                    equipment_name = st.text_input(
                        "Specify other equipment",
                        max_chars=100,
                        key=f"equip_{equipment}"
                    )
                else:
                    equipment_name = equipment
                    st.markdown(f"**{equipment}**")  # display fixed text

            # Quantity: New / Used / Out of Service
            with col3:
                qty_new = st.number_input(
                    "New", min_value=0, max_value=20, step=1, key=f"new_{equipment}"
                )
            with col4:
                qty_used = st.number_input(
                    "Used", min_value=0, max_value=20, step=1, key=f"used_{equipment}"
                )
            with col5:
                qty_out = st.number_input(
                    "Out of Service", min_value=0, max_value=20, step=1, key=f"out_{equipment}"
                )

            # Source
            source = st.radio(
                "Source",
                ["O", "RL", "B"],
                horizontal=True,
                key=f"source_{equipment}"
            )

            # Append row to data list
            machinery_data.append({
                "holder_id": holder_id,
                "has_item": has_item,
                "equipment_name": equipment_name,
                "quantity_new": qty_new,
                "quantity_used": qty_used,
                "quantity_out_of_service": qty_out,
                "source": source,
            })

        # Submit button
        submitted = st.form_submit_button("💾 Save Machinery Data")

        if submitted:
            save_to_db(machinery_data)
            st.success("✅ Agricultural machinery data saved successfully!")
            st.balloons()

    return machinery_data
