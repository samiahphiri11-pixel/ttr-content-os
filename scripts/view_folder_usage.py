import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("\nFOLDER USAGE HISTORY")
    print("=" * 80)

    cur.execute("""
        SELECT id, folder_name, post_id, day_of_week, used_at
        FROM folder_usage
        ORDER BY used_at DESC, id DESC
    """)
    rows = cur.fetchall()

    if not rows:
        print("No folder usage history found.")
    else:
        for usage_id, folder_name, post_id, day_of_week, used_at in rows:
            print(f"\nUsage ID: {usage_id}")
            print("-" * 80)
            print(f"Folder: {folder_name}")
            print(f"Post ID: {post_id}")
            print(f"Day: {day_of_week}")
            print(f"Used At: {used_at}")

    conn.close()


if __name__ == "__main__":
    main()