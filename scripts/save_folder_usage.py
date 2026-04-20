import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, day_of_week, source_folder
        FROM posts
        WHERE source_folder IS NOT NULL
        ORDER BY id
    """)
    posts = cur.fetchall()

    if not posts:
        print("No posts with source folders found.")
        conn.close()
        return

    inserted_count = 0

    for post_id, day_of_week, source_folder in posts:
        cur.execute("""
            SELECT id
            FROM folder_usage
            WHERE post_id = ?
        """, (post_id,))
        existing = cur.fetchone()

        if existing:
            continue

        cur.execute("""
            INSERT INTO folder_usage (folder_name, post_id, day_of_week)
            VALUES (?, ?, ?)
        """, (source_folder, post_id, day_of_week))

        inserted_count += 1

    conn.commit()
    conn.close()

    print(f"Saved folder usage for {inserted_count} posts.")


if __name__ == "__main__":
    main()