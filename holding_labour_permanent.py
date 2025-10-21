# census_app/modules/holding_labour_permanent.py

import streamlit as st
from sqlalchemy import create_engine, text
from census_app.config import (
    SQLALCHEMY_DATABASE_URI,
    POSITION_OPTIONS,
    SEX_OPTIONS_PERM,
    AGE_OPTIONS,
    NATIONALITY_OPTIONS_PERM,
    EDUCATION_OPTIONS_PERM,
    AG_TRAINING_OPTIONS_PERM,
    MAIN_DUTIES_OPTIONS,
    WORKING_TIME_OPTIONS_PERM
)

# ------------------- Database Engine -------------------
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False, future=True)

SECTION_NO = 3  # Permanent Workers Section

# ------------------- Mark Section Complete -------------------
def mark_section_complete(holder_id: int):
    """Mark this section as completed in holder_survey_progress."""
    with engine.begin() as conn:
        exists = conn.execute(
            text("SELECT id FROM holder_survey_progress WHERE holder_id=:hid AND section_id=:sec"),
            {"hid": holder_id, "sec": SECTION_NO}
        ).fetchone()
        if exists:
            conn.execute(
                text("UPDATE holder_survey_progress SET completed=true WHERE id=:id"),
                {"id": exists[0]}
            )
        else:
            conn.execute(
                text("INSERT INTO holder_survey_progress(holder_id, section_id, completed) VALUES(:hid, :sec, true)"),
                {"hid": holder_id, "sec": SECTION_NO}
            )

# ------------------- Load Existing Permanent Workers -------------------
def load_permanent_workers(holder_id: int):
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT * FROM holding_labour_permanent WHERE holder_id=:hid ORDER BY id"),
            {"hid": holder_id}
        ).mappings().all()
    return [dict(r) for r in rows]

# ------------------- Permanent Workers Form -------------------
def holding_labour_permanent_form(holder_id: int, max_rows: int = 10):
    st.subheader("Holding Labour - Permanent Workers (Section 3)")

    # Load saved data
    if "permanent_data" not in st.session_state or st.session_state.selected_holder != holder_id:
        saved_data = load_permanent_workers(holder_id)
        # Fill missing rows if less than max_rows
        st.session_state.permanent_data = saved_data + [{} for _ in range(max_rows - len(saved_data))]
        st.session_state.selected_holder = holder_id

    # Display input rows
    for i in range(max_rows):
        st.markdown(f"**Worker {i + 1}**")
        col1, col2, col3, col4 = st.columns(4)
        row = st.session_state.permanent_data[i]

        with col1:
            position = st.selectbox(
                "Position Title",
                list(POSITION_OPTIONS.keys()),
                index=list(POSITION_OPTIONS.values()).index(row.get("position_title", list(POSITION_OPTIONS.values())[0])),
                key=f"position_{i}"
            )
            sex = st.selectbox(
                "Sex",
                list(SEX_OPTIONS_PERM.keys()),
                index=list(SEX_OPTIONS_PERM.values()).index(row.get("sex", list(SEX_OPTIONS_PERM.values())[0])),
                key=f"sex_{i}"
            )
            age = st.selectbox(
                "Age",
                list(AGE_OPTIONS.keys()),
                index=list(AGE_OPTIONS.values()).index(row.get("age_group", list(AGE_OPTIONS.values())[0])),
                key=f"age_{i}"
            )

        with col2:
            nationality = st.selectbox(
                "Nationality",
                list(NATIONALITY_OPTIONS_PERM.keys()),
                index=list(NATIONALITY_OPTIONS_PERM.values()).index(row.get("nationality", list(NATIONALITY_OPTIONS_PERM.values())[0])),
                key=f"nationality_{i}"
            )
            education = st.selectbox(
                "Education Level",
                list(EDUCATION_OPTIONS_PERM.keys()),
                index=list(EDUCATION_OPTIONS_PERM.values()).index(row.get("education_level", list(EDUCATION_OPTIONS_PERM.values())[0])),
                key=f"education_{i}"
            )

        with col3:
            agri_training = st.selectbox(
                "Agricultural Training/Education",
                list(AG_TRAINING_OPTIONS_PERM.keys()),
                index=list(AG_TRAINING_OPTIONS_PERM.values()).index(row.get("agri_training", list(AG_TRAINING_OPTIONS_PERM.values())[0])),
                key=f"agri_{i}"
            )
            main_duties = st.selectbox(
                "Main Duties",
                list(MAIN_DUTIES_OPTIONS.keys()),
                index=list(MAIN_DUTIES_OPTIONS.values()).index(row.get("main_duties", list(MAIN_DUTIES_OPTIONS.values())[0])),
                key=f"duties_{i}"
            )

        with col4:
            working_time = st.selectbox(
                "Working Time on Holding",
                list(WORKING_TIME_OPTIONS_PERM.keys()),
                index=list(WORKING_TIME_OPTIONS_PERM.values()).index(row.get("working_time", list(WORKING_TIME_OPTIONS_PERM.values())[0])),
                key=f"worktime_{i}"
            )

        # Update session state
        st.session_state.permanent_data[i] = {
            "position_title": POSITION_OPTIONS[position],
            "sex": SEX_OPTIONS_PERM[sex],
            "age_group": AGE_OPTIONS[age],
            "nationality": NATIONALITY_OPTIONS_PERM[nationality],
            "education_level": EDUCATION_OPTIONS_PERM[education],
            "agri_training": AG_TRAINING_OPTIONS_PERM[agri_training],
            "main_duties": MAIN_DUTIES_OPTIONS[main_duties],
            "working_time": WORKING_TIME_OPTIONS_PERM[working_time]
        }

    # Save button
    if st.button("💾 Save Permanent Workers"):
        try:
            with engine.begin() as conn:
                # Delete old rows
                conn.execute(
                    text("DELETE FROM holding_labour_permanent WHERE holder_id=:hid"),
                    {"hid": holder_id}
                )
                # Insert new data
                for row in st.session_state.permanent_data:
                    # Skip empty rows
                    if not row.get("position_title"):
                        continue
                    conn.execute(
                        text("""
                            INSERT INTO holding_labour_permanent
                            (holder_id, position_title, sex, age_group, nationality, education_level,
                             agri_training, main_duties, working_time)
                            VALUES (:holder_id, :position_title, :sex, :age_group, :nationality, :education_level,
                                    :agri_training, :main_duties, :working_time)
                        """),
                        {**row, "holder_id": holder_id}
                    )
            mark_section_complete(holder_id)
            st.success("✅ Section 3 completed and saved!")
        except Exception as e:
            st.error(f"Error saving permanent workers data: {e}")

# ------------------- Run Section -------------------
def run_holding_labour_permanent(holder_id: int):
    if not holder_id:
        st.info("Please select a holder to continue.")
        return
    holding_labour_permanent_form(holder_id)
