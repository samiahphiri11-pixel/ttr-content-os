import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("data/content.db")

ALLOWED_TYPES = {"ig", "tiktok", "hashtags"}


def main():
    if len(sys.argv) != 4:
        print('Usage: python3 scripts/save_caption.py <post_id> <type> "<text>"')
        print('Example: python3 scripts/save_caption.py 51 ig "Train with purpose. Every rep matters."')
        print("Allowed types: ig, tiktok, hashtags")
        return

    post_id = sys.argv[1]
    caption_type = sys.argv[2].lower()
    text = sys.argv[3]

    if caption_type not in ALLOWED_TYPES:
        print(f"Invalid type: {caption_type}")
        print("Allowed types: ig, tiktok, hashtags")
        return

    column_map = {
        "ig": "caption_ig",
        "tiktok": "caption_tiktok",
        "hashtags": "hashtags"
    }

    column_name = column_map[caption_type]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id, title FROM posts WHERE id = ?", (post_id,))
    post = cur.fetchone()

    if not post:
        print(f"No post found with ID {post_id}")
        conn.close()
        return

    query = f"UPDATE posts SET {column_name} = ? WHERE id = ?"
    cur.execute(query, (text, post_id))

    conn.commit()

    if cur.rowcount == 0:
        print(f"Nothing was updated for post {post_id}.")
    else:
        print(f"Saved {caption_type} text for post {post_id}.")

    conn.close()


if __name__ == "__main__":
    main()