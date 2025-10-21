# census_app/modules/household_information.py

import streamlit as st
import pandas as pd
from sqlalchemy import text
from census_app.db import engine

# ------------------- Constants -------------------
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
WORKING_TIME_OPTIONS = {
    "N": "None", "F": "Full time", "P": "Part time",
    "P3": "1-3 months", "P6": "4-6 months", "P7": "7+ months"
}

# ------------------- Main Function -------------------
def household_information(holder_id: int, prefix="household"):
    st.header("🏠 Section 3 - Household Information")

    # --- Initialize session data safely ---
    if "household_form_data" not in st.session_state:
        st.session_state["household_form_data"] = {}

    # ---------------- Household Summary ----------------
    st.subheader("Household Summary")
    total_persons = st.number_input(
        "Total persons in household (including holder)",
        min_value=0, max_value=100, step=1, key=f"{prefix}_total_persons"
    )
    col1, col2 = st.columns(2)
    with col1:
        u14_male = st.number_input("Under 14 (Male)", 0, 100, 0, key=f"{prefix}_u14_male")
        plus14_male = st.number_input("14+ (Male)", 0, 100, 0, key=f"{prefix}_14plus_male")
    with col2:
        u14_female = st.number_input("Under 14 (Female)", 0, 100, 0, key=f"{prefix}_u14_female")
        plus14_female = st.number_input("14+ (Female)", 0, 100, 0, key=f"{prefix}_14plus_female")

    total_by_age = u14_male + u14_female + plus14_male + plus14_female
    if total_by_age > total_persons:
        st.warning("⚠️ Sum of age groups exceeds total persons entered.")

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

    # ---------------- Existing Members ----------------
    st.subheader("👨‍👩‍👧‍👦 Existing Household Members")
    with engine.begin() as conn:
        members = conn.execute(text("""
            SELECT id, relationship_to_holder, sex, age, education_level,
                   primary_occupation, secondary_occupation, working_time_on_holding
            FROM household_information
            WHERE holder_id = :holder_id
            ORDER BY id
        """), {"holder_id": holder_id}).fetchall()

    if members:
        df_members = pd.DataFrame([{
            "Relationship": RELATIONSHIP_OPTIONS.get(m.relationship_to_holder, "Unknown"),
            "Sex": m.sex,
            "Age": m.age,
            "Education": EDUCATION_OPTIONS.get(m.education_level, "Unknown"),
            "Primary Occupation": OCCUPATION_OPTIONS.get(m.primary_occupation, "Unknown"),
            "Secondary Occupation": OCCUPATION_OPTIONS.get(m.secondary_occupation, "None"),
            "Work Time": WORKING_TIME_OPTIONS.get(m.working_time_on_holding, "Unknown")
        } for m in members])
        st.dataframe(df_members, use_container_width=True)
    else:
        st.info("No existing household members found.")

    # ---------------- Add New Members ----------------
    st.subheader("➕ Add Household Members")
    current_count = len(members) if members else 0
    max_new_members = min(10, max(0, total_persons - current_count))

    if total_persons == 0:
        st.info("Enter total persons in household first.")
        return
    if max_new_members <= 0:
        st.info("All household members already added based on total persons.")
        return

    for i in range(1, max_new_members + 1):
        st.markdown(f"### New Member {i}")
        with st.form(f"{prefix}_new_member_form_{i}", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                relationship = st.selectbox(
                    "Relationship to Holder", options=list(RELATIONSHIP_OPTIONS.keys()),
                    format_func=lambda x: RELATIONSHIP_OPTIONS[x]
                )
                sex = st.radio("Sex", SEX_OPTIONS, horizontal=True)
                age = st.number_input("Age", min_value=0, max_value=120, step=1)
                edu = st.selectbox(
                    "Education Level", options=list(EDUCATION_OPTIONS.keys()),
                    format_func=lambda x: EDUCATION_OPTIONS[x]
                )
            with col2:
                primary_occ = st.selectbox(
                    "Primary Occupation", options=list(OCCUPATION_OPTIONS.keys()),
                    format_func=lambda x: OCCUPATION_OPTIONS[x]
                )
                secondary_occ = st.selectbox(
                    "Secondary Occupation (optional)",
                    options=[None] + list(OCCUPATION_OPTIONS.keys()),
                    format_func=lambda x: OCCUPATION_OPTIONS[x] if x else "None"
                )
                work_time = st.selectbox(
                    "Working Time on Holding", options=list(WORKING_TIME_OPTIONS.keys()),
                    format_func=lambda x: WORKING_TIME_OPTIONS[x]
                )

            submitted = st.form_submit_button("Add Member")
            if submitted:
                with engine.begin() as conn:
                    conn.execute(text("""
                        INSERT INTO household_information
                        (holder_id, relationship_to_holder, sex, age, education_level,
                         primary_occupation, secondary_occupation, working_time_on_holding)
                        VALUES (:holder_id, :relationship, :sex, :age, :edu, :primary_occ, :secondary_occ, :work_time)
                    """), {
                        "holder_id": holder_id,
                        "relationship": relationship,
                        "sex": sex,
                        "age": age,
                        "edu": edu,
                        "primary_occ": primary_occ,
                        "secondary_occ": secondary_occ,
                        "work_time": work_time
                    })
                st.success(f"✅ Member {i} added successfully!")
                st.rerun()
