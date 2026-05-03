import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_name TEXT,
            campaign_goal TEXT,
            campaign_start_date TEXT,
            campaign_end_date TEXT,
            campaign_priority TEXT,
            campaign_cta TEXT,
            campaign_notes TEXT,
            campaign_active INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

    print("Campaign Mode table created successfully.")


if __name__ == "__main__":
    main()