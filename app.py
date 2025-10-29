import streamlit as st
from sqlalchemy import text
from db import engine

if "page" not in st.session_state:
    st.session_state.page = "personal_info"

# ---------------------------
# STEP 1: Personal Information
# ---------------------------
def personal_info_page():
    st.title("🧾 Registration Form - Step 1")
    st.session_state.name = st.text_input("Full Name", st.session_state.get("name", ""))
    st.session_state.phone = st.text_input("Phone Number", st.session_state.get("phone", ""))
    st.session_state.email = st.text_input("Email Address", st.session_state.get("email", ""))
    st.session_state.address = st.text_area("Home Address", st.session_state.get("address", ""))
    if st.button("Next ➡️"):
        if not st.session_state.name or not st.session_state.phone:
            st.warning("Please fill name and phone number.")
        else:
            st.session_state.page = "availability"

# ---------------------------
# STEP 2: Availability
# ---------------------------
def availability_page():
    st.title("📅 Registration Form - Step 2")
    st.write("Please select all that apply:")
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    times = [
        "Morning (7 am - 10 am)",
        "Midday (11 am - 1 pm)",
        "Afternoon (2 pm - 5 pm)",
        "Evening (6 pm - 8 pm)"
    ]
    selected_days = [d for d in days if st.checkbox(d, key=f"day_{d}")]
    selected_times = [t for t in times if st.checkbox(t, key=f"time_{t}")]
    if st.button("Next ➡️"):
        if not selected_days or not selected_times:
            st.warning("Select at least one day and one time slot.")
        else:
            st.session_state.selected_days = selected_days
            st.session_state.selected_times = selected_times
            st.session_state.page = "confirmation"

# ---------------------------
# STEP 3: Confirmation & Save
# ---------------------------
def confirmation_page():
    st.title("✅ Confirm Your Registration")
    st.write(f"**Full Name:** {st.session_state.name}")
    st.write(f"**Phone:** {st.session_state.phone}")
    st.write(f"**Email:** {st.session_state.email}")
    st.write(f"**Address:** {st.session_state.address}")
    st.write(f"**Days Available:** {', '.join(st.session_state.selected_days)}")
    st.write(f"**Times Available:** {', '.join(st.session_state.selected_times)}")

    if st.button("💾 Save to Database"):
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO registration_form (
                    full_name, phone, email, address, days_available, times_available
                ) VALUES (:n, :p, :e, :a, :d, :t)
            """), {
                "n": st.session_state.name,
                "p": st.session_state.phone,
                "e": st.session_state.email,
                "a": st.session_state.address,
                "d": st.session_state.selected_days,
                "t": st.session_state.selected_times
            })
        st.success("✅ Registration saved successfully!")

# ---------------------------
# PAGE ROUTING
# ---------------------------
if st.session_state.page == "personal_info":
    personal_info_page()
elif st.session_state.page == "availability":
    availability_page()
elif st.session_state.page == "confirmation":
    confirmation_page()
