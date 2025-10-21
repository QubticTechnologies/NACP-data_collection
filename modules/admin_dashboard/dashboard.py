# census_app/modules/admin_dashboard/admin_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text

from census_app.config import engine
from census_app.modules.admin_dashboard.utils import fetch_table
from census_app.modules.admin_dashboard.alerts import load_alerts, check_alerts
from census_app.modules.admin_dashboard.queries import render_aggrid, apply_conditions, load_templates
from census_app.modules.admin_dashboard.reports import generate_report
from census_app.modules.admin_dashboard.approval import bulk_approve, bulk_reject, bulk_delete
from census_app.modules.admin_dashboard.general_info_admin import general_info_admin

def admin_dashboard():
    st.title("👨‍💼 Admin Dashboard")
    st.write("Welcome, Admin! Manage users, holders, holdings, general information, alerts, and reports here.")

    # ---------------- Navigation Tabs ----------------
    tab = st.radio(
        "Select Action",
        ["Manage Users/Holders", "General Information", "Advanced Query", "Alerts Monitor", "Graphs & Reports"]
    )

    # ---------------- Manage Users/Holders ----------------
    if tab == "Manage Users/Holders":
        for entity, table_name in [("Users", "users"), ("Holders", "holders")]:
            st.subheader(f"{entity} Management")
            df = fetch_table(engine, table_name)
            if df.empty:
                st.info(f"No {entity.lower()} found.")
                continue

            with st.form(key=f"{table_name}_form"):
                selected_ids = render_aggrid(df, grid_key=f"{table_name}_grid")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.form_submit_button(f"Approve Selected {entity}") and selected_ids:
                        bulk_approve(table_name, selected_ids)
                        st.success(f"Approved {len(selected_ids)} {entity.lower()}.")
                        st.rerun()
                with col2:
                    if st.form_submit_button(f"Reject Selected {entity}") and selected_ids:
                        bulk_reject(table_name, selected_ids)
                        st.success(f"Rejected {len(selected_ids)} {entity.lower()}.")
                        st.rerun()
                with col3:
                    if st.form_submit_button(f"Delete Selected {entity}") and selected_ids:
                        bulk_delete(table_name, selected_ids)
                        st.success(f"Deleted {len(selected_ids)} {entity.lower()}.")
                        st.rerun()

    # ---------------- General Information ----------------
    elif tab == "General Information":
        df_general = general_info_admin(return_df=True)
        if df_general is not None and not df_general.empty:
            df_map = df_general.dropna(subset=["latitude", "longitude"])
            if not df_map.empty:
                try:
                    df_map["latitude"] = df_map["latitude"].astype(float)
                    df_map["longitude"] = df_map["longitude"].astype(float)
                    st.subheader("🌍 Map of All Holdings")
                    st.map(df_map[["latitude", "longitude"]], zoom=7)
                except Exception as e:
                    st.warning(f"Could not render map: {e}")
            else:
                st.info("No valid coordinates found for holdings.")

    # ---------------- Advanced Query ----------------
    elif tab == "Advanced Query":
        st.subheader("Advanced Query")
        entity = st.selectbox("Entity", ["Users", "Holders", "General Information"])
        table_map = {"Users": "users", "Holders": "holders", "General Information": "general_information"}
        table = table_map[entity]
        df = fetch_table(engine, table)
        if df.empty:
            st.info(f"No data found for {entity}.")
        else:
            templates = load_templates()
            tpl_names = ["None"] + list(templates.keys())
            selected_tpl = st.selectbox("Load Template", tpl_names)
            filtered = df
            if selected_tpl != "None":
                filtered = apply_conditions(
                    df,
                    templates[selected_tpl]["conditions"],
                    templates[selected_tpl]["connector"]
                )
            selected_ids = render_aggrid(filtered, grid_key=f"{table}_query_grid")
            if not filtered.empty:
                st.download_button(
                    "Download CSV",
                    filtered.to_csv(index=False).encode('utf-8'),
                    f"{table}_query.csv"
                )

    # ---------------- Alerts Monitor ----------------
    elif tab == "Alerts Monitor":
        st.subheader("Alerts Monitor")
        new_alerts = check_alerts(engine, send_notifications=True)
        if new_alerts:
            st.markdown("### 🔥 Newly Triggered Alerts")
            for a in new_alerts:
                st.warning(f"{a}")

        alerts = load_alerts()
        if alerts:
            st.subheader("All Alerts")
            for name, alert in alerts.items():
                st.write(f"- {name}: {alert}")

    # ---------------- Graphs & Reports ----------------
    elif tab == "Graphs & Reports":
        st.subheader("Data Visualizations & Reports")
        entity = st.selectbox("Entity for Graphs/Reports", ["Users", "Holders", "Holdings", "General Information"])
        table_map = {
            "Users": "users",
            "Holders": "holders",
            "Holdings": "holdings",
            "General Information": "general_information"
        }
        table = table_map[entity]
        df = fetch_table(engine, table)
        if df.empty:
            st.info(f"No data found for {entity}.")
        else:
            # ---------- Users Charts ----------
            if entity == "Users" and 'role' in df.columns:
                role_counts = df['role'].value_counts().reset_index()
                role_counts.columns = ['Role', 'Count']
                fig = px.pie(
                    role_counts, values='Count', names='Role',
                    title="User Role Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig)

            # ---------- Holders Charts ----------
            if entity == "Holders" and 'status' in df.columns:
                status_counts = df['status'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']
                fig = px.bar(
                    status_counts, x='Status', y='Count',
                    color='Status',
                    color_discrete_map={'approved': 'green', 'pending': 'orange', 'rejected': 'red'},
                    title="Holder Status Distribution"
                )
                st.plotly_chart(fig)

            # ---------- Holdings Charts ----------
            if entity == "Holdings":
                try:
                    summary_df = generate_report("summary")
                    if not summary_df.empty:
                        st.markdown("### 📊 Holdings Summary")
                        st.dataframe(summary_df)

                    df_map = df.dropna(subset=["latitude", "longitude"])
                    if not df_map.empty:
                        df_map["latitude"] = df_map["latitude"].astype(float)
                        df_map["longitude"] = df_map["longitude"].astype(float)
                        st.subheader("🌍 Map of All Holdings")
                        st.map(df_map[["latitude", "longitude"]], zoom=7)

                    if 'assigned_agent_id' in df.columns:
                        agent_counts = df['assigned_agent_id'].value_counts().reset_index()
                        agent_counts.columns = ['Agent ID', 'Total Holdings']
                        fig2 = px.bar(
                            agent_counts,
                            x='Agent ID',
                            y='Total Holdings',
                            title="Number of Holdings per Agent",
                            text='Total Holdings'
                        )
                        st.plotly_chart(fig2)
                except Exception as e:
                    st.error(f"Error generating holdings charts: {e}")

            # ---------- General Info ----------
            if entity == "General Information":
                st.dataframe(df)

            # ---------- Last 24h Updates ----------
            if 'last_updated' in df.columns:
                df['last_updated'] = pd.to_datetime(df['last_updated'])
                df_recent = df[df['last_updated'] >= pd.Timestamp.now() - pd.Timedelta(hours=24)]
                if not df_recent.empty:
                    st.markdown("### 🕒 Records Updated in Last 24h")
                    st.dataframe(df_recent)

        st.success("Graphs and reports updated in real-time!")
