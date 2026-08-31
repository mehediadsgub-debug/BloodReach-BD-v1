import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import psycopg2
from dotenv import load_dotenv

# Load env variables
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "bloodreach_bd")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")

def clean_database():
    print("========================================================")
    print("  🧹 BloodReach BD — Clearing User & Operational Data")
    print("========================================================")
    print(f"Connecting to {DB_NAME} at {DB_HOST}:{DB_PORT} as {DB_USER}...")

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        conn.autocommit = True
        cur = conn.cursor()

        tables_to_truncate = [
            "request_matches",
            "donations",
            "blood_requests",
            "hospital_inventory",
            "hospitals",
            "donors",
            "notifications",
            "audit_logs",
            "users"
        ]

        print("\nTruncating user-generated tables (preserving 64 districts & 8 divisions)...")
        for table in tables_to_truncate:
            try:
                cur.execute(f"TRUNCATE TABLE {table} CASCADE;")
                print(f"  ✔ Table '{table}' cleared successfully.")
            except Exception as e:
                print(f"  ℹ Note on '{table}': {e}")

        # Check counts
        print("\nVerifying table counts:")
        for table in tables_to_truncate:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table};")
                count = cur.fetchone()[0]
                print(f"  • {table}: {count} records")
            except Exception as e:
                pass

        cur.execute("SELECT COUNT(*) FROM divisions;")
        div_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM districts;")
        dist_count = cur.fetchone()[0]

        print(f"\n  • divisions (reference): {div_count} divisions")
        print(f"  • districts (reference): {dist_count} districts")

        cur.close()
        conn.close()

        print("\n========================================================")
        print("  ✅ Database is completely clean and ready for real users!")
        print("========================================================")

    except Exception as e:
        print(f"\n❌ Error resetting database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    clean_database()
