import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import text

def status_icon(status):
    return {'approved':'🟢','pending':'🟡','rejected':'🔴'}.get(status, status)

def highlight_recent(df, hours=24):
    if 'last_updated' not in df.columns or df.empty:
        df['row_style'] = ''
        return df
    df['row_style'] = df['last_updated'].apply(
        lambda x: 'background-color: #d0f0fd' if pd.notna(x) and datetime.now() - pd.to_datetime(x) <= timedelta(hours=hours) else ''
    )
    return df

def fetch_table(engine, table_name):
    with engine.connect() as conn:
        data = conn.execute(text(f"SELECT * FROM {table_name}")).mappings().all()
    df = pd.DataFrame(data)
    if not df.empty and 'status' in df.columns:
        df['status_icon'] = df['status'].apply(status_icon)
    if 'last_updated' not in df.columns:
        df['last_updated'] = datetime.now()
    return highlight_recent(df)
