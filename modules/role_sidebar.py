import streamlit as st
from sqlalchemy import text
from census_app.db import engine
from census_app.config import TOTAL_SURVEY_SECTIONS

# Lazy import to avoid circular issues
def _import_survey_sidebar():
    from census_app.modules.survey_sidebar import survey_sidebar
    return survey_sidebar

survey_sidebar = _import_survey_sidebar()

# ---------------- Fetch Holders ----------------
def fetch_holder_options(user_id=None, agent_id=None, verified_only=False):
    """
    Return a dict: {holder_name (ID): holder_id} for a given user/agent.
    """
    query = "SELECT holder_id, name AS full_name FROM holders"
    conditions = []
    params = {}

    if user_id:
        conditions.append("owner_id = :uid")
        params["uid"] = user_id
    if agent_id:
        conditions.append("assigned_agent_id = :aid")
        params["aid"] = agent_id
    if verified_only:
        conditions.append("status = 'active'")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY holder_id"

    with engine.connect() as conn:
        result = conn.execute(text(query), params).mappings().all()

    return {f"{row['full_name']} (ID: {row['holder_id']})": row['holder_id'] for row in result}


# ---------------- Role Sidebar ----------------
def role_sidebar(user_role=None, user_id=None, agent_id=None, holder_id=None):
    st.sidebar.markdown("## Navigation")

    if not user_role:
        st.sidebar.info("🔑 Please login to see your dashboard.")
        return

    # ---------------- Holder Dashboard ----------------
    if user_role.lower() == "holder":
        st.sidebar.markdown("### Holder Dashboard")
        st.sidebar.info("Complete your survey sections here.")

        holder_options = fetch_holder_options(user_id=user_id, verified_only=True)
        if not holder_options:
            st.sidebar.warning("⚠️ No holders available.")
            return

        select_key = f"holder_selectbox_{user_role}"

        # Pre-select holder if provided
        if holder_id and holder_id in holder_options.values():
            selected_holder_name = [
                name for name, hid in holder_options.items() if hid == holder_id
            ][0]
        else:
            selected_holder_name = st.sidebar.selectbox(
                "Select Holder",
                options=list(holder_options.keys()),
                key=select_key
            )

        holder_id = holder_options[selected_holder_name]
        st.session_state["selected_holder_id"] = holder_id

        st.sidebar.markdown(
            f"<h4 style='text-align:center; font-weight:bold;'>{selected_holder_name}</h4>",
            unsafe_allow_html=True
        )
        st.sidebar.markdown("---")

        # ---------------- Render Survey ----------------
        # Section 1 automatically renders without needing holder_id
        survey_sidebar(holder_id, prefix=f"role_sidebar_{holder_id}")

    # ---------------- Agent Dashboard ----------------
    elif user_role.lower() == "agent":
        st.sidebar.markdown("### Agent Dashboard")
        st.sidebar.info("Access your assigned holders here.")

        holder_options = fetch_holder_options(agent_id=agent_id, verified_only=True)
        if not holder_options:
            st.sidebar.warning("⚠️ No holders assigned to you yet.")
            return

        st.sidebar.markdown(f"Assigned Holders: {len(holder_options)}")

        select_key = "agent_holder_selectbox"

        # Pre-select holder if provided
        if holder_id and holder_id in holder_options.values():
            selected_holder_name = [
                name for name, hid in holder_options.items() if hid == holder_id
            ][0]
        else:
            selected_holder_name = st.sidebar.selectbox(
                "Select Holder to Review",
                options=list(holder_options.keys()),
                key=select_key
            )

        holder_id = holder_options[selected_holder_name]
        st.session_state["selected_holder_id"] = holder_id

        survey_sidebar(holder_id, prefix=f"agent_sidebar_{holder_id}")

    # ---------------- Admin Dashboard ----------------
    elif user_role.lower() == "admin":
        st.sidebar.markdown("### Admin Dashboard")
        st.sidebar.info("Manage users, agents, and holders here.")

        holder_options = fetch_holder_options(verified_only=False)
        if not holder_options:
            st.sidebar.warning("⚠️ No holders in system.")
            return

        st.sidebar.markdown(f"Total Holders: {len(holder_options)}")

        select_key = "admin_holder_selectbox"

        # Pre-select holder if provided
        if holder_id and holder_id in holder_options.values():
            selected_holder_name = [
                name for name, hid in holder_options.items() if hid == holder_id
            ][0]
        else:
            selected_holder_name = st.sidebar.selectbox(
                "Select Holder to Review / Verify",
                options=list(holder_options.keys()),
                key=select_key
            )

        holder_id = holder_options[selected_holder_name]
        st.session_state["selected_holder_id"] = holder_id

        survey_sidebar(holder_id, prefix=f"admin_sidebar_{holder_id}")

        # ---------------- Admin Actions ----------------
        st.sidebar.markdown("---")
        st.sidebar.subheader("Admin Actions")
        st.sidebar.button("Verify Holder", key="verify_holder_btn")
        st.sidebar.button("Assign Holder to Agent", key="assign_holder_btn")
