from sqlalchemy import text
from census_app.db import engine
from census_app.config import HOLDERS_TABLE, TOTAL_SURVEY_SECTIONS
from census_app.modules.holder_information_form import holder_information_form
import streamlit as st


# --------------------- Survey Progress ---------------------
def mark_section_complete(holder_id: int, section_no: int):
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO holder_survey_progress (holder_id, section_id, completed)
                VALUES (:hid, :sec, TRUE)
                ON CONFLICT(holder_id, section_id)
                DO UPDATE SET completed=TRUE
            """),
            {"hid": holder_id, "sec": section_no}
        )


def get_completed_sections(holder_id: int) -> set[int]:
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT section_id FROM holder_survey_progress WHERE holder_id=:hid AND completed=TRUE"),
            {"hid": holder_id}
        ).fetchall()
    return {r[0] for r in rows}


# --------------------- Holder Info ---------------------
def get_holder_name(holder_id: int) -> str:
    with engine.connect() as conn:
        row = conn.execute(
            text(f"SELECT name FROM {HOLDERS_TABLE} WHERE holder_id = :hid"),
            {"hid": holder_id}
        ).fetchone()
    return row[0] if row else "Unknown Holder"


def get_holder_info(holder_id: int) -> dict:
    with engine.connect() as conn:
        row = conn.execute(
            text(f"SELECT * FROM {HOLDERS_TABLE} WHERE holder_id = :hid"),
            {"hid": holder_id}
        ).mappings().first()
    return dict(row) if row else {}


# --------------------- Streamlit Dashboard ---------------------
def show_holder_dashboard(holder_id: int):
    """
    Unified holder dashboard:
    - Survey progress
    - Section 2: Holder Information
    - Automatically shows next section after Section 2
    """
    # Import from helpers to avoid circular import
    from census_app.modules.survey_helpers import show_regular_survey_section

    completed = get_completed_sections(holder_id)

    st.sidebar.markdown(f"### {get_holder_name(holder_id)}")

    # Progress bar
    st.write("### Survey Progress")
    st.progress(len(completed) / TOTAL_SURVEY_SECTIONS if TOTAL_SURVEY_SECTIONS else 0)
    if completed:
        st.write(f"✅ Completed Sections: {sorted(completed)}")
    else:
        st.info("No sections completed yet. Section 2: Holder Information is first.")

    # ---------------- Render Section 2 ----------------
    st.write("---")
    holder_information_form(holder_id)

    # Automatically mark Section 2 complete if data exists
    holder_info = get_holder_info(holder_id)
    if holder_info.get("full_name"):
        mark_section_complete(holder_id, section_no=2)

    # Show next section if Section 2 complete
    if 2 in completed or holder_info.get("full_name"):
        next_section = 3
        if next_section <= TOTAL_SURVEY_SECTIONS:
            show_regular_survey_section(section_number=next_section, holder_id=holder_id)
