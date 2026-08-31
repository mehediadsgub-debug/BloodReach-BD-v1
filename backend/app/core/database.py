import os
import tempfile
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.base import Base

# Construct DATABASE_URL with Cloud PostgreSQL formatting (Neon / Supabase / Railway)
RAW_DATABASE_URL = os.getenv("DATABASE_URL")
if RAW_DATABASE_URL:
    if RAW_DATABASE_URL.startswith("postgres://"):
        PG_URL = RAW_DATABASE_URL.replace("postgres://", "postgresql://", 1)
    else:
        PG_URL = RAW_DATABASE_URL
else:
    PG_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

try:
    engine = create_engine(
        PG_URL,
        pool_pre_ping=True,
        pool_recycle=300
    )
    with engine.connect() as conn:
        pass
except Exception as e:
    is_serverless = os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")
    if is_serverless:
        sqlite_path = os.path.join(tempfile.gettempdir(), "bloodreach.db")
    else:
        sqlite_path = "./bloodreach.db"
    SQLITE_URL = f"sqlite:///{sqlite_path}"
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to yield database session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DIVISIONS_DATA = [
    (1, "Dhaka", "ঢাকা"),
    (2, "Chattogram", "চট্টগ্রাম"),
    (3, "Rajshahi", "রাজশাহী"),
    (4, "Khulna", "খুলনা"),
    (5, "Barishal", "বরিশাল"),
    (6, "Sylhet", "সিলেট"),
    (7, "Rangpur", "রংপুর"),
    (8, "Mymensingh", "ময়মনসিংহ"),
]

DISTRICTS_DATA = [
    ("Dhaka", "ঢাকা", 1), ("Gazipur", "গাজীপুর", 1), ("Narayanganj", "নারায়ণগঞ্জ", 1),
    ("Narsingdi", "নরসিংদী", 1), ("Manikganj", "মানিকগঞ্জ", 1), ("Munshiganj", "মুন্সিগঞ্জ", 1),
    ("Kishoreganj", "কিশোরগঞ্জ", 1), ("Tangail", "টাঙ্গাইল", 1), ("Faridpur", "ফরিদপুর", 1),
    ("Gopalganj", "গোপালগঞ্জ", 1), ("Madaripur", "মাদারীপুর", 1), ("Shariatpur", "শরীয়তপুর", 1),
    ("Rajbari", "রাজবাড়ী", 1),
    ("Chattogram", "চট্টগ্রাম", 2), ("Cox's Bazar", "কক্সবাজার", 2), ("Rangamati", "রাঙ্গামাটি", 2),
    ("Bandarban", "বান্দরবান", 2), ("Khagrachhari", "খাগড়াছড়ি", 2), ("Feni", "ফেনী", 2),
    ("Noakhali", "নোয়াখালী", 2), ("Lakshmipur", "লক্ষ্মীপুর", 2), ("Comilla", "কুমিল্লা", 2),
    ("Chandpur", "চাঁদপুর", 2), ("Brahmanbaria", "ব্রাহ্মণবাড়িয়া", 2),
    ("Rajshahi", "রাজশাহী", 3), ("Natore", "নাটোর", 3), ("Naogaon", "নওগাঁ", 3),
    ("Chapainawabganj", "চাঁপাইনবাবগঞ্জ", 3), ("Pabna", "পাবনা", 3), ("Sirajganj", "সিরাজগঞ্জ", 3),
    ("Bogura", "বগুড়া", 3), ("Joypurhat", "জয়পুরহাট", 3),
    ("Khulna", "খুলনা", 4), ("Bagerhat", "বাগেরহাট", 4), ("Satkhira", "সাতক্ষীরা", 4),
    ("Jashore", "যশোর", 4), ("Narail", "নড়াইল", 4), ("Magura", "মাগুরা", 4),
    ("Jhenaidah", "ঝিনাইদহ", 4), ("Kushtia", "কুষ্টিয়া", 4), ("Meherpur", "মেহেরপুর", 4),
    ("Chuadanga", "চুয়াডাঙ্গা", 4),
    ("Barishal", "বরিশাল", 5), ("Bhola", "ভোলা", 5), ("Jhalokati", "ঝালকাঠি", 5),
    ("Pirojpur", "পিরোজপুর", 5), ("Patuakhali", "পটুয়াখালী", 5), ("Barguna", "বরগুনা", 5),
    ("Sylhet", "সিলেট", 6), ("Moulvibazar", "মৌলভীবাজার", 6), ("Habiganj", "হবিগঞ্জ", 6),
    ("Sunamganj", "সুনামগঞ্জ", 6),
    ("Rangpur", "রংপুর", 7), ("Gaibandha", "গাইবান্ধা", 7), ("Nilphamari", "নীলফামারী", 7),
    ("Kurigram", "কুড়িগ্রাম", 7), ("Lalmonirhat", "লালমনিরহাট", 7), ("Dinajpur", "দিনাজপুর", 7),
    ("Thakurgaon", "ঠাকুরগাঁও", 7), ("Panchagarh", "পঞ্চগড়", 7),
    ("Mymensingh", "ময়মনসিংহ", 8), ("Jamalpur", "জামালপুর", 8), ("Netrokona", "নেত্রকোণা", 8),
    ("Sherpur", "শেরপুর", 8)
]


def init_db():
    """Initialize database tables, apply migrations, and seed structural reference data"""
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
                except Exception:
                    pass
    except Exception as e:
        print(f"[WARN] Migration note: {e}")

    # Auto-seed divisions and districts if missing
    try:
        from app.models.division import Division
        from app.models.district import District
        from app.models.user import User, UserRole
        from app.core.security import hash_password

        db = SessionLocal()
        try:
            div_count = db.query(Division).count()
            if div_count == 0:
                for div_id, name, bn_name in DIVISIONS_DATA:
                    db.add(Division(division_id=div_id, name=name, bn_name=bn_name))
                db.commit()

            dist_count = db.query(District).count()
            if dist_count == 0:
                for name, bn_name, div_id in DISTRICTS_DATA:
                    db.add(District(name=name, bn_name=bn_name, division_id=div_id))
                db.commit()

            # Seed default admin if user table is completely empty
            user_count = db.query(User).count()
            if user_count == 0:
                dhaka_dist = db.query(District).filter(District.name == "Dhaka").first()
                admin_user = User(
                    full_name="Md. Mehedi Hasan",
                    phone="01700000000",
                    email="MehediMiaAdmin@gmail.com",
                    hashed_password=hash_password("Mehedi@1234"),
                    role=UserRole.SUPERADMIN,
                    district_id=dhaka_dist.district_id if dhaka_dist else 1,
                    is_active=True,
                    is_verified=True
                )
                db.add(admin_user)
                db.commit()
        finally:
            db.close()
    except Exception as e:
        print(f"[WARN] Reference data seed note: {e}")