# census_app/modules/admin_dashboard/admin_sidebar.py

import streamlit as st

def admin_sidebar():
    st.sidebar.title("👨‍💼 Admin Panel")

    # ----------------- User Info -----------------
    if "user_name" in st.session_state:
        st.sidebar.write(f"Logged in as: **{st.session_state['user_name']}**")
        st.sidebar.write(f"Role: **{st.session_state.get('user_role','Unknown')}**")
    else:
        st.sidebar.warning("Not logged in")

    st.sidebar.markdown("---")

    # ----------------- Navigation -----------------
    st.sidebar.subheader("Navigation")
    tab = st.sidebar.radio(
        "Go to",
        ["Manage Users/Holders", "General Information", "Advanced Query", "Alerts Monitor", "Graphs & Reports"]
    )
    st.session_state["admin_tab"] = tab

    # ----------------- Quick Actions -----------------
    st.sidebar.subheader("Quick Actions")
    if tab == "Manage Users/Holders":
        st.sidebar.info("Approve, reject, or delete users and holders.")
    elif tab == "General Information":
        st.sidebar.info("View, approve, reject, email, or export general information records.")
    elif tab == "Advanced Query":
        st.sidebar.info("Run queries and download CSV/Excel reports.")
    elif tab == "Alerts Monitor":
        st.sidebar.info("Check recent and all system alerts.")
    elif tab == "Graphs & Reports":
        st.sidebar.info("View data visualizations and summary reports.")

    # ----------------- Session Controls -----------------
    st.sidebar.markdown("---")
    if st.sidebar.button("🔒 Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.experimental_rerun()
