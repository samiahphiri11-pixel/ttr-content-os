import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("\nPOST STATUS BOARD")
    print("=" * 80)

    cur.execute("""
        SELECT id, day_of_week, title, pillar, format, goal, source_folder, status
        FROM posts
        ORDER BY id
    """)
    posts = cur.fetchall()

    if not posts:
        print("No posts found.")
        conn.close()
        return

    current_status = None

    for post in posts:
        post_id, day, title, pillar, post_format, goal, source_folder, status = post

        if status != current_status:
            current_status = status
            print(f"\nSTATUS: {status.upper()}")
            print("-" * 80)

        print(f"[Post {post_id}] {day} - {title}")
        print(f"  Pillar: {pillar}")
        print(f"  Format: {post_format}")
        print(f"  Goal: {goal}")
        print(f"  Source Folder: {source_folder}")
        print("")

    conn.close()


if __name__ == "__main__":
    main()