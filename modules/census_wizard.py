import streamlit as st
from sqlalchemy import text
from census_app.db import engine
import pandas as pd
import datetime

# ---------------- Session Defaults ----------------
st.session_state.setdefault("current_section", 1)
st.session_state.setdefault("holder_form_data", {})      # Section 1: Holder info
st.session_state.setdefault("labour_form_data", {})      # Section 2: Holding labour
st.session_state.setdefault("household_form_data", {})   # Section 3: Household members

TOTAL_SECTIONS = 3
holder_id = st.session_state.get("holder_id", 1)  # Replace with actual holder ID

# ---------------- Navigation Buttons ----------------
col1, col2, col3 = st.columns([1,2,1])
with col1:
    if st.button("⬅ Back") and st.session_state["current_section"] > 1:
        st.session_state["current_section"] -= 1
with col3:
    if st.button("Next ➡") and st.session_state["current_section"] < TOTAL_SECTIONS:
        st.session_state["current_section"] += 1

st.markdown(f"### Section {st.session_state['current_section']} of {TOTAL_SECTIONS}")

# ===================== Section 1: Holder Information =====================
def holder_information_form(holder_id, prefix="holder"):
    SEX_OPTIONS = ["Male", "Female", "Other"]
    MARITAL_STATUS_OPTIONS = ["Single", "Married", "Divorced", "Separated", "Widowed", "Common-law", "Prefer not to disclose"]
    EDUCATION_OPTIONS = ["No Schooling", "Primary", "Junior Secondary", "Senior Secondary", "Undergraduate", "Masters", "Doctorate", "Vocational", "Professional Designation"]
    YES_NO = ["Yes", "No"]
    OCCUPATION_OPTIONS = ["Agriculture", "Other"]

    st.header("Section 1: Holder Information")
    if not holder_id:
        st.warning("No holder ID found.")
        return

    # Number of holders
    num_holders = st.number_input("Number of holders to add", min_value=1, max_value=3, step=1, key=f"{prefix}_num")

    holders_data = []

    for i in range(1, num_holders + 1):
        saved = st.session_state["holder_form_data"].get(i, {})
        st.subheader(f"Holder {i}{' - Main' if i==1 else ''}")

        full_name = st.text_input(f"Full Name (Holder {i})", value=saved.get("full_name",""), key=f"{prefix}_name_{i}")
        sex = st.selectbox(f"Sex (Holder {i})", SEX_OPTIONS, index=SEX_OPTIONS.index(saved.get("sex","Male")) if saved else 0, key=f"{prefix}_sex_{i}")
        dob = st.date_input(f"Date of Birth (Holder {i})", value=saved.get("date_of_birth", datetime.date.today()), min_value=datetime.date(1900,1,1), max_value=datetime.date.today(), key=f"{prefix}_dob_{i}")
        nationality = st.selectbox(f"Nationality (Holder {i})", ["Bahamian","Other"], index=0 if saved.get("nationality","Bahamian")=="Bahamian" else 1, key=f"{prefix}_nat_{i}")
        nationality_other = st.text_input(f"Specify Nationality (Holder {i})", value=saved.get("nationality_other",""), key=f"{prefix}_nat_other_{i}") if nationality=="Other" else ""
        marital_status = st.selectbox(f"Marital Status (Holder {i})", MARITAL_STATUS_OPTIONS, key=f"{prefix}_mar_{i}")
        education = st.selectbox(f"Highest Level of Education (Holder {i})", EDUCATION_OPTIONS, key=f"{prefix}_edu_{i}")
        ag_training = st.radio(f"Agricultural Education/Training (Holder {i})", YES_NO, index=YES_NO.index(saved.get("agri_training","No")), key=f"{prefix}_train_{i}")
        primary_occupation = st.selectbox(f"Primary Occupation (Holder {i})", OCCUPATION_OPTIONS, key=f"{prefix}_primocc_{i}")
        primary_occupation_other = st.text_input(f"Specify Primary Occupation (Holder {i})", value=saved.get("primary_occupation_other",""), key=f"{prefix}_primocc_other_{i}") if primary_occupation=="Other" else ""
        secondary_occupation = st.text_input(f"Secondary Occupation (Holder {i})", value=saved.get("secondary_occupation",""), key=f"{prefix}_secocc_{i}")

        holders_data.append({
            "holder_number": i,
            "full_name": full_name,
            "sex": sex,
            "date_of_birth": dob,
            "nationality": nationality,
            "nationality_other": nationality_other,
            "marital_status": marital_status,
            "highest_education": education,
            "agri_training": ag_training,
            "primary_occupation": primary_occupation,
            "primary_occupation_other": primary_occupation_other,
            "secondary_occupation": secondary_occupation
        })

    # Save to session
    for idx, h in enumerate(holders_data, start=1):
        st.session_state["holder_form_data"][idx] = h

    # Preview
    st.subheader("Preview Entered Holder Information")
    st.dataframe(pd.DataFrame([h for h in holders_data if h["full_name"]]))

    # Save to DB
    if st.button("💾 Save Holder Information"):
        with engine.begin() as conn:
            for holder in holders_data:
                if holder["full_name"]:
                    conn.execute(
                        text("""
                            INSERT INTO holders (
                                owner_id, name, sex, date_of_birth,
                                nationality, nationality_other, marital_status,
                                highest_education, agri_training,
                                primary_occupation, primary_occupation_other,
                                secondary_occupation
                            )
                            VALUES (
                                :holder_id, :full_name, :sex, :date_of_birth,
                                :nationality, :nationality_other, :marital_status,
                                :highest_education, :agri_training,
                                :primary_occupation, :primary_occupation_other,
                                :secondary_occupation
                            )
                            ON CONFLICT (owner_id, holder_number)
                            DO UPDATE SET
                                name = EXCLUDED.name,
                                sex = EXCLUDED.sex,
                                date_of_birth = EXCLUDED.date_of_birth,
                                nationality = EXCLUDED.nationality,
                                nationality_other = EXCLUDED.nationality_other,
                                marital_status = EXCLUDED.marital_status,
                                highest_education = EXCLUDED.highest_education,
                                agri_training = EXCLUDED.agri_training,
                                primary_occupation = EXCLUDED.primary_occupation,
                                primary_occupation_other = EXCLUDED.primary_occupation_other,
                                secondary_occupation = EXCLUDED.secondary_occupation
                        """), {**holder, "holder_id": holder_id}
                    )
        st.success("✅ Holder Information saved/updated successfully!")

# ===================== Section 2: Holding Labour =====================
def holding_labour_form(holder_id, prefix="holder"):
    st.header("Section 2: Holding Labour")
    st.session_state.setdefault(f"{prefix}_responses", {})

    questions = [
        {"question_no": 2, "text": "Permanent workers (excluding household) from Aug 1, 2024 to Jul 31, 2025", "type": "count"},
        {"question_no": 3, "text": "Temporary workers (excluding household) from Aug 1, 2024 to Jul 31, 2025", "type": "count"},
        {"question_no": 4, "text": "Number of non-Bahamian workers from Aug 1, 2024 to Jul 31, 2025", "type": "count"},
        {"question_no": 5, "text": "Did any of your workers have work permits?", "type": "option", "options": ["Yes", "No", "Not Applicable"]},
        {"question_no": 6, "text": "Any volunteer (unpaid) workers?", "type": "option", "options": ["Yes", "No", "Not Applicable"]},
        {"question_no": 7, "text": "Use of agricultural contracted services?", "type": "option", "options": ["Yes", "No", "Not Applicable"]},
    ]

    responses = st.session_state[f"{prefix}_responses"]

    for q in questions:
        q_no = q["question_no"]
        key_base = f"{prefix}_{holder_id}_q{q_no}"
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

# ===================== Section 3: Household Information =====================
def household_information(holder_id, prefix="household"):
    RELATIONSHIP_OPTIONS = {
        1: "Spouse/Partner", 2: "Son", 3: "Daughter", 4: "In-Laws",
        5: "Grandchild", 6: "Parent/Parent-In-Law", 7: "Other Relative", 8: "Non-Relative"
    }
    SEX_OPTIONS = ["Male", "Female"]
    EDUCATION_OPTIONS = {
        1: "No Schooling", 2: "Primary", 3: "Junior Secondary", 4: "Senior Secondary",
        5: "Undergraduate", 6: "Masters", 7: "Doctorate", 8: "Vocational", 9: "Professional Designation"
    }
    OCCUPATION_OPTIONS = {
        1: "Agriculture", 2: "Fishing", 3: "Professional/Technical", 4: "Administrative/Manager",
        5: "Sales", 6: "Customer Service", 7: "Tourism", 8: "Not Economically Active", 9: "Other"
    }
    WORKING_TIME_OPTIONS = {"N": "None", "F": "Full time", "P": "Part time", "P3": "1-3 months", "P6": "4-6 months", "P7": "7+ months"}

    st.header("Section 3 - Household Information")

    # Household summary
    total_persons = st.number_input("Total persons in household (including holder)", min_value=0, max_value=100, step=1, key=f"{prefix}_total_persons")
    col1, col2 = st.columns(2)
    with col1:
        u14_male = st.number_input("Under 14 (Male)", 0, 100, 0, key=f"{prefix}_u14_male")
        plus14_male = st.number_input("14+ (Male)", 0, 100, 0, key=f"{prefix}_14plus_male")
    with col2:
        u14_female = st.number_input("Under 14 (Female)", 0, 100, 0, key=f"{prefix}_u14_female")
        plus14_female = st.number_input("14+ (Female)", 0, 100, 0, key=f"{prefix}_14plus_female")

    if (u14_male + u14_female + plus14_male + plus14_female) > total_persons:
        st.warning("⚠️ Sum of age groups exceeds total persons")

    if st.button("💾 Save Household Summary", key=f"{prefix}_save_summary"):
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO household_summary (
                    holdings_id, holder_number, total_persons,
                    persons_under_14_male, persons_under_14_female,
                    persons_14plus_male, persons_14plus_female
                ) VALUES (
                    :holdings_id, :holder_number, :total_persons,
                    :u14_male, :u14_female, :plus14_male, :plus14_female
                )
                ON CONFLICT (holdings_id, holder_number)
                DO UPDATE SET
                    total_persons = EXCLUDED.total_persons,
                    persons_under_14_male = EXCLUDED.persons_under_14_male,
                    persons_under_14_female = EXCLUDED.persons_under_14_female,
                    persons_14plus_male = EXCLUDED.persons_14plus_male,
                    persons_14plus_female = EXCLUDED.persons_14plus_female;
            """), {
                "holdings_id": holder_id,
                "holder_number": holder_id,
                "total_persons": total_persons,
                "u14_male": u14_male,
                "u14_female": u14_female,
                "plus14_male": plus14_male,
                "plus14_female": plus14_female
            })
        st.success("✅ Household summary saved!")

# ===================== Section Router =====================
current = st.session_state["current_section"]

if current == 1:
    holder_information_form(holder_id)
elif current == 2:
    holding_labour_form
