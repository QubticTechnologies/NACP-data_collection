import streamlit as st
import pandas as pd
import json
import os
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# ---------------- Config ----------------
BASE_DIR = os.path.dirname(__file__)
TEMPLATE_FILE = os.path.join(BASE_DIR, "query_templates.json")


# ---------------- Load/Save Templates ----------------
def load_templates():
    """Load saved query templates from JSON file."""
    try:
        with open(TEMPLATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_templates(templates):
    """Save query templates to JSON file."""
    with open(TEMPLATE_FILE, "w") as f:
        json.dump(templates, f, indent=4)


# ---------------- Apply Query Conditions ----------------
def apply_conditions(df, conditions, connector="AND"):
    """Filter dataframe based on conditions and connector (AND/OR)."""
    if df is None or df.empty or not conditions:
        return df.copy()

    mask = pd.Series(True, index=df.index) if connector == "AND" else pd.Series(False, index=df.index)

    for col, op, val in conditions:
        if not val or col not in df.columns:
            continue
        try:
            if op == "=":
                cond = df[col].astype(str) == val
            elif op == "!=":
                cond = df[col].astype(str) != val
            elif op == "<":
                cond = pd.to_numeric(df[col], errors="coerce") < float(val)
            elif op == "<=":
                cond = pd.to_numeric(df[col], errors="coerce") <= float(val)
            elif op == ">":
                cond = pd.to_numeric(df[col], errors="coerce") > float(val)
            elif op == ">=":
                cond = pd.to_numeric(df[col], errors="coerce") >= float(val)
            elif op == "contains":
                cond = df[col].astype(str).str.contains(val, case=False, na=False)
            elif op == "not contains":
                cond = ~df[col].astype(str).str.contains(val, case=False, na=False)
            else:
                cond = pd.Series(True, index=df.index)
        except Exception:
            cond = pd.Series(True, index=df.index)

        mask = mask & cond if connector == "AND" else mask | cond

    return df[mask].copy()


# ---------------- Render AgGrid ----------------
def render_aggrid(df, grid_key="default_grid"):
    """
    Render dataframe in AgGrid and return selected row IDs.
    Always returns a list (never None).
    """
    if df is None or df.empty:
        st.warning("No records found.")
        return []

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection("multiple", use_checkbox=True)
    gb.configure_default_column(editable=False, filter=True)
    grid_options = gb.build()

    response = AgGrid(
        df,
        gridOptions=grid_options,
        height=400,
        width="100%",
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
        key=grid_key,
        enable_enterprise_modules=False,
    )

    # Safely extract selected rows
    selected_rows = response.get("selected_rows", []) if response else []
    if selected_rows is None:
        selected_rows = []

    if isinstance(selected_rows, pd.DataFrame):
        selected_rows = selected_rows.to_dict(orient="records")

    # Always return a list of IDs
    selected_ids = [
        row["id"] for row in selected_rows if isinstance(row, dict) and "id" in row
    ]
    return selected_ids


# ---------------- Streamlit Query Builder UI ----------------
def query_builder_ui(df):
    st.subheader("🔎 Advanced Query Builder")

    templates = load_templates()
    template_names = list(templates.keys())

    # --- Load template ---
    if template_names:
        template_choice = st.selectbox("Load saved template", ["-- New Query --"] + template_names)
        if template_choice != "-- New Query --":
            conditions = templates[template_choice].get("conditions", [])
            connector = templates[template_choice].get("connector", "AND")
        else:
            conditions, connector = [], "AND"
    else:
        template_choice, conditions, connector = "-- New Query --", [], "AND"

    # --- Start form ---
    with st.form(key="query_builder_form"):
        st.write("### Conditions")
        new_conditions = []
        cols = list(df.columns)
        operators = ["=", "!=", "<", "<=", ">", ">=", "contains", "not contains"]

        num_rules = st.number_input(
            "Number of conditions",
            min_value=1,
            max_value=5,
            value=max(len(conditions), 1),
            step=1,
        )

        for i in range(num_rules):
            col = st.selectbox(
                f"Column {i+1}",
                cols,
                index=cols.index(conditions[i][0]) if i < len(conditions) and conditions[i][0] in cols else 0,
                key=f"col_{i}",
            )
            op = st.selectbox(
                f"Operator {i+1}",
                operators,
                index=operators.index(conditions[i][1]) if i < len(conditions) and conditions[i][1] in operators else 0,
                key=f"op_{i}",
            )
            val = st.text_input(
                f"Value {i+1}",
                conditions[i][2] if i < len(conditions) else "",
                key=f"val_{i}",
            )
            new_conditions.append((col, op, val))

        connector = st.radio("Connector", ["AND", "OR"], index=0 if connector == "AND" else 1)

        template_name = st.text_input("Template name")

        run_query = st.form_submit_button("Run Query")
        save_template = st.form_submit_button("💾 Save Template")

    # --- Handle Run Query ---
    if run_query:
        filtered_df = apply_conditions(df, new_conditions, connector)
        st.success(f"{len(filtered_df)} records found")

        if not filtered_df.empty:
            selected_ids = render_aggrid(filtered_df, grid_key="query_results_grid")
            st.write("Selected IDs:", selected_ids)

            csv = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download All Results (CSV)",
                data=csv,
                file_name="query_results.csv",
                mime="text/csv",
            )

            if selected_ids:
                ids_df = pd.DataFrame(selected_ids, columns=["id"])
                ids_csv = ids_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download Selected IDs (CSV)",
                    data=ids_csv,
                    file_name="selected_ids.csv",
                    mime="text/csv",
                )

    # --- Handle Save Template ---
    if save_template:
        if template_name.strip():
            templates[template_name.strip()] = {
                "conditions": new_conditions,
                "connector": connector,
            }
            save_templates(templates)
            st.success(f"Template '{template_name}' saved! ✅")
            # No rerun needed; UI stays active
        else:
            st.warning("⚠️ Please enter a template name before saving.")
