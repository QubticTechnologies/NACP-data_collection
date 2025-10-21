import streamlit as st
from sqlalchemy import text
from census_app.db import engine

# ---------------- Holder Labour Form ----------------
def holding_labour_form(holder_id, prefix="holder"):
    """
    Render Section 2: Holding Labour form for a given holder.
    Handles permanent/temporary workers, non-Bahamian workers, work permits,
    volunteers, and contracted services.
    """
    st.header("Section 2: Holding Labour")

    # Initialize session for form persistence
    st.session_state.setdefault(f"{prefix}_responses", {})

    # Define questions
    questions = [
        {"question_no": 2, "text": "Permanent workers (excluding household) from Aug 1, 2024 to Jul 31, 2025", "type": "count"},
        {"question_no": 3, "text": "Temporary workers (excluding household) from Aug 1, 2024 to Jul 31, 2025", "type": "count"},
        {"question_no": 4, "text": "Number of non-Bahamian workers from Aug 1, 2024 to Jul 31, 2025", "type": "count"},
        {"question_no": 5, "text": "Did any of your workers have work permits?", "type": "option", "options": ["Yes", "No", "Not Applicable"]},
        {"question_no": 6, "text": "Any volunteer (unpaid) workers?", "type": "option", "options": ["Yes", "No", "Not Applicable"]},
        {"question_no": 7, "text": "Use of agricultural contracted services?", "type": "option", "options": ["Yes", "No", "Not Applicable"]},
    ]

    responses = st.session_state[f"{prefix}_responses"]

    # Render questions
    for q in questions:
        q_no = q["question_no"]
        key_base = f"{prefix}_{holder_id}_q{q_no}"

        # Load previous session values if available
        saved = responses.get(q_no, {})

        if q["type"] == "count":
            male = st.number_input(f"Male - {q['text']}", min_value=0, value=saved.get("male", 0), key=f"{key_base}_male")
            female = st.number_input(f"Female - {q['text']}", min_value=0, value=saved.get("female", 0), key=f"{key_base}_female")
            total = male + female
            st.write(f"Total: {total}")
            responses[q_no] = {"male": male, "female": female, "total": total, "option_response": None}

        elif q["type"] == "option":
            option_response = st.selectbox(q["text"], options=q["options"], index=q["options"].index(saved.get("option_response", q["options"][0])), key=f"{key_base}_option")
            responses[q_no] = {"male": None, "female": None, "total": None, "option_response": option_response}

    # ---------------- Save to Database ----------------
    if st.button("💾 Save Section 2 Responses", key=f"{prefix}_save_btn"):
        try:
            with engine.begin() as conn:
                for q in questions:
                    r = responses[q["question_no"]]
                    conn.execute(
                        text("""
                            INSERT INTO holding_labour (
                                holder_id, question_no, question_text,
                                male_count, female_count, total_count, option_response
                            ) VALUES (
                                :holder_id, :q_no, :question_text, :male, :female, :total, :option_response
                            )
                            ON CONFLICT (holder_id, question_no) DO UPDATE
                            SET male_count = EXCLUDED.male_count,
                                female_count = EXCLUDED.female_count,
                                total_count = EXCLUDED.total_count,
                                option_response = EXCLUDED.option_response
                        """),
                        {
                            "holder_id": holder_id,
                            "q_no": q["question_no"],
                            "question_text": q["text"],
                            "male": r["male"],
                            "female": r["female"],
                            "total": r["total"],
                            "option_response": r["option_response"]
                        }
                    )
            st.success("✅ Section 2 responses saved successfully!")
        except Exception as e:
            st.error(f"Error saving responses: {e}")
