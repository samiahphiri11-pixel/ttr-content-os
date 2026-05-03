import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute("ALTER TABLE content_folders ADD COLUMN last_used_date TEXT")
    except:
        pass

    try:
        cur.execute("ALTER TABLE content_folders ADD COLUMN cooldown_weeks INTEGER DEFAULT 2")
    except:
        pass

    conn.commit()
    conn.close()

    print("Cooldown fields added.")


if __name__ == "__main__":
    main()