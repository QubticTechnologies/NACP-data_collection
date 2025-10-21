# census_app/modules/holder_information_form.py

import streamlit as st
import pandas as pd
from sqlalchemy import text
from census_app.db import engine
import datetime

# ------------------- Initialize Session State -------------------
if "holder_form_data" not in st.session_state:
    st.session_state["holder_form_data"] = {}

# ---------------- Options ----------------
SEX_OPTIONS = ["Male", "Female", "Other"]
MARITAL_STATUS_OPTIONS = [
    "Single", "Married", "Divorced", "Separated",
    "Widowed", "Common-law", "Prefer not to disclose"
]
EDUCATION_OPTIONS = [
    "No Schooling", "Primary", "Junior Secondary",
    "Senior Secondary", "Undergraduate", "Masters",
    "Doctorate", "Vocational", "Professional Designation"
]
YES_NO = ["Yes", "No"]
OCCUPATION_OPTIONS = ["Agriculture", "Other"]

# ---------------- Form ----------------
def holder_information_form(holder_id, prefix="holder"):
    st.header("Section 1: Holder Information")
    if not holder_id:
        st.warning("No holder ID found.")
        return

    # Number of holders
    num_holders = st.number_input(
        "Number of holders to add", min_value=1, max_value=3, step=1,
        key=f"{prefix}_num"
    )

    holders_data = []

    for i in range(1, num_holders + 1):
        saved = st.session_state["holder_form_data"].get(i, {})
        st.subheader(f"Holder {i}{' - Main' if i==1 else ''}")

        # Full Name
        full_name = st.text_input(
            f"Full Name (Holder {i})",
            value=saved.get("full_name", ""),
            key=f"{prefix}_name_{i}"
        )

        sex = st.selectbox(
            f"Sex (Holder {i})",
            SEX_OPTIONS,
            index=SEX_OPTIONS.index(saved.get("sex", "Male")) if saved else 0,
            key=f"{prefix}_sex_{i}"
        )

        # DOB - ensure proper type
        dob_value = saved.get("date_of_birth", datetime.date.today())
        if isinstance(dob_value, str):
            try:
                dob_value = datetime.date.fromisoformat(dob_value)
            except:
                dob_value = datetime.date.today()

        dob = st.date_input(
            f"Date of Birth (Holder {i})",
            value=dob_value,
            min_value=datetime.date(1900,1,1),
            max_value=datetime.date.today(),
            key=f"{prefix}_dob_{i}"
        )

        nationality = st.selectbox(
            f"Nationality (Holder {i})",
            ["Bahamian","Other"],
            index=0 if saved.get("nationality","Bahamian")=="Bahamian" else 1,
            key=f"{prefix}_nat_{i}"
        )

        nationality_other = st.text_input(
            f"Specify Nationality (Holder {i})",
            value=saved.get("nationality_other",""),
            key=f"{prefix}_nat_other_{i}"
        ) if nationality=="Other" else ""

        marital_status = st.selectbox(
            f"Marital Status (Holder {i})",
            MARITAL_STATUS_OPTIONS,
            index=MARITAL_STATUS_OPTIONS.index(saved.get("marital_status","Single")) if saved else 0,
            key=f"{prefix}_mar_{i}"
        )

        education = st.selectbox(
            f"Highest Level of Education (Holder {i})",
            EDUCATION_OPTIONS,
            index=EDUCATION_OPTIONS.index(saved.get("highest_education","No Schooling")) if saved else 0,
            key=f"{prefix}_edu_{i}"
        )

        ag_training = st.radio(
            f"Agricultural Education/Training (Holder {i})",
            YES_NO,
            index=YES_NO.index(saved.get("agri_training","No")) if saved else 1,
            key=f"{prefix}_train_{i}"
        )

        primary_occupation = st.selectbox(
            f"Primary Occupation (Holder {i})",
            OCCUPATION_OPTIONS,
            index=OCCUPATION_OPTIONS.index(saved.get("primary_occupation","Agriculture")) if saved else 0,
            key=f"{prefix}_primocc_{i}"
        )

        primary_occupation_other = st.text_input(
            f"Specify Primary Occupation (Holder {i})",
            value=saved.get("primary_occupation_other",""),
            key=f"{prefix}_primocc_other_{i}"
        ) if primary_occupation=="Other" else ""

        secondary_occupation = st.text_input(
            f"Secondary Occupation (Holder {i})",
            value=saved.get("secondary_occupation",""),
            key=f"{prefix}_secocc_{i}"
        )

        holders_data.append({
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
                    dob_iso = holder["date_of_birth"].isoformat() if holder["date_of_birth"] else None
                    conn.execute(text("""
                        INSERT INTO holders (
                            owner_id, name, sex, date_of_birth,
                            nationality, nationality_other, marital_status,
                            highest_education, agri_training,
                            primary_occupation, primary_occupation_other,
                            secondary_occupation
                        ) VALUES (
                            :owner_id, :full_name, :sex, :date_of_birth,
                            :nationality, :nationality_other, :marital_status,
                            :highest_education, :agri_training,
                            :primary_occupation, :primary_occupation_other,
                            :secondary_occupation
                        )
                        ON CONFLICT (owner_id) DO UPDATE SET
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
                            secondary_occupation = EXCLUDED.secondary_occupation;
                    """), {**holder, "owner_id": holder_id, "date_of_birth": dob_iso})
        st.success("✅ Holder Information saved successfully!")
