# census_app/modules/user_utils.py

import streamlit as st
from sqlalchemy import text
from db import engine
import bcrypt
from config import USERS_TABLE, ROLE_HOLDER, ROLE_ADMIN, STATUS_ACTIVE, STATUS_PENDING, STATUS_APPROVED

# --------------------- Password Utilities ---------------------
def hash_password(password: str | bytes) -> str:
    """Hash a password safely for storage. Accepts str or bytes."""
    if isinstance(password, str):
        password = password.encode("utf-8")
    return bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str | bytes, hashed: str | bytes) -> bool:
    """Verify a password against a hashed value safely. Accepts str or bytes."""
    if isinstance(password, str):
        password = password.encode("utf-8")
    if isinstance(hashed, str):
        hashed = hashed.encode("utf-8")
    return bcrypt.checkpw(password, hashed)


# --------------------- User Registration ---------------------
def register_user_logic(username: str, email: str, password: str | bytes, role: str):
    """Register a new user with hashed password."""
    if not username or not email or not password:
        return False, "All fields are required!"

    try:
        password_hash = hash_password(password)
        status = STATUS_ACTIVE if role == ROLE_HOLDER else STATUS_PENDING

        with engine.begin() as conn:
            query = text(f"""
                INSERT INTO {USERS_TABLE} (username, email, password_hash, role, status, timestamp)
                VALUES (:username, :email, :password_hash, :role, :status, now())
                RETURNING id
            """)
            result = conn.execute(query, {
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "role": role,
                "status": status
            })
            user_id = result.scalar_one()  # Returns the new user's ID

        return user_id, f"Registered {role} successfully!"
    except Exception as e:
        return False, f"Registration error: {e}"


# --------------------- User Login ---------------------
def login_user_logic(username: str, password: str | bytes, role: str = None):
    """
    Login logic with optional role filtering.
    Returns: (success: bool, message: str, session_info: dict|None)
    """
    if not username or not password:
        return False, "Please enter both username and password.", None

    try:
        with engine.connect() as conn:
            query = text(f"SELECT * FROM {USERS_TABLE} WHERE username=:username")
            result = conn.execute(query, {"username": username}).mappings().first()

            if not result:
                return False, "Username not found.", None

            # Role check
            if role and result["role"] != role:
                return False, f"User role does not match '{role}'.", None

            # Password verification
            if not verify_password(password, result["password_hash"]):
                return False, "Invalid password.", None

            # Status check (except admin)
            if result["role"] != ROLE_ADMIN and result["status"] != STATUS_APPROVED:
                return False, f"User status is '{result['status']}'. Cannot login yet.", None

            session_info = {
                "user_id": result["id"],
                "username": result["username"],
                "user_role": result["role"]
            }

            return True, "Login successful!", session_info

    except Exception as e:
        return False, f"Login error: {e}", None


# --------------------- Session Reset (Logout) ---------------------
def reset_session():
    """Reset Streamlit session state for logout."""
    for key in [
        "logged_in",
        "user_role",
        "user_id",
        "username",
        "next_survey_section",
        "user",
        "page"
    ]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state["logged_out"] = True
