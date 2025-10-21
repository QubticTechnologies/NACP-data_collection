# census_app/modules/admin_auth.py
import streamlit as st
from sqlalchemy import text
from census_app.db import engine
from census_app.helpers import verify_password  # make sure helpers has verify_password

# Constants
USERS_TABLE = "users"
ROLE_ADMIN = "Admin"


def login_admin():
    """
    Display admin login form.
    Updates session_state on successful login and navigates to dashboard.
    """
    st.subheader("Admin Login")

    username = st.text_input("Admin Username", key="admin_username")
    password = st.text_input("Password", type="password", key="admin_password")

    if st.button("Login as Admin"):
        if not username or not password:
            st.error("Please enter both username and password.")
            return

        try:
            with engine.connect() as conn:
                query = text(f"""
                    SELECT * FROM {USERS_TABLE}
                    WHERE username=:username AND role=:role
                """)
                result = conn.execute(query, {"username": username, "role": ROLE_ADMIN}).mappings().first()

                if result:
                    # Verify password hash
                    if verify_password(password, result["password_hash"]):
                        # Store admin user in session_state as dict
                        st.session_state["user"] = {
                            "id": result["id"],
                            "username": result["username"],
                            "role": ROLE_ADMIN
                        }
                        st.session_state["page"] = "admin_dashboard"  # navigate to dashboard
                        st.success(f"Logged in as Admin {username}")
                        st.rerun()  # refresh page to show dashboard
                    else:
                        st.error("Invalid admin username or password.")
                else:
                    st.error("Invalid admin username or password.")

        except Exception as e:
            st.error(f"Admin login error: {e}")


def admin_dashboard():
    """
    Admin dashboard placeholder content.
    Customize this with actual functionality.
    """
    st.title("Admin Dashboard")
    st.info("Welcome to the Admin Dashboard!")
    st.write("Here you can manage users, view census data, and export reports.")
