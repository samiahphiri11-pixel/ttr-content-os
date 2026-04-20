import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")

EXPECTED_STATUSES = [
    "idea",
    "planned",
    "editing",
    "caption_ready",
    "scheduled",
    "posted"
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT status, COUNT(*)
        FROM posts
        GROUP BY status
    """)
    rows = cur.fetchall()

    counts = {status: 0 for status in EXPECTED_STATUSES}

    for status, count in rows:
        counts[status] = count

    total_posts = sum(counts.values())

    print("\nPOST PROGRESS SUMMARY")
    print("=" * 60)
    print(f"Total Posts: {total_posts}")
    print("")

    for status in EXPECTED_STATUSES:
        print(f"{status}: {counts[status]}")

    conn.close()


if __name__ == "__main__":
    main()