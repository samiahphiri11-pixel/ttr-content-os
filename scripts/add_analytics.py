import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("data/content.db")


def main():
    if len(sys.argv) < 9:
        print("Usage:")
        print("python3 scripts/add_analytics.py <post_id> <platform> <views> <likes> <comments> <shares> <saves> <follows_gained> [link_clicks] [notes]")
        print("")
        print("Example:")
        print('python3 scripts/add_analytics.py 1 instagram 1200 85 6 14 22 5 0 "Strong hook, good saves"')
        return

    post_id = sys.argv[1]
    platform = sys.argv[2]
    views = int(sys.argv[3])
    likes = int(sys.argv[4])
    comments = int(sys.argv[5])
    shares = int(sys.argv[6])
    saves = int(sys.argv[7])
    follows_gained = int(sys.argv[8])

    link_clicks = int(sys.argv[9]) if len(sys.argv) > 9 else 0
    notes = sys.argv[10] if len(sys.argv) > 10 else ""

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id, title FROM posts WHERE id = ?", (post_id,))
    post = cur.fetchone()

    if not post:
        print(f"No post found with ID {post_id}")
        conn.close()
        return

    cur.execute("""
        INSERT INTO analytics (
            post_id,
            platform,
            views,
            likes,
            comments,
            shares,
            saves,
            follows_gained,
            link_clicks,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        post_id,
        platform,
        views,
        likes,
        comments,
        shares,
        saves,
        follows_gained,
        link_clicks,
        notes
    ))

    conn.commit()
    conn.close()

    print(f"Analytics added for post {post_id} on {platform}.")


if __name__ == "__main__":
    main()