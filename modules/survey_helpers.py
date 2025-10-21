# census_app/modules/survey_helpers.py

from census_app.db import engine
from sqlalchemy import text

# ---------------- Completed Sections ----------------
def get_completed_sections(holder_id: int):
    """Return a list of completed section IDs for a holder."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT section_id FROM holder_survey_progress WHERE holder_id=:hid AND completed=true"),
            {"hid": holder_id}
        ).fetchall()
    return [r[0] for r in rows]

# ---------------- Show Regular Section ----------------
def show_regular_survey_section(section_id: int, holder_id: int):
    """Placeholder to render regular survey sections."""
    from streamlit import write
    write(f"Rendering Section {section_id} for Holder {holder_id}")

# ---------------- Mark Section Complete ----------------
def mark_section_complete(section_id: int, holder_id: int):
    """Mark a section as completed for a holder."""
    with engine.begin() as conn:
        exists = conn.execute(
            text("SELECT id FROM holder_survey_progress WHERE holder_id=:hid AND section_id=:sec"),
            {"hid": holder_id, "sec": section_id}
        ).fetchone()
        if exists:
            conn.execute(
                text("UPDATE holder_survey_progress SET completed=true WHERE id=:id"),
                {"id": exists[0]}
            )
        else:
            conn.execute(
                text("INSERT INTO holder_survey_progress (holder_id, section_id, completed) VALUES(:hid, :sec, true)"),
                {"hid": holder_id, "sec": section_id}
            )
