import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if running in local mode
LOCAL_DEV = os.getenv("LOCAL_DEV", "1").lower() in ["1", "true", "yes"]

if LOCAL_DEV:
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "sherline10152")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "agri_census")

    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    # Use Streamlit secrets for deployment
    import streamlit as st
    secrets = st.secrets["postgres"]
    DB_USER = secrets["user"]
    DB_PASS = secrets["password"]
    DB_HOST = secrets["host"]
    DB_PORT = secrets["port"]
    DB_NAME = secrets["dbname"]

    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_connection():
    """Returns a raw connection from SQLAlchemy engine."""
    try:
        conn = engine.connect()
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None


def get_session():
    """Returns a new SQLAlchemy session."""
    try:
        session = SessionLocal()
        return session
    except Exception as e:
        print(f"❌ Failed to create session: {e}")
        return None


def test_connection():
    """Test database connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")


if __name__ == "__main__":
    test_connection()
