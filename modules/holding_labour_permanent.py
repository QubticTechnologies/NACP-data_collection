# census_app/modules/holding_labour_permanent.py

import streamlit as st
from sqlalchemy import create_engine, text
from census_app.config import SQLALCHEMY_DATABASE_URI

# ------------------- Database Engine -------------------
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False, future=True)

# ------------------- Dropdown Options -------------------
position_options = {"Manager": '1', "Farm Worker": '2', "Grower": '3',
                    "Office Worker": '4', "Technician": '5'}
sex_options = {"Male": 'M', "Female": 'F'}
age_options = {"15-24": '1', "25-34": '2', "35-44": '3', "45-54": '4', "55-64": '5', "65+": '6'}
nationality_options = {"Bahamian": 'B', "Non-Bahamian": 'NB'}
education_options = {"No Schooling": '1', "Primary": '2', "Junior Secondary": '3', "Senior Secondary": '4',
                     "Undergraduate": '5', "Masters": '6', "Doctorate": '7', "Vocational": '8',
                     "Professional Designation": '9'}
agri_training_options = {"Yes": 'Y', "No": 'N'}
main_duties_options = {"Land Preparation": '1', "Establishment": '2', "Maintenance": '3',
                       "Harvesting/Slaughtering": '4', "Transportation": '5', "Marketing/Management": '6',
                       "Administrative": '7'}
working_time_options = {"None": 'N', "Full time": 'F', "Part time": 'P', "1-3 months": 'P3',
                        "4-6 months": 'P6', "7+ months": 'P7'}

SECTION_NO = 3  # Permanent Workers Section ID


# ------------------- Holder Selector -------------------
def select_holder(agent_id: int):
    """Fetch and select holder assigned to the agent."""
    with engine.begin() as conn:
        holders = conn.execute(
            text("SELECT id, name FROM holders WHERE assigned_agent_id=:agent_id ORDER BY name"),
            {"agent_id": agent_id}
        ).fetchall()

    if not holders:
        st.warning("⚠️ No holders assigned to this agent.")
        return None

    if len(holders) == 1:
        h = holders[0]
        st.info(f"Auto-selected holder: {h.name} (ID: {h.id})")
        return h.id

    holder_options = {f"{h.name} (ID: {h.id})": h.id for h in holders}
    selected_label = st.selectbox("Select Holder", list(holder_options.keys()))
    return holder_options[selected_label]


# ------------------- Mark Section Complete -------------------
def mark_section_complete(holder_id: int):
    """Mark this section as completed in holder_survey_progress."""
    with engine.begin() as conn:
        exists = conn.execute(
            text("SELECT id FROM holder_survey_progress WHERE holder_id=:hid AND section_id=:sec"),
            {"hid": holder_id, "sec": SECTION_NO}
        ).fetchone()
        if exists:
            conn.execute(text("UPDATE holder_survey_progress SET completed=true WHERE id=:id"), {"id": exists[0]})
        else:
            conn.execute(text(
                "INSERT INTO holder_survey_progress(holder_id, section_id, completed) VALUES(:hid, :sec, true)"
            ), {"hid": holder_id, "sec": SECTION_NO})


# ------------------- Permanent Workers Form -------------------
def holding_labour_permanent_form(holder_id: int, max_rows: int = 10):
    st.subheader("Holding Labour - Permanent Workers (Section 3)")

    # Initialize session state
    if "permanent_data" not in st.session_state or st.session_state.selected_holder != holder_id:
        st.session_state.permanent_data = [{} for _ in range(max_rows)]
        st.session_state.selected_holder = holder_id

    # Display input rows
    for i in range(max_rows):
        st.markdown(f"**Worker {i + 1}**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            position = st.selectbox("Position Title", list(position_options.keys()), index=0, key=f"position_{i}")
            sex = st.selectbox("Sex", list(sex_options.keys()), index=0, key=f"sex_{i}")
            age = st.selectbox("Age", list(age_options.keys()), index=0, key=f"age_{i}")
        with col2:
            nationality = st.selectbox("Nationality", list(nationality_options.keys()), index=0, key=f"nationality_{i}")
            education = st.selectbox("Education Level", list(education_options.keys()), index=0, key=f"education_{i}")
        with col3:
            agri_training = st.selectbox("Agricultural Training/Education", list(agri_training_options.keys()), index=0,
                                         key=f"agri_{i}")
            main_duties = st.selectbox("Main Duties", list(main_duties_options.keys()), index=0, key=f"duties_{i}")
        with col4:
            working_time = st.selectbox("Working Time on Holding", list(working_time_options.keys()), index=0,
                                        key=f"worktime_{i}")

        st.session_state.permanent_data[i] = {
            "position_title": position_options[position],
            "sex": sex_options[sex],
            "age_group": age_options[age],
            "nationality": nationality_options[nationality],
            "education_level": education_options[education],
            "agri_training": agri_training_options[agri_training],
            "main_duties": main_duties_options[main_duties],
            "working_time": working_time_options[working_time]
        }

    # Save button
    if st.button("💾 Save Permanent Workers"):
        with engine.begin() as conn:
            # Delete old rows
            conn.execute(text("DELETE FROM holding_labour_permanent WHERE holder_id=:hid"), {"hid": holder_id})
            # Insert new data
            for row in st.session_state.permanent_data:
                conn.execute(text("""
                    INSERT INTO holding_labour_permanent
                    (holder_id, position_title, sex, age_group, nationality, education_level,
                     agri_training, main_duties, working_time)
                    VALUES (:holder_id, :position_title, :sex, :age_group, :nationality, :education_level,
                            :agri_training, :main_duties, :working_time)
                """), {**row, "holder_id": holder_id})
        mark_section_complete(holder_id)
        st.success("✅ Section 3 completed!")


# ------------------- Run Section -------------------
def run_holding_labour_permanent(holder_id: int):
    if not holder_id:
        st.info("Please select a holder to continue.")
        return
    holding_labour_permanent_form(holder_id)
