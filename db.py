import os
from sqlalchemy import create_engine, text

# Get Supabase connection mode from environment variable (optional)
# Use "POOLER" to connect via Shared Pooler, default is Direct Connection
DB_MODE = os.environ.get("DB_MODE", "DIRECT").upper()  # DIRECT or POOLER

# Credentials
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "test1234$")
DB_HOST = os.environ.get("DB_HOST", "db.dtpioxkmtytszogsqyfa.supabase.co")
DB_NAME = os.environ.get("DB_NAME", "registration_form")

# Choose port based on connection mode
if DB_MODE == "POOLER":
    DB_PORT = os.environ.get("DB_PORT", "6543")  # Shared Pooler default
else:
    DB_PORT = os.environ.get("DB_PORT", "5432")  # Direct Connection default

# Build the SQLAlchemy database URL
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Function to test connection
def test_db_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW();")).fetchone()
            print(f"✅ DB Connected ({DB_MODE}):", result)
            return True
    except Exception as e:
        print(f"❌ DB Connection Failed ({DB_MODE}):", e)
        return False

# Run test automatically if executed directly
if __name__ == "__main__":
    test_db_connection()
