# db.py
import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine with pool_pre_ping to avoid stale connections
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # Checks if connection is alive before use
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,  # Wait up to 30s for a connection
)

def test_connection(retries=3, delay=5):
    """
    Test DB connection with retries for Shared Pooler.
    """
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version();"))
                print("✅ Connected to DB:", result.fetchone())
                return True
        except OperationalError as e:
            print(f"❌ Attempt {attempt}: Connection failed:", e)
            if attempt < retries:
                print(f"⏳ Retrying in {delay}s...")
                time.sleep(delay)
            else:
                print("❌ All connection attempts failed.")
                return False

if __name__ == "__main__":
    test_connection()
