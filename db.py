from sqlalchemy import create_engine, text
import os

# -------------------------------
# Database Configuration
# -------------------------------
DB_USER = os.getenv("LOCAL_DB_USER", "postgres")
DB_PASSWORD = os.getenv("LOCAL_DB_PASSWORD", "sherline10152")
DB_HOST = os.getenv("LOCAL_DB_HOST", "localhost")
DB_PORT = os.getenv("LOCAL_DB_PORT", "5432")
DB_NAME = os.getenv("LOCAL_DB_NAME", "agri_census")

# Build Connection URL
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create Engine
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# -------------------------------
# Test Database Connection
# -------------------------------
def test_connection():
    try:
        with engine.begin() as conn:
            version = conn.execute(text("SELECT version();")).scalar()
            print(f"✅ Connected to PostgreSQL: {version}")
    except Exception as e:
        print(f"❌ [DB] Connection failed: {e}")

# Run test when loaded locally
if __name__ == "__main__":
    test_connection()
