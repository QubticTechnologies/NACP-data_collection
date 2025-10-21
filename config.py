import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# --------------------------------------------------------
# Environment Setup
# --------------------------------------------------------
os.environ["LOCAL_DEV"] = "1"  # force local mode
load_dotenv()

LOCAL_DEV = os.environ.get("LOCAL_DEV", "0") == "1"

# --------------------------------------------------------
# Database Configuration
# --------------------------------------------------------
if LOCAL_DEV:
    DB_USER = os.getenv("LOCAL_DB_USER", "agri_user")
    DB_PASSWORD = os.getenv("LOCAL_DB_PASSWORD", "sherline10152")
    DB_HOST = os.getenv("LOCAL_DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("LOCAL_DB_PORT", 5432))
    DB_NAME = os.getenv("LOCAL_DB_NAME", "agri_census")
    DB_SSLMODE = "disable"
else:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_NAME = os.getenv("DB_NAME")
    DB_SSLMODE = "require"

SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode={DB_SSLMODE}"
)

# --------------------------------------------------------
# SQLAlchemy Engine & Session
# --------------------------------------------------------
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

# --------------------------------------------------------
# Test Connection (Optional)
# --------------------------------------------------------
def test_connection():
    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version();")).fetchone()
            print(f"✅ [DB] Connected successfully → {version[0]}")
    except Exception as e:
        print(f"❌ [DB] Connection failed: {e}")

if __name__ == "__main__":
    test_connection()

# --------------------------------------------------------
# Table Constants
# --------------------------------------------------------
USERS_TABLE = "users"
HOLDERS_TABLE = "holders"
HOUSEHOLD_MEMBERS_TABLE = "household_members"
HOLDING_LABOUR_TABLE = "holding_labour"
HOLDING_LABOUR_PERM_TABLE = "holding_labour_permanent"
HOLDER_SURVEY_PROGRESS_TABLE = "holder_survey_progress"

# --------------------------------------------------------
# Roles
# --------------------------------------------------------
ROLE_HOLDER = "Holder"
ROLE_AGENT = "Agent"
ROLE_ADMIN = "Admin"

# --------------------------------------------------------
# Status
# --------------------------------------------------------
STATUS_PENDING = "pending"
STATUS_ACTIVE = "active"
STATUS_APPROVED = "approved"

# --------------------------------------------------------
# Survey Config
# --------------------------------------------------------
TOTAL_SURVEY_SECTIONS = 5

# --------------------------------------------------------
# Email Settings
# --------------------------------------------------------
EMAIL_USER = os.getenv("EMAIL_USER", "your_email@example.com")
EMAIL_PASS = os.getenv("EMAIL_PASS", "")

# --------------------------------------------------------
# Enumerations & Constants
# --------------------------------------------------------
SEX_OPTIONS = ["Male", "Female", "Other"]

MARITAL_STATUS_OPTIONS = [
    "Single", "Married", "Divorced", "Separated", "Widowed",
    "Common-Law", "Prefer not to disclose"
]

NATIONALITY_OPTIONS = ["Bahamian", "Other"]

EDUCATION_OPTIONS = [
    "No Schooling", "Primary", "Junior Secondary", "Senior Secondary",
    "Undergraduate", "Masters", "Doctorate", "Vocational", "Professional Designation"
]

AG_TRAINING_OPTIONS = ["Yes", "No"]

PRIMARY_OCC_OPTIONS = ["Agriculture", "Other"]

OCCUPATION_OPTIONS = [
    "Agriculture", "Fishing", "Professional/ Technical", "Administrative/ Manager",
    "Sales", "Customer Service", "Tourism", "Not Economically Active", "Other"
]

RELATIONSHIP_OPTIONS = [
    "Spouse/ Partner", "Son", "Daughter", "In-Laws", "Grandchild",
    "Parent/ Parent-in-law", "Other Relative", "Non-Relative"
]

WORKING_TIME_OPTIONS = ["N", "F", "P", "P3", "P6", "P7"]
