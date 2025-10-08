import os
from sqlalchemy import create_engine, text

# Get database URL from environment variable (Render / GitHub)
# Fallback to direct URL if env variable is not set
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:test1234$@db.dtpioxkmtytszogsqyfa.supabase.co:5432/registration_form"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Function to test DB connection
def test_db_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW();")).fetchone()
            print("✅ Database connected successfully:", result)
            return True
    except Exception as e:
        print("❌ Database connection failed:", e)
        return False

# Run test automatically if this file is executed directly
if __name__ == "__main__":
    test_db_connection()
