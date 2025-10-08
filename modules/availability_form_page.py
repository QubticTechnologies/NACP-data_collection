# census_app/modules/availability_form_page.py
import streamlit as st
from census_app.db import SessionLocal
from census_app.models.registration_form import RegistrationForm

def availability_form_page(holder_id=None):
    st.subheader("🕒 Best Time to Visit You")
    st.write("Please select all that apply:")

    if holder_id is None:
        st.warning("Holder ID missing. Selections will not be saved to DB.")

    # --- Days ---
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    selected_days = []
    cols = st.columns(4)
    for i, day in enumerate(days):
        with cols[i % 4]:
            if st.checkbox(day, key=f"day_{day}"):
                selected_days.append(day)

    # --- Time slots ---
    time_slots = [
        "Morning (7 am - 10 am)",
        "Midday (11 am - 1 pm)",
        "Afternoon (2 pm - 5 pm)",
        "Evening (6 pm - 8 pm)"
    ]
    selected_times = []
    cols2 = st.columns(2)
    for i, slot in enumerate(time_slots):
        with cols2[i % 2]:
            if st.checkbox(slot, key=f"time_{slot}"):
                selected_times.append(slot)

    # --- Save button ---
    if st.button("💾 Save Availability"):
        if not selected_days or not selected_times:
            st.warning("Please select at least one day and one time slot.")
            return

        st.success("Selections saved!")

        if holder_id:
            session = SessionLocal()
            try:
                # Fetch existing registration record
                registration = session.query(RegistrationForm).filter_by(holder_id=holder_id).first()
                if registration:
                    registration.available_days = selected_days
                    registration.available_times = selected_times
                    session.commit()
                    st.success("✅ Availability saved to database.")
                else:
                    st.warning("Holder not found in database.")
            except Exception as e:
                session.rollback()
                st.error(f"❌ Error saving availability: {e}")
            finally:
                session.close()

        # Save to session state for confirmation page
        st.session_state.available_days = selected_days
        st.session_state.available_times = selected_times
