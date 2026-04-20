import os
import sqlite3
import subprocess
import sys
from pathlib import Path

DB_PATH = Path("data/content.db")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/auto_generate_single_post.py <post_id>")
        return

    post_id = sys.argv[1]

    if not post_id.isdigit():
        print("post_id must be a number")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id, title FROM posts WHERE id = ?", (post_id,))
    post = cur.fetchone()

    if not post:
        print(f"No post found with ID {post_id}")
        conn.close()
        return

    cur.execute("""
        UPDATE posts
        SET caption_ig = NULL,
            caption_tiktok = NULL,
            hashtags = NULL
        WHERE id = ?
    """, (post_id,))

    cur.execute("DELETE FROM agent_outputs WHERE post_id = ?", (post_id,))
    conn.commit()
    conn.close()

    print(f"Cleared saved outputs for post {post_id}.")
    print("Running weekly AI generator again...")

    result = subprocess.run(
        ["python3", "scripts/auto_generate_weekly_outputs.py"],
        capture_output=True,
        text=True,
    )

    print(result.stdout)
    if result.stderr:
        print("ERRORS:")
        print(result.stderr)

    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()