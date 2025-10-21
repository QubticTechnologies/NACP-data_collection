import streamlit as st
from sqlalchemy import text
from census_app.db import engine

SECTION_NO = 2  # Section ID for Holding Labour Survey

# --------------------- Helper Functions ---------------------
def get_holder_name_local(holder_id: int):
    """Fetch holder name directly from the DB to avoid circular imports."""
    with engine.connect() as conn:
        name = conn.execute(
            text("SELECT name FROM holders WHERE id=:hid"),
            {"hid": holder_id}
        ).scalar()
    return name or f"Holder {holder_id}"


def initialize_labour_questions(holder_id: int):
    """Create default labour survey questions for a new holder."""
    default_questions = [
        (2, "How many permanent workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?"),
        (3, "How many temporary workers including administrative staff were hired on the holding from Aug 1, 2024 to Jul 31, 2025 (excluding household)?"),
        (4, "What was the number of non-Bahamian workers on the holding from Aug 1, 2024 to Jul 31, 2025?"),
        (5, "Did any of your workers have work permits?", "Not Applicable"),
        (6, "Were there any volunteer workers on the holding (i.e. unpaid labourers)?", "Not Applicable"),
        (7, "Did you use any agricultural contracted services (crop protection, pruning, composting, harvesting, animal services, irrigation, farm admin etc.) on the holding?", "Not Applicable")
    ]

    with engine.begin() as conn:
        for q_no, q_text, *opt_response in default_questions:
            default_opt = opt_response[0] if opt_response else "Not Applicable"
            conn.execute(
                text("""
                    INSERT INTO holding_labour
                    (holder_id, question_no, question_text, male_count, female_count, total_count, option_response)
                    VALUES (:hid, :q_no, :q_text, 0, 0, 0, :opt)
                """),
                {"hid": holder_id, "q_no": q_no, "q_text": q_text, "opt": default_opt}
            )


def select_holder(agent_id: int):
    """Fetch holders assigned to this agent and let the agent select one."""
    with engine.begin() as conn:
        holders = conn.execute(
            text("SELECT id, name FROM holders WHERE assigned_agent_id=:agent_id ORDER BY name"),
            {"agent_id": agent_id}
        ).fetchall()

    if not holders:
        st.warning("⚠️ No holders assigned to you.")
        return None

    if len(holders) == 1:
        h = holders[0]
        st.info(f"Auto-selected holder: {h.name} (ID: {h.id})")
        return h.id

    holder_options = {f"{h.name} (ID: {h.id})": h.id for h in holders}
    selected_label = st.selectbox("Select Holder", list(holder_options.keys()))
    return holder_options[selected_label]


def fetch_questions(holder_id: int):
    """Get all labour questions for a holder."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT id, question_no, question_text, male_count, female_count, total_count, option_response
                FROM holding_labour
                WHERE holder_id=:hid
                ORDER BY question_no
            """),
            {"hid": holder_id}
        ).mappings().all()
    return rows


def mark_section_complete(holder_id: int):
    """Mark Section 2 as completed."""
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
                text("INSERT INTO holder_survey_progress (holder_id, section_id, completed) VALUES(:hid, :sec, true)"),
                {"hid": holder_id, "sec": SECTION_NO}
            )


# --------------------- Labour Form ---------------------
def labour_form_page(holder_id=None, holder_name=None):
    """Render and manage the Holding Labour survey."""
    agent_id = st.session_state.get("user_id", 1)

    if holder_id is None:
        holder_id = select_holder(agent_id)
        if not holder_id:
            st.info("Please assign a holder to continue.")
            return

    if holder_name is None:
        holder_name = get_holder_name_local(holder_id)

    st.subheader(f"Holding Labour Survey{' for ' + holder_name if holder_name else ''}")

    questions = fetch_questions(holder_id)
    if not questions:
        st.info("Initializing default labour questions...")
        initialize_labour_questions(holder_id)
        questions = fetch_questions(holder_id)

    # Initialize session state
    if "labour_current_form" not in st.session_state or st.session_state.get("labour_holder_id") != holder_id:
        st.session_state["labour_current_form"] = 2
        st.session_state["labour_holder_id"] = holder_id
        st.session_state["labour_complete"] = False

    current_q = next((q for q in questions if q["question_no"] == st.session_state["labour_current_form"]), None)

    if not current_q:
        st.success("✅ Section 2 completed!")
        mark_section_complete(holder_id)
        st.session_state["labour_complete"] = True
        return

    st.write(f"**Q{current_q['question_no']}: {current_q['question_text']}**")

    male = female = total = None
    option_response = None

    if current_q["question_no"] in [2, 3, 4]:
        male = st.number_input(
            "Male count",
            min_value=0,
            value=current_q.get("male_count") or 0,
            key=f"male_{current_q['question_no']}"
        )
        female = st.number_input(
            "Female count",
            min_value=0,
            value=current_q.get("female_count") or 0,
            key=f"female_{current_q['question_no']}"
        )
        total = male + female
        st.write(f"**Total Count:** {total}")
    else:
        option_response = st.selectbox(
            "Select response",
            ["Yes", "No", "Not Applicable"],
            index=["Yes", "No", "Not Applicable"].index(current_q.get("option_response") or "Not Applicable"),
            key=f"option_{current_q['question_no']}"
        )

    if st.button("💾 Save & Next"):
        with engine.begin() as conn:
            exists = conn.execute(
                text("SELECT id FROM holding_labour WHERE holder_id=:hid AND question_no=:qno"),
                {"hid": holder_id, "qno": current_q["question_no"]}
            ).fetchone()

            data = {
                "male_count": male,
                "female_count": female,
                "total_count": total,
                "option_response": option_response
            }

            if exists:
                conn.execute(
                    text("""
                        UPDATE holding_labour
                        SET male_count=:male_count,
                            female_count=:female_count,
                            total_count=:total_count,
                            option_response=:option_response
                        WHERE holder_id=:holder_id AND question_no=:question_no
                    """),
                    {**data, "holder_id": holder_id, "question_no": current_q["question_no"]}
                )
            else:
                conn.execute(
                    text("""
                        INSERT INTO holding_labour
                        (holder_id, question_no, question_text, male_count, female_count, total_count, option_response)
                        VALUES (:holder_id, :question_no, :question_text, :male_count, :female_count, :total_count, :option_response)
                    """),
                    {**data, "holder_id": holder_id, "question_no": current_q["question_no"], "question_text": current_q["question_text"]}
                )

        # Move to next question
        next_q = next((q for q in questions if q["question_no"] == st.session_state["labour_current_form"] + 1), None)
        if next_q:
            st.session_state["labour_current_form"] += 1
        else:
            st.session_state["labour_complete"] = True
            mark_section_complete(holder_id)

        st.experimental_rerun()


# --------------------- Backward Compatibility ---------------------
holding_labour_form = labour_form_page


# --------------------- Run Section 2 ---------------------
def run_holding_labour_survey(holder_id=None):
    """Run the full Holding Labour survey; accepts optional holder_id."""
    st.title("NACP - Holding Labour Survey (Section 2)")

    if holder_id is None:
        agent_id = st.session_state.get("user_id", 1)
        holder_id = select_holder(agent_id)
        if holder_id is None:
            st.info("Please assign a holder to continue.")
            return

    labour_form_page(holder_id=holder_id, holder_name=get_holder_name_local(holder_id))
