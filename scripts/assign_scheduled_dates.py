import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path("data/content.db")

DAY_OFFSETS = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/assign_scheduled_dates.py <start_monday_date>")
        print("Example: python3 scripts/assign_scheduled_dates.py 2026-04-13")
        return

    start_date_str = sys.argv[1]

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, day_of_week, title
        FROM posts
        ORDER BY id
    """)
    posts = cur.fetchall()

    if not posts:
        print("No posts found.")
        conn.close()
        return

    updated_count = 0

    for post_id, day_of_week, title in posts:
        if day_of_week not in DAY_OFFSETS:
            print(f"Skipping Post {post_id}: unknown day_of_week '{day_of_week}'")
            continue

        scheduled_date = start_date + timedelta(days=DAY_OFFSETS[day_of_week])

        cur.execute("""
            UPDATE posts
            SET scheduled_date = ?
            WHERE id = ?
        """, (scheduled_date.isoformat(), post_id))

        print(f"Post {post_id}: {day_of_week} - {title} -> {scheduled_date.isoformat()}")
        updated_count += 1

    conn.commit()
    conn.close()

    print(f"\nAssigned scheduled dates for {updated_count} posts.")

if __name__ == "__main__":
    main()