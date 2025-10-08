# census_app/db.py

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL not set in environment variables or .env file")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=True,       # Logs SQL statements; set False in production
    future=True      # SQLAlchemy 2.0 style
)

# --------------------------
# Test Connection Function
# --------------------------
def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            print("✅ Connected to database:", result.scalar())
    except Exception as e:
        print("❌ [DB] Connection failed:", e)

# --------------------------
# Example Query Function
# --------------------------
def fetch_sample(query: str):
    """Fetch results from a SQL query (for testing)."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            return result.fetchall()
    except Exception as e:
        print("❌ Query failed:", e)
        return []

# --------------------------
# Run test if executed directly
# --------------------------
if __name__ == "__main__":
    print("🔍 Testing database connection...")
    test_connection()
