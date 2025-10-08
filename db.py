import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load local .env (Render will use environment variables automatically)
load_dotenv()

# Get credentials
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD", "test1234$"))  # encode special chars
DB_HOST = os.getenv("DB_HOST", "aws-1-us-east-2.pooler.supabase.com")  # Supabase pooler host
DB_PORT = os.getenv("DB_PORT", "5432")  # pooler port
DB_NAME = os.getenv("DB_NAME", "registration_form")

# Build SQLAlchemy URL
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print("DATABASE_URL =", DATABASE_URL)  # Optional for debugging

# Create engine & session
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
