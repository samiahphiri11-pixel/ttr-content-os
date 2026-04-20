import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("\nWEEKLY CONTENT PLAN")
    print("=" * 60)

    cur.execute("""
        SELECT day_of_week, title, pillar, format, goal, source_folder, status
        FROM posts
        ORDER BY id
    """)
    posts = cur.fetchall()

    if not posts:
        print("No weekly plan found.")
    else:
        for day, title, pillar, post_format, goal, source_folder, status in posts:
            print(f"\n{day}")
            print("-" * 60)
            print(f"Title: {title}")
            print(f"Pillar: {pillar}")
            print(f"Format: {post_format}")
            print(f"Goal: {goal}")
            print(f"Source Folder: {source_folder}")
            print(f"Status: {status}")

    conn.close()

if __name__ == "__main__":
    main()