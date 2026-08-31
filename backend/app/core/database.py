from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Base

# Construct PostgreSQL DATABASE_URL
DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to yield database session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from sqlalchemy import text


def init_db():
    """Initialize database tables and add new columns if they do not exist"""
    Base.metadata.create_all(bind=engine)
    try:
        with engine.begin() as conn:
            # Safely add new columns to blood_requests table
            new_columns = [
                "ALTER TABLE blood_requests ADD COLUMN IF NOT EXISTS nid_number VARCHAR(30)",
                "ALTER TABLE blood_requests ADD COLUMN IF NOT EXISTS nid_name VARCHAR(150)",
                "ALTER TABLE blood_requests ADD COLUMN IF NOT EXISTS nid_dob VARCHAR(30)",
                "ALTER TABLE blood_requests ADD COLUMN IF NOT EXISTS nid_image_url TEXT",
                "ALTER TABLE blood_requests ADD COLUMN IF NOT EXISTS hospital_name VARCHAR(200)",
                "ALTER TABLE blood_requests ADD COLUMN IF NOT EXISTS hospital_cabin VARCHAR(100)",
                "ALTER TABLE blood_requests ADD COLUMN IF NOT EXISTS verification_status VARCHAR(50) DEFAULT 'PENDING_VERIFICATION'",
                "ALTER TABLE blood_requests ADD COLUMN IF NOT EXISTS admin_notes TEXT",
                "ALTER TABLE blood_requests ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP WITH TIME ZONE",
                "ALTER TABLE blood_requests ADD COLUMN IF NOT EXISTS verified_by_id UUID REFERENCES users(user_id) ON DELETE SET NULL"
            ]
            for col_sql in new_columns:
                try:
                    conn.execute(text(col_sql))
                except Exception as e:
                    pass
    except Exception as e:
        print(f"[WARN] Migration note: {e}")