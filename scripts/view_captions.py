import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("\nSAVED CAPTIONS")
    print("=" * 80)

    cur.execute("""
        SELECT id, day_of_week, title, caption_ig, caption_tiktok, hashtags
        FROM posts
        ORDER BY id
    """)
    rows = cur.fetchall()

    if not rows:
        print("No posts found.")
        conn.close()
        return

    for row in rows:
        post_id, day, title, caption_ig, caption_tiktok, hashtags = row

        print(f"\n[Post {post_id}] {day} - {title}")
        print("-" * 80)
        print(f"Instagram Caption: {caption_ig if caption_ig else '[none]'}")
        print(f"TikTok Caption: {caption_tiktok if caption_tiktok else '[none]'}")
        print(f"Hashtags: {hashtags if hashtags else '[none]'}")

    conn.close()


if __name__ == "__main__":
    main()