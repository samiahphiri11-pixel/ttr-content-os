import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS monthly_strategy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month_name TEXT,
            monthly_theme TEXT,
            main_goal TEXT,
            secondary_goal TEXT,
            priority_pillars TEXT,
            campaign_focus TEXT,
            strategy_notes TEXT,
            strategy_active INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

    print("Monthly strategy table created successfully.")


if __name__ == "__main__":
    main()