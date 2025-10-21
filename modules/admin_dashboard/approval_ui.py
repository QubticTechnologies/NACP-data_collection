# census_app/modules/admin_dashboard/approval_ui.py

import streamlit as st
from census_app.modules.admin_dashboard.approval import (
    bulk_approve,
    bulk_reject,
    bulk_delete,
)


def render_approval_ui(entity: str, selected_ids: list):
    """
    Render approval/reject/delete buttons for selected records.
    entity: 'users' or 'holders'
    selected_ids: list of IDs selected from AgGrid
    """

    if not selected_ids:
        st.info("Select at least one record to approve, reject, or delete.")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✅ Approve Selected"):
            affected = bulk_approve(entity, selected_ids)
            if affected > 0:
                st.success(f"{affected} {entity} approved successfully.")
                st.experimental_rerun()
            else:
                st.error(f"Failed to approve {entity}. Check logs.")

    with col2:
        if st.button("❌ Reject Selected"):
            affected = bulk_reject(entity, selected_ids)
            if affected > 0:
                st.warning(f"{affected} {entity} rejected.")
                st.experimental_rerun()
            else:
                st.error(f"Failed to reject {entity}. Check logs.")

    with col3:
        if st.button("🗑️ Delete Selected"):
            affected = bulk_delete(entity, selected_ids)
            if affected > 0:
                st.error(f"{affected} {entity} deleted.")
                st.experimental_rerun()
            else:
                st.error(f"Failed to delete {entity}. Check logs.")
