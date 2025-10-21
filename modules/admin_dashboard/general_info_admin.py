# census_app/modules/admin_dashboard/general_info_admin.py

import streamlit as st
import pandas as pd
from sqlalchemy import text
from census_app.db import engine
from census_app.modules.admin_dashboard.approval import bulk_approve, bulk_reject, bulk_delete

TABLE_NAME = "general_information"

def general_info_admin(filter_status=None, return_df=False):
    st.header("📋 General Information Records")

    # --- Load records ---
    with engine.connect() as conn:
        df = pd.read_sql_query(
            text(f"SELECT * FROM {TABLE_NAME} ORDER BY created_at DESC"),
            conn
        )

    if df.empty:
        st.info("No general information records found.")
        if return_df:
            return df
        return

    # --- Filter by status if provided ---
    if filter_status:
        df = df[df.get("status", "") == filter_status]

    # --- Search ---
    search = st.text_input("🔍 Search by Name, Phone, Email, or Island")
    if search:
        df = df[df.apply(
            lambda row: search.lower() in row.astype(str).str.lower().to_string(),
            axis=1
        )]

    # --- Show table ---
    st.dataframe(df, use_container_width=True)

    # --- Map of records with coordinates ---
    df_map = df.dropna(subset=["latitude", "longitude"])
    if not df_map.empty:
        try:
            df_map["latitude"] = df_map["latitude"].astype(float)
            df_map["longitude"] = df_map["longitude"].astype(float)
            st.subheader("🌍 Map of Holdings")
            st.map(df_map[["latitude", "longitude"]], zoom=7)
        except Exception as e:
            st.warning(f"Could not plot map: {e}")

    # --- Record selection ---
    selected_id = st.selectbox("📌 Select a record to view details", [None] + df["id"].tolist())
    if selected_id:
        record = df[df["id"] == selected_id].iloc[0].to_dict()
        st.subheader(f"🗂️ Record Details (ID: {selected_id})")
        for key, value in record.items():
            st.write(f"**{key.replace('_',' ').title()}**: {value}")

        # Record actions
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🖨️ Print Record"):
                st.markdown("<script>window.print()</script>", unsafe_allow_html=True)
        with col2:
            if st.button("📧 Email Record"):
                st.info(f"Emailing record for {record.get('respondent_name','Unknown')} (simulation).")
        with col3:
            if st.button("✅ Approve Record"):
                bulk_approve(TABLE_NAME, [selected_id])
                st.success("Record approved ✅")
                st.experimental_rerun()

    # --- Bulk Actions ---
    st.subheader("⚡ Bulk Actions")
    selected_ids = st.multiselect("Select multiple records by ID", df["id"].tolist())
    colA, colB, colC, colD = st.columns(4)
    with colA:
        if st.button("✅ Approve Selected"):
            if selected_ids:
                count = bulk_approve(TABLE_NAME, selected_ids)
                st.success(f"{count} records approved.")
                st.experimental_rerun()
            else:
                st.warning("No records selected.")
    with colB:
        if st.button("❌ Reject Selected"):
            if selected_ids:
                count = bulk_reject(TABLE_NAME, selected_ids)
                st.warning(f"{count} records rejected.")
                st.experimental_rerun()
            else:
                st.warning("No records selected.")
    with colC:
        if st.button("🗑️ Delete Selected"):
            if selected_ids:
                count = bulk_delete(TABLE_NAME, selected_ids)
                st.error(f"{count} records deleted.")
                st.experimental_rerun()
            else:
                st.warning("No records selected.")
    with colD:
        if st.button("📧 Email Selected"):
            if selected_ids:
                st.info(f"📨 Sending {len(selected_ids)} record(s) via email (simulation).")
            else:
                st.warning("No records selected.")

    # --- Export Options ---
    st.subheader("📤 Export Data")
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv, "general_info.csv", "text/csv")
    with col2:
        excel_data = df.to_excel(index=False, engine="openpyxl")
        st.download_button(
            "⬇️ Download Excel",
            excel_data,
            "general_info.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    if return_df:
        return df
