# census_app/modules/admin_dashboard/reports.py

import pandas as pd
from sqlalchemy import text
from census_app.config import engine

def generate_report(report_type="summary", start_date=None, end_date=None):
    """
    Generate different types of reports from the database.

    Args:
        report_type (str): Type of report ('summary', 'detailed')
        start_date (str or datetime): Optional start date filter 'YYYY-MM-DD'
        end_date (str or datetime): Optional end date filter 'YYYY-MM-DD'

    Returns:
        pd.DataFrame: Report data as a DataFrame.
    """
    with engine.connect() as conn:
        if report_type == "summary":
            query = """
                SELECT 
                    COUNT(DISTINCT holders.id) AS total_holders,
                    COUNT(DISTINCT holdings.id) AS total_holdings,
                    COUNT(DISTINCT agents.id) AS total_agents
                FROM holders
                LEFT JOIN holdings ON holdings.holder_id = holders.id
                LEFT JOIN agents ON agents.id = holders.assigned_agent_id
            """
            df = pd.read_sql_query(text(query), conn)

        elif report_type == "detailed":
            query = """
                SELECT 
                    holders.id AS holder_id,
                    holders.full_name AS holder_name,
                    holdings.parcel_no,
                    holdings.total_acres,
                    agents.full_name AS agent_name,
                    holders.status AS holder_status,
                    holders.last_updated
                FROM holders
                LEFT JOIN holdings ON holdings.holder_id = holders.id
                LEFT JOIN agents ON agents.id = holders.assigned_agent_id
            """
            if start_date and end_date:
                query += " WHERE holders.last_updated BETWEEN :start_date AND :end_date"
                df = pd.read_sql_query(
                    text(query),
                    conn,
                    params={"start_date": start_date, "end_date": end_date}
                )
            else:
                df = pd.read_sql_query(text(query), conn)

        else:
            raise ValueError(f"Unknown report type: {report_type}")

    return df

# ---------------- Test run ----------------
if __name__ == "__main__":
    print(generate_report("summary"))
    print(generate_report("detailed").head())
