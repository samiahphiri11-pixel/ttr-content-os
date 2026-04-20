import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

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

    print("\nTT&R ELITE WEEKLY BRIEFS")
    print("=" * 80)

    for post_id, day, title, pillar, post_format, goal, source_folder, status in posts:
        print(f"\n[{post_id}] {day}")
        print("-" * 80)
        print(f"Title: {title}")
        print(f"Pillar: {pillar}")
        print(f"Format: {post_format}")
        print(f"Goal: {goal}")
        print(f"Source Folder: {source_folder}")
        print(f"Status: {status}")

        print("\nBrief:")
        print(f"- Create a {post_format} post for TT&R Elite")
        print(f"- Use the source folder: {source_folder}")
        print(f"- The content pillar is {pillar}")
        print(f"- The main goal is {goal}")
        print("- Make it practical, engaging, and aligned with the TT&R Elite brand")
        print("- Build supporting stories and a caption for this post")

    conn.close()

if __name__ == "__main__":
    main()