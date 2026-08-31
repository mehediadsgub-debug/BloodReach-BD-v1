#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║         BloodReach BD — Automatic Database Setup Script          ║
║                                                                  ║
║  এই script এক কমান্ডে সব কিছু তৈরি করবে:                         ║
║    ✓  bloodreach_bd database তৈরি                                ║
║    ✓  ১১টি Table তৈরি (relations, constraints, indexes সহ)       ║
║    ✓  ৮টি Division seed                                         ║
║    ✓  ৬৪টি District seed                                        ║
║                                                                  ║
║  Usage:  python setup_db.py                                      ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# .env ফাইল থেকে config load করো
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "bloodreach_bd")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")

# ── Bangladesh এর ৮টি Division ────────────────────────────────────────────────
DIVISIONS_DATA = [
    (1, "Dhaka",        "ঢাকা"),
    (2, "Chattogram",   "চট্টগ্রাম"),
    (3, "Rajshahi",     "রাজশাহী"),
    (4, "Khulna",       "খুলনা"),
    (5, "Barishal",     "বরিশাল"),
    (6, "Sylhet",       "সিলেট"),
    (7, "Rangpur",      "রংপুর"),
    (8, "Mymensingh",   "ময়মনসিংহ"),
]

# ── Bangladesh এর ৬৪টি District ──────────────────────────────────────────────
# Format: (name_en, name_bn, division_id)
DISTRICTS_DATA = [
    # ── Dhaka Division (13) ──────────────────────────────────────
    ("Dhaka",           "ঢাকা",               1),
    ("Gazipur",         "গাজীপুর",             1),
    ("Narayanganj",     "নারায়ণগঞ্জ",          1),
    ("Narsingdi",       "নরসিংদী",             1),
    ("Manikganj",       "মানিকগঞ্জ",           1),
    ("Munshiganj",      "মুন্সিগঞ্জ",          1),
    ("Kishoreganj",     "কিশোরগঞ্জ",           1),
    ("Tangail",         "টাঙ্গাইল",            1),
    ("Faridpur",        "ফরিদপুর",             1),
    ("Gopalganj",       "গোপালগঞ্জ",           1),
    ("Madaripur",       "মাদারীপুর",           1),
    ("Shariatpur",      "শরীয়তপুর",           1),
    ("Rajbari",         "রাজবাড়ী",            1),
    # ── Chattogram Division (11) ──────────────────────────────────
    ("Chattogram",      "চট্টগ্রাম",           2),
    ("Cox's Bazar",     "কক্সবাজার",           2),
    ("Rangamati",       "রাঙ্গামাটি",          2),
    ("Bandarban",       "বান্দরবান",           2),
    ("Khagrachhari",    "খাগড়াছড়ি",          2),
    ("Feni",            "ফেনী",               2),
    ("Noakhali",        "নোয়াখালী",           2),
    ("Lakshmipur",      "লক্ষ্মীপুর",         2),
    ("Comilla",         "কুমিল্লা",            2),
    ("Chandpur",        "চাঁদপুর",             2),
    ("Brahmanbaria",    "ব্রাহ্মণবাড়িয়া",     2),
    # ── Rajshahi Division (8) ─────────────────────────────────────
    ("Rajshahi",        "রাজশাহী",             3),
    ("Natore",          "নাটোর",               3),
    ("Naogaon",         "নওগাঁ",               3),
    ("Chapainawabganj", "চাঁপাইনবাবগঞ্জ",     3),
    ("Pabna",           "পাবনা",               3),
    ("Sirajganj",       "সিরাজগঞ্জ",           3),
    ("Bogura",          "বগুড়া",              3),
    ("Joypurhat",       "জয়পুরহাট",           3),
    # ── Khulna Division (10) ──────────────────────────────────────
    ("Khulna",          "খুলনা",               4),
    ("Bagerhat",        "বাগেরহাট",            4),
    ("Satkhira",        "সাতক্ষীরা",           4),
    ("Jashore",         "যশোর",               4),
    ("Narail",          "নড়াইল",              4),
    ("Magura",          "মাগুরা",              4),
    ("Jhenaidah",       "ঝিনাইদহ",             4),
    ("Kushtia",         "কুষ্টিয়া",           4),
    ("Meherpur",        "মেহেরপুর",            4),
    ("Chuadanga",       "চুয়াডাঙ্গা",         4),
    # ── Barishal Division (6) ─────────────────────────────────────
    ("Barishal",        "বরিশাল",              5),
    ("Bhola",           "ভোলা",               5),
    ("Patuakhali",      "পটুয়াখালী",          5),
    ("Pirojpur",        "পিরোজপুর",            5),
    ("Barguna",         "বরগুনা",              5),
    ("Jhalokati",       "ঝালকাঠি",             5),
    # ── Sylhet Division (4) ───────────────────────────────────────
    ("Sylhet",          "সিলেট",               6),
    ("Moulvibazar",     "মৌলভীবাজার",          6),
    ("Habiganj",        "হবিগঞ্জ",             6),
    ("Sunamganj",       "সুনামগঞ্জ",           6),
    # ── Rangpur Division (8) ──────────────────────────────────────
    ("Rangpur",         "রংপুর",               7),
    ("Dinajpur",        "দিনাজপুর",            7),
    ("Kurigram",        "কুড়িগ্রাম",          7),
    ("Gaibandha",       "গাইবান্ধা",           7),
    ("Nilphamari",      "নীলফামারী",           7),
    ("Lalmonirhat",     "লালমনিরহাট",          7),
    ("Panchagarh",      "পঞ্চগড়",             7),
    ("Thakurgaon",      "ঠাকুরগাঁও",          7),
    # ── Mymensingh Division (4) ───────────────────────────────────
    ("Mymensingh",      "ময়মনসিংহ",           8),
    ("Jamalpur",        "জামালপুর",            8),
    ("Sherpur",         "শেরপুর",              8),
    ("Netrokona",       "নেত্রকোণা",           8),
]

# ── সম্পূর্ণ SQL Schema ────────────────────────────────────────────────────────
CREATE_TABLES_SQL = """
-- UUID support এর জন্য extension enable করো
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─────────────────────────────────────────────────────────────────
-- TABLE 1: divisions  (৮টি বিভাগ)
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS divisions (
    division_id  SERIAL       PRIMARY KEY,
    name         VARCHAR(100) NOT NULL UNIQUE,
    bn_name      VARCHAR(100)
);

-- ─────────────────────────────────────────────────────────────────
-- TABLE 2: districts  (৬৪টি জেলা)
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS districts (
    district_id  SERIAL       PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    bn_name      VARCHAR(100),
    division_id  INT          NOT NULL
                 REFERENCES divisions(division_id) ON DELETE RESTRICT,
    UNIQUE(name, division_id)
);

CREATE INDEX IF NOT EXISTS idx_districts_division ON districts(division_id);

-- ─────────────────────────────────────────────────────────────────
-- TABLE 3: users  (সকল registered ব্যবহারকারী)
-- Roles: DONOR | SEEKER | HOSPITAL_ADMIN | SUPERADMIN
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    user_id         UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name       VARCHAR(150) NOT NULL,
    email           VARCHAR(255) NOT NULL UNIQUE,
    phone           VARCHAR(20)  UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    role            VARCHAR(20)  NOT NULL
                    CHECK (role IN ('DONOR', 'SEEKER', 'HOSPITAL_ADMIN', 'SUPERADMIN')),
    district_id     INT
                    REFERENCES districts(district_id) ON DELETE SET NULL,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    is_verified     BOOLEAN      NOT NULL DEFAULT FALSE,
    profile_pic_url TEXT,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_role     ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_district ON users(district_id);
CREATE INDEX IF NOT EXISTS idx_users_email    ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_active   ON users(is_active);

-- ─────────────────────────────────────────────────────────────────
-- TABLE 4: donors  (users এর সাথে 1:1 relation)
-- Blood groups: A+, A-, B+, B-, AB+, AB-, O+, O-
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS donors (
    donor_id           UUID       PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id            UUID       NOT NULL UNIQUE
                       REFERENCES users(user_id) ON DELETE CASCADE,
    blood_group        VARCHAR(5) NOT NULL
                       CHECK (blood_group IN ('A+','A-','B+','B-','AB+','AB-','O+','O-')),
    is_available       BOOLEAN    NOT NULL DEFAULT TRUE,
    last_donation_date DATE,
    total_donations    INT        NOT NULL DEFAULT 0,
    weight_kg          FLOAT,
    date_of_birth      DATE,
    emergency_contact  VARCHAR(20),
    created_at         TIMESTAMP  NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMP  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_donors_blood_group ON donors(blood_group);
CREATE INDEX IF NOT EXISTS idx_donors_available   ON donors(is_available);
CREATE INDEX IF NOT EXISTS idx_donors_user        ON donors(user_id);

-- ─────────────────────────────────────────────────────────────────
-- TABLE 5: hospitals
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS hospitals (
    hospital_id    UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    name           VARCHAR(200) NOT NULL,
    address        TEXT,
    district_id    INT
                   REFERENCES districts(district_id) ON DELETE SET NULL,
    contact_phone  VARCHAR(20),
    contact_email  VARCHAR(255),
    admin_user_id  UUID
                   REFERENCES users(user_id) ON DELETE SET NULL,
    is_active      BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hospitals_district ON hospitals(district_id);
CREATE INDEX IF NOT EXISTS idx_hospitals_active   ON hospitals(is_active);

-- ─────────────────────────────────────────────────────────────────
-- TABLE 6: hospital_inventory  (প্রতি blood group এর stock)
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS hospital_inventory (
    inv_id           UUID       PRIMARY KEY DEFAULT gen_random_uuid(),
    hospital_id      UUID       NOT NULL
                     REFERENCES hospitals(hospital_id) ON DELETE CASCADE,
    blood_group      VARCHAR(5) NOT NULL
                     CHECK (blood_group IN ('A+','A-','B+','B-','AB+','AB-','O+','O-')),
    units_available  INT        NOT NULL DEFAULT 0 CHECK (units_available >= 0),
    low_stock_alert  INT        NOT NULL DEFAULT 5,
    last_updated     TIMESTAMP  NOT NULL DEFAULT NOW(),
    UNIQUE(hospital_id, blood_group)
);

CREATE INDEX IF NOT EXISTS idx_inventory_hospital    ON hospital_inventory(hospital_id);
CREATE INDEX IF NOT EXISTS idx_inventory_blood_group ON hospital_inventory(blood_group);

-- ─────────────────────────────────────────────────────────────────
-- TABLE 7: blood_requests  (Seekers দের রক্তের অনুরোধ)
-- Urgency: LOW | NORMAL | HIGH | CRITICAL
-- Status:  OPEN | IN_PROGRESS | FULFILLED | CANCELLED | EXPIRED
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS blood_requests (
    request_id        UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    seeker_id         UUID        NOT NULL
                      REFERENCES users(user_id) ON DELETE CASCADE,
    blood_group       VARCHAR(5)  NOT NULL
                      CHECK (blood_group IN ('A+','A-','B+','B-','AB+','AB-','O+','O-')),
    units_needed      INT         NOT NULL DEFAULT 1 CHECK (units_needed > 0),
    district_id       INT
                      REFERENCES districts(district_id) ON DELETE SET NULL,
    hospital_id       UUID
                      REFERENCES hospitals(hospital_id) ON DELETE SET NULL,
    urgency_level     VARCHAR(20) NOT NULL DEFAULT 'NORMAL'
                      CHECK (urgency_level IN ('LOW', 'NORMAL', 'HIGH', 'CRITICAL')),
    status            VARCHAR(20) NOT NULL DEFAULT 'OPEN'
                      CHECK (status IN ('OPEN', 'IN_PROGRESS', 'FULFILLED', 'CANCELLED', 'EXPIRED')),
    patient_name      VARCHAR(150),
    patient_condition TEXT,
    required_by       DATE,
    contact_phone     VARCHAR(20),
    created_at        TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMP   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_requests_blood_group ON blood_requests(blood_group);
CREATE INDEX IF NOT EXISTS idx_requests_district    ON blood_requests(district_id);
CREATE INDEX IF NOT EXISTS idx_requests_urgency     ON blood_requests(urgency_level);
CREATE INDEX IF NOT EXISTS idx_requests_status      ON blood_requests(status);
CREATE INDEX IF NOT EXISTS idx_requests_seeker      ON blood_requests(seeker_id);

-- ─────────────────────────────────────────────────────────────────
-- TABLE 8: request_matches  (Donor ↔ Request junction table)
-- Status: PENDING | ACCEPTED | REJECTED | COMPLETED
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS request_matches (
    match_id      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id    UUID        NOT NULL
                  REFERENCES blood_requests(request_id) ON DELETE CASCADE,
    donor_id      UUID        NOT NULL
                  REFERENCES donors(donor_id) ON DELETE CASCADE,
    status        VARCHAR(20) NOT NULL DEFAULT 'PENDING'
                  CHECK (status IN ('PENDING', 'ACCEPTED', 'REJECTED', 'COMPLETED')),
    matched_at    TIMESTAMP   NOT NULL DEFAULT NOW(),
    responded_at  TIMESTAMP,
    notes         TEXT,
    UNIQUE(request_id, donor_id)
);

CREATE INDEX IF NOT EXISTS idx_matches_request ON request_matches(request_id);
CREATE INDEX IF NOT EXISTS idx_matches_donor   ON request_matches(donor_id);
CREATE INDEX IF NOT EXISTS idx_matches_status  ON request_matches(status);

-- ─────────────────────────────────────────────────────────────────
-- TABLE 9: donations  (Confirmed donation records)
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS donations (
    donation_id    UUID       PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id       UUID       UNIQUE
                   REFERENCES request_matches(match_id) ON DELETE SET NULL,
    donor_id       UUID       NOT NULL
                   REFERENCES donors(donor_id),
    request_id     UUID
                   REFERENCES blood_requests(request_id) ON DELETE SET NULL,
    hospital_id    UUID
                   REFERENCES hospitals(hospital_id) ON DELETE SET NULL,
    blood_group    VARCHAR(5) NOT NULL,
    units_donated  INT        NOT NULL DEFAULT 1,
    donation_date  DATE       NOT NULL DEFAULT CURRENT_DATE,
    verified_by    UUID
                   REFERENCES users(user_id) ON DELETE SET NULL,
    notes          TEXT,
    created_at     TIMESTAMP  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_donations_donor    ON donations(donor_id);
CREATE INDEX IF NOT EXISTS idx_donations_hospital ON donations(hospital_id);
CREATE INDEX IF NOT EXISTS idx_donations_date     ON donations(donation_date);

-- ─────────────────────────────────────────────────────────────────
-- TABLE 10: notifications
-- Types: EMAIL | SMS | SYSTEM | PUSH
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS notifications (
    notif_id           UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id            UUID         NOT NULL
                       REFERENCES users(user_id) ON DELETE CASCADE,
    title              VARCHAR(200) NOT NULL,
    message            TEXT         NOT NULL,
    type               VARCHAR(20)  NOT NULL DEFAULT 'SYSTEM'
                       CHECK (type IN ('EMAIL', 'SMS', 'SYSTEM', 'PUSH')),
    is_read            BOOLEAN      NOT NULL DEFAULT FALSE,
    related_request_id UUID
                       REFERENCES blood_requests(request_id) ON DELETE SET NULL,
    created_at         TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notif_user   ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notif_unread ON notifications(user_id, is_read);

-- ─────────────────────────────────────────────────────────────────
-- TABLE 11: audit_logs  (Admin action history)
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id        UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id      UUID
                  REFERENCES users(user_id) ON DELETE SET NULL,
    action        VARCHAR(100) NOT NULL,
    target_table  VARCHAR(100),
    target_id     UUID,
    details       JSONB,
    ip_address    VARCHAR(45),
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_actor  ON audit_logs(actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_time   ON audit_logs(created_at);
"""


# ── Helper functions ───────────────────────────────────────────────────────────

def get_connection(dbname: str = "postgres") -> psycopg2.extensions.connection:
    """PostgreSQL এ connect করো"""
    return psycopg2.connect(
        host=DB_HOST,
        port=int(DB_PORT),
        dbname=dbname,
        user=DB_USER,
        password=DB_PASS,
    )


def print_step(step: int, total: int, msg: str):
    print(f"\n[{step}/{total}] {msg}")


def print_ok(msg: str):
    print(f"      ✅ {msg}")


def print_skip(msg: str):
    print(f"      ⏭  {msg}")


def print_info(msg: str):
    print(f"      ℹ  {msg}")


# ── Step 1: Database তৈরি করো ─────────────────────────────────────────────────

def create_database():
    print_step(1, 4, f"Database '{DB_NAME}'toyri kora hoiche..")
    conn = get_connection("postgres")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        if cur.fetchone():
            print_skip(f"Database '{DB_NAME}'age thekei ache, skip kora holo।")
        else:
            cur.execute(f'CREATE DATABASE "{DB_NAME}" ENCODING \'UTF8\'')
            print_ok(f"Database '{DB_NAME}' sofol vabe toyri kora hoiche।")
    finally:
        cur.close()
        conn.close()


# ── Step 2: সব Tables তৈরি করো ───────────────────────────────────────────────

def create_tables():
    print_step(2, 4, "11 ti Table toyri kora hocche...")
    conn = get_connection(DB_NAME)
    conn.autocommit = False
    cur = conn.cursor()
    try:
        cur.execute(CREATE_TABLES_SQL)
        conn.commit()
        tables = [
            "divisions", "districts", "users", "donors",
            "hospitals", "hospital_inventory", "blood_requests",
            "request_matches", "donations", "notifications", "audit_logs",
        ]
        for t in tables:
            print_ok(f"Table '{t}' ready")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


# ── Step 3: Divisions seed করো ────────────────────────────────────────────────

def seed_divisions():
    print_step(3, 4, "৮টি Division seed করা হচ্ছে...")
    conn = get_connection(DB_NAME)
    conn.autocommit = False
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM divisions")
        count = cur.fetchone()[0]
        if count > 0:
            print_skip(f"Division table a itimoddhe {count} ti row ache, skip kora holo।")
        else:
            for div_id, name, bn_name in DIVISIONS_DATA:
                cur.execute(
                    "INSERT INTO divisions (division_id, name, bn_name) VALUES (%s, %s, %s)",
                    (div_id, name, bn_name),
                )
            conn.commit()
            print_ok(f"{len(DIVISIONS_DATA)} ti Division sofol vabe insert hoyeche।")
            for div_id, name, bn_name in DIVISIONS_DATA:
                print_info(f"  {div_id}. {name} ({bn_name})")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


# ── Step 4: Districts seed করো ────────────────────────────────────────────────

def seed_districts():
    print_step(4, 4, "64 ti District seed kora hocche...")
    conn = get_connection(DB_NAME)
    conn.autocommit = False
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM districts")
        count = cur.fetchone()[0]
        if count > 0:
            print_skip(f"District table a itimoddhe {count}ti row ache, skip kora holo।")
        else:
            for name, bn_name, division_id in DISTRICTS_DATA:
                cur.execute(
                    "INSERT INTO districts (name, bn_name, division_id) VALUES (%s, %s, %s)",
                    (name, bn_name, division_id),
                )
            conn.commit()
            print_ok(f"{len(DISTRICTS_DATA)}ti District sofol vabe insert hoyeche।")

            # Division অনুযায়ী breakdown দেখাও
            cur.execute("""
                SELECT d.name, COUNT(dist.district_id) as cnt
                FROM divisions d
                LEFT JOIN districts dist ON d.division_id = dist.division_id
                GROUP BY d.name, d.division_id
                ORDER BY d.division_id
            """)
            for div_name, cnt in cur.fetchall():
                print_info(f"  {div_name}: {cnt}ti jela")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


# ── Main entry point ───────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("  🩸  BloodReach BD — Database Setup")
    print("=" * 65)
    print(f"\n  Host    : {DB_HOST}:{DB_PORT}")
    print(f"  Database: {DB_NAME}")
    print(f"  User    : {DB_USER}")
    print()

    try:
        create_database()
        create_tables()
        seed_divisions()
        seed_districts()

        print("\n" + "=" * 65)
        print("  ✅  Database setup সম্পূর্ণ হয়েছে!")
        print("=" * 65)
        print("""
    ekhon pgAdmin 4 খুলে 'bloodreach_bd' database-a jao।
  sekhane 11 ti table ebong seed data dekhte pabe.

    poroborti dhap:
    • pgAdmin 4 > Servers > PostgreSQL > Databases > bloodreach_bd
    • Schemas > public > Tables — ekhane sob table dekhte parbe
        """)

    except psycopg2.OperationalError as e:
        print(f"\n  ❌ Connection Error: {e}")
        print("""
  somvabbo somossa:
    1. PostgreSQL service cholche na
       → Windows Services a 'postgresql-x64-18' chalu koro
    2. Password vul
       → backend/.env file e DB_PASS sothik password dao
    3. Port occupied
       → DB_PORT=5432 correct kina dekho
        """)
        sys.exit(1)

    except psycopg2.Error as e:
        print(f"\n  ❌ Database Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
