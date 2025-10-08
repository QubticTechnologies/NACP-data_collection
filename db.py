# census_app/registration_test/db.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load .env file locally (Render will use its environment variables automatically)
load_dotenv()

# Get DB credentials from environment variables
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "test1234$")
DB_HOST = os.getenv("DB_HOST", "db.apbkobhfnmcqqzqeeqss.supabase.co")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "registration_form")

# Build the SQLAlchemy database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Optional: print for debugging (remove in production)
print("DATABASE_URL =", DATABASE_URL)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Helper function to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
