import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env (for local dev)
load_dotenv()

# --- Supabase credentials ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")  # Direct DB URL from Supabase (recommended)

# --- Local fallback ---
LOCAL_DB_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/agri_census"

# --- Determine which connection to use ---
if SUPABASE_DB_URL:
    DATABASE_URL = SUPABASE_DB_URL
elif SUPABASE_URL and SUPABASE_KEY:
    # ⚠️ Replace the placeholder below with your actual Supabase credentials.
    # Make sure to remove [ ] and quotes from password if it contains special characters.
    DATABASE_URL = (
        "postgresql+psycopg2://postgres.dtpioxkmtytszogsqyfa:"
        "test1234$"
        "@aws-1-us-east-2.pooler.supabase.com:6543/postgres"
    )
else:
    DATABASE_URL = LOCAL_DB_URL

# --- Create SQLAlchemy engine ---
try:
    engine = create_engine(DATABASE_URL, echo=False)
    print("✅ Connected to database successfully.")
except Exception as e:
    print("❌ Database connection failed:", e)
