import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("data/content.db")

ALLOWED_STATUSES = {
    "idea",
    "planned",
    "editing",
    "caption_ready",
    "scheduled",
    "posted"
}


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/update_post_status.py <post_id> <status>")
        print("Example: python3 scripts/update_post_status.py 1 editing")
        print("")
        print("Allowed statuses:")
        for status in sorted(ALLOWED_STATUSES):
            print(f"- {status}")
        return

    post_id = sys.argv[1]
    new_status = sys.argv[2]

    if new_status not in ALLOWED_STATUSES:
        print(f"Invalid status: {new_status}")
        print("Allowed statuses:")
        for status in sorted(ALLOWED_STATUSES):
            print(f"- {status}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        UPDATE posts
        SET status = ?
        WHERE id = ?
    """, (new_status, post_id))

    conn.commit()

    if cur.rowcount == 0:
        print(f"No post found with ID {post_id}")
    else:
        print(f"Post {post_id} updated to '{new_status}'")

    conn.close()


if __name__ == "__main__":
    main()