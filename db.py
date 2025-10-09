# db.py
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv
import time

load_dotenv()  # load .env file

DB_USER = os.getenv("DB_USER", "agri_data_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "lo7GjOG52LrKPTlk2wDEnNgq1965WG0Q")
DB_HOST = os.getenv("DB_HOST", "dpg-d3jgpvc9c44c73bs8m60-a.oregon-postgres.render.com")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "agri_data")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = None

def connect_with_retries(retries=5, delay=3):
    global engine
    attempt = 0
    while attempt < retries:
        try:
            engine = create_engine(DATABASE_URL, pool_pre_ping=True)
            # simple test
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Database connected!")
            return engine
        except OperationalError as e:
            print(f"⚠️ Database connection failed (attempt {attempt+1}/{retries}): {e}")
            time.sleep(delay)
            attempt += 1
    print("❌ Could not connect to database after retries.")
    return None
