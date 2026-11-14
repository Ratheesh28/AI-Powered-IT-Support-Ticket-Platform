
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "tickets.db"

connection = sqlite3.connect(DB_PATH)

try:
    cursor = connection.cursor()

    # Check the existing table structure
    cursor.execute("PRAGMA table_info(tickets)")
    columns = [column[1] for column in cursor.fetchall()]

    if "priority" not in columns:
        cursor.execute("""
            ALTER TABLE tickets
            ADD COLUMN priority VARCHAR(20)
            NOT NULL DEFAULT 'Medium'
        """)
        print("Priority column added successfully.")
    else:
        print("Priority column already exists.")

    # Verify existing records
    cursor.execute("""
        SELECT id, title, priority
        FROM tickets
        ORDER BY id
    """)

    records = cursor.fetchall()

    connection.commit()

    print("\nDatabase migration completed.")
    print("Existing ticket records:")

    for record in records:
        print(record)

    print(f"\nTotal tickets preserved: {len(records)}")

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()
