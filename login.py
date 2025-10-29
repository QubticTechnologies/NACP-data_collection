import streamlit as st

# --- Hardcoded credentials ---
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# --- Initialize session state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.subheader("🔐 Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.success("✅ Login successful!")
            st.session_state.logged_in = True
        else:
            st.error("❌ Invalid username or password")

def logout():
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

# --- Show login or dashboard ---
if not st.session_state.logged_in:
    login()
else:
    st.write("Welcome, Admin!")
    logout()
    # You can put your admin dashboard code here
    st.write("📊 Dashboard will be displayed here")
