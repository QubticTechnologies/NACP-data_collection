# census_app/modules/auth.py

import streamlit as st
from sqlalchemy import text
from census_app.db import engine
from census_app.modules.user_utils import register_user_logic, login_user_logic
from census_app.modules.survey_sidebar import survey_sidebar
from census_app.modules.holder_info import show_holder_dashboard
from census_app.config import TOTAL_SURVEY_SECTIONS
import pandas as pd


# --------------------- Streamlit-Safe Holder Creation ---------------------
def create_holder_for_user(user_id, username):
    """Ensure holder exists for user; prompt location if new. Uses session_state to prevent duplicates."""
    if st.session_state.get(f"holder_id_{user_id}"):
        return st.session_state[f"holder_id_{user_id}"]

    with engine.begin() as conn:
        exists = conn.execute(
            text("SELECT holder_id, latitude, longitude FROM holders WHERE owner_id=:uid"),
            {"uid": user_id}
        ).mappings().first()

        if exists:
            st.session_state[f"holder_id_{user_id}"] = exists["holder_id"]
            return exists["holder_id"]

    # Prompt user for location if holder does not exist
    st.info(f"📍 Please select your location on the map for {username}.")
    df = pd.DataFrame([[0.0, 0.0]], columns=["lat", "lon"])
    st.map(df)

    latitude = st.number_input("Latitude", value=0.0, step=0.000001, key=f"lat_{user_id}")
    longitude = st.number_input("Longitude", value=0.0, step=0.000001, key=f"lon_{user_id}")

    if st.button("Save Holder Location", key=f"save_holder_{user_id}"):
        with engine.begin() as conn:
            result = conn.execute(
                text("""
                    INSERT INTO holders (name, owner_id, status, submitted_at, latitude, longitude)
                    VALUES (:name, :owner_id, 'active', NOW(), :lat, :lon)
                    RETURNING holder_id
                """),
                {"name": username, "owner_id": user_id, "lat": latitude, "lon": longitude}
            )
            holder_id = result.scalar_one()

            # Initialize survey progress
            for sec in range(1, TOTAL_SURVEY_SECTIONS + 2):
                conn.execute(
                    text("""
                        INSERT INTO holder_survey_progress (holder_id, section_id, completed)
                        VALUES (:hid, :sec, FALSE)
                    """),
                    {"hid": holder_id, "sec": sec}
                )

        st.success("📌 Holder created successfully with location!")
        st.session_state[f"holder_id_{user_id}"] = holder_id
        st.experimental_rerun()

    st.stop()


# --------------------- Registration Form ---------------------
def register_user():
    st.subheader("📝 Register")

    username = st.text_input("Username", key="reg_username")
    email = st.text_input("Email", key="reg_email")
    password = st.text_input("Password", type="password", key="reg_password")
    role = st.selectbox("Role", ["Holder", "Agent"], key="reg_role")

    if st.button("Register", key="register_btn"):
        if not username or not password or not email:
            st.error("⚠️ All fields are required.")
            return

        # Register user (password hashing happens inside register_user_logic)
        user_id, msg = register_user_logic(username, email, password, role)

        if user_id:
            st.success(msg)
            # Store user in session_state immediately
            st.session_state["user"] = {
                "id": user_id,
                "username": username,
                "role": role
            }

            # Redirect to dashboard; holder location setup deferred
            st.session_state["page"] = "holder_dashboard" if role.lower() == "holder" else "landing"
            st.rerun()
        else:
            st.error(msg)


# --------------------- Login Form ---------------------
def login_user(role=None):
    st.subheader("🔑 Login")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if role:
        st.info(f"Logging in as: {role}")

    if st.button("Login", key="login_btn"):
        if not username or not password:
            st.error("⚠️ Username and password are required.")
            return

        success, msg, session_info = login_user_logic(username, password, role=role)

        if success:
            st.session_state["user"] = {
                "id": session_info["user_id"],
                "username": session_info["username"],
                "role": session_info["user_role"]
            }

            # Redirect to holder dashboard or agent dashboard
            st.session_state["page"] = "holder_dashboard" if session_info["user_role"].lower() == "holder" else "agent_dashboard"

            st.success(msg)
            st.rerun()
        else:
            st.error(msg)


# --------------------- Logout ---------------------
def logout_user():
    if st.button("🚪 Logout", key="logout_btn"):
        for key in ["user", "page"]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state["logged_out"] = True
        st.success("Logged out successfully!")
        st.rerun()


# --------------------- Sidebar Wrapper ---------------------
def auth_sidebar():
    """Sidebar for auth + holder dashboard integration"""
    if not st.session_state.get("user"):
        survey_sidebar(holder_id=None)
        login_user()
        st.write("---")
        register_user()
    else:
        user_role = st.session_state["user"]["role"]
        user_id = st.session_state["user"]["id"]

        if user_role.lower() == "holder":
            # Only now call create_holder_for_user on first login
            holder_id = create_holder_for_user(user_id, st.session_state["user"]["username"])
            show_holder_dashboard(holder_id)
            survey_sidebar(holder_id=holder_id)
        else:
            survey_sidebar(holder_id=None)

        st.write(f"👤 Logged in as: **{st.session_state['user']['username']}** ({user_role})")
        logout_user()
