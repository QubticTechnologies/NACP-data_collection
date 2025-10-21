# census_app/modules/admin_dashboard/approval.py

from sqlalchemy import text
from census_app.config import engine

# ---------------- Bulk Approve ----------------
def bulk_approve(table_name, ids):
    """
    Approve multiple records by updating their status to 'approved'.
    Returns the number of records affected.
    """
    if not ids:
        return 0
    query = text(f"""
        UPDATE {table_name}
        SET status = 'approved'
        WHERE id = ANY(:ids)
    """)
    with engine.begin() as conn:
        result = conn.execute(query, {"ids": ids})
    return result.rowcount

# ---------------- Bulk Reject ----------------
def bulk_reject(table_name, ids):
    """
    Reject multiple records by updating their status to 'rejected'.
    Returns the number of records affected.
    """
    if not ids:
        return 0
    query = text(f"""
        UPDATE {table_name}
        SET status = 'rejected'
        WHERE id = ANY(:ids)
    """)
    with engine.begin() as conn:
        result = conn.execute(query, {"ids": ids})
    return result.rowcount

# ---------------- Bulk Delete ----------------
def bulk_delete(table_name, ids):
    """
    Delete multiple records from the table.
    Returns the number of records deleted.
    """
    if not ids:
        return 0
    query = text(f"""
        DELETE FROM {table_name}
        WHERE id = ANY(:ids)
    """)
    with engine.begin() as conn:
        result = conn.execute(query, {"ids": ids})
    return result.rowcount
