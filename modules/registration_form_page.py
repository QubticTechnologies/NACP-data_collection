# census_app/modules/registration_form_page.py
import streamlit as st
from census_app.db import SessionLocal
from census_app.models.registration_form import RegistrationForm

def registration_form_page():
    st.title("🌱 NACP - National Agricultural Census Pilot Project")
    st.subheader("Registration Form")

    # --- Consent ---
    st.write("I understand my information will be kept strictly confidential and used only for statistical purposes.")
    consent_options = ["I do not wish to participate", "I do wish to participate"]
    consent = st.radio("Consent", consent_options)

    if consent == "I do not wish to participate":
        st.warning("You cannot proceed without consenting.")
        return

    # --- Contact Info ---
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email")
    telephone = st.text_input("Telephone Number")
    cell = st.text_input("Cell Number")

    # --- Preferred Communication ---
    st.write("Preferred Communication (Select all that apply)")
    methods = ["WhatsApp", "Phone Call", "Email", "Text Message"]
    selected_methods = []
    cols = st.columns(2)
    for i, method in enumerate(methods):
        with cols[i % 2]:
            if st.checkbox(method, key=f"method_{method}"):
                selected_methods.append(method)

    # --- Location ---
    ISLANDS = [
        "New Providence", "Grand Bahama", "Abaco", "Acklins", "Andros", "Berry Islands",
        "Bimini", "Cat Island", "Crooked Island", "Eleuthera", "Exuma",
        "Inagua", "Long Island", "Mayaguana", "Ragged Island", "Rum Cay", "San Salvador"
    ]
    island_selected = st.selectbox("Which Island is your agricultural activity on?", ISLANDS)

    SETTLEMENTS = {
        "New Providence": ["Nassau", "Other"],
        "Grand Bahama": ["Freeport", "West End", "Other"],
        "Abaco": ["Marsh Harbour", "Hope Town", "Other"],
        # Add remaining islands here...
    }
    settlement_selected = st.selectbox("Settlement/District", SETTLEMENTS.get(island_selected, ["Other"]))

    # --- Follow-Up Preference ---
    st.write("Preferred Form for Follow-Up (Select all that apply)")
    follow_up_options = ["Telephone Interview", "In Person", "Self Registration"]
    follow_up_selected = []
    cols_fu = st.columns(2)
    for i, option in enumerate(follow_up_options):
        with cols_fu[i % 2]:
            if st.checkbox(option, key=f"followup_{option}"):
                follow_up_selected.append(option)

    # --- Latitude & Longitude ---
    latitude = st.text_input("Latitude")
    longitude = st.text_input("Longitude")

    # --- Save Button ---
    if st.button("💾 Save Registration"):
        if not all([first_name, last_name, email, selected_methods, island_selected, settlement_selected]):
            st.warning("Please fill all required fields and select at least one communication method.")
            return

        session = SessionLocal()
        try:
            # Create new registration record
            registration = RegistrationForm(
                consent=consent,
                first_name=first_name,
                last_name=last_name,
                email=email,
                telephone=telephone,
                cell=cell,
                communication_methods=selected_methods,
                island=island_selected,
                settlement=settlement_selected,
                latitude=float(latitude) if latitude else None,
                longitude=float(longitude) if longitude else None,
                follow_up=follow_up_selected
            )
            session.add(registration)
            session.commit()
            st.success("✅ Registration information saved successfully!")
        except Exception as e:
            session.rollback()
            st.error(f"❌ Error saving registration: {e}")
        finally:
            session.close()
