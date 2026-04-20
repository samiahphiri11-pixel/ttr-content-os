import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("\nSCHEDULED POSTS")
    print("=" * 80)

    cur.execute("""
        SELECT id, scheduled_date, day_of_week, title, format, status
        FROM posts
        ORDER BY scheduled_date, id
    """)
    rows = cur.fetchall()

    if not rows:
        print("No posts found.")
        conn.close()
        return

    for post_id, scheduled_date, day_of_week, title, post_format, status in rows:
        print(f"\n[Post {post_id}]")
        print("-" * 80)
        print(f"Date: {scheduled_date}")
        print(f"Day: {day_of_week}")
        print(f"Title: {title}")
        print(f"Format: {post_format}")
        print(f"Status: {status}")

    conn.close()


if __name__ == "__main__":
    main()