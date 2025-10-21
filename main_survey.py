# census_app/main_survey.py

import streamlit as st
from sqlalchemy import text
from census_app.db import engine
from census_app.config import TOTAL_SURVEY_SECTIONS

# --- Modular survey sections ---
from census_app.modules.holder_info import run_holder_info_survey
from census_app.modules.holding_labour_form import run_holding_labour_survey
from census_app.modules.holding_labour_permanent import run_holding_labour_permanent_survey
from census_app.modules.survey_sections import show_regular_survey_section

# ---------------------- Progress Helpers ----------------------

def mark_section_complete(holder_id: int, section_no: int):
    """Mark a survey section as completed for a given holder."""
    with engine.begin() as conn:
        exists = conn.execute(
            text("""
                SELECT id FROM holder_survey_progress
                WHERE holder_id = :hid AND section_no = :sec
            """),
            {"hid": holder_id, "sec": section_no}
        ).fetchone()

        if exists:
            conn.execute(
                text("""
                    UPDATE holder_survey_progress
                    SET completed = TRUE
                    WHERE id = :id
                """),
                {"id": exists[0]}
            )
        else:
            conn.execute(
                text("""
                    INSERT INTO holder_survey_progress(holder_id, section_no, completed)
                    VALUES(:hid, :sec, TRUE)
                """),
                {"hid": holder_id, "sec": section_no}
            )

def get_completed_sections(holder_id: int):
    """Return list of completed section numbers for a holder."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT section_no
                FROM holder_survey_progress
                WHERE holder_id = :hid AND completed = TRUE
            """),
            {"hid": holder_id}
        ).fetchall()
    return [r[0] for r in rows]

# ---------------------- Survey Navigator ----------------------

def run_main_survey(holder_id: int):
    """
    Main survey runner for a single holder.
    Shows section navigation, tracks progress, and renders each section.
    """
    st.title("📋 Agricultural Census Survey")

    # Progress tracking
    completed_sections = get_completed_sections(holder_id)
    st.progress(len(completed_sections) / TOTAL_SURVEY_SECTIONS)

    # Sidebar navigation
    section_no = st.sidebar.selectbox(
        "📑 Select Section",
        list(range(1, TOTAL_SURVEY_SECTIONS + 1)),
        format_func=lambda x: f"Section {x} {'✅' if x in completed_sections else ''}"
    )

    st.markdown(f"### Section {section_no}")

    # --- Section routing ---
    if section_no == 1:
        run_holder_info_survey(holder_id)
        if st.button("✅ Mark Section 1 Complete"):
            mark_section_complete(holder_id, 1)
            st.success("Section 1 marked complete!")

    elif section_no == 2:
        run_holding_labour_survey(holder_id)
        if st.button("✅ Mark Section 2 Complete"):
            mark_section_complete(holder_id, 2)
            st.success("Section 2 marked complete!")

    elif section_no == 3:
        run_holding_labour_permanent_survey(holder_id)
        if st.button("✅ Mark Section 3 Complete"):
            mark_section_complete(holder_id, 3)
            st.success("Section 3 marked complete!")

    else:
        show_regular_survey_section(section_no, holder_id)
        if st.button(f"✅ Mark Section {section_no} Complete"):
            mark_section_complete(holder_id, section_no)
            st.success(f"Section {section_no} marked complete!")

    # Final completion
    if len(completed_sections) == TOTAL_SURVEY_SECTIONS:
        st.success("🎉 All sections completed for this holder!")

