import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("\nWEEKLY TASKS")
    print("=" * 60)

    cur.execute("""
        SELECT tasks.id, posts.day_of_week, posts.title, tasks.task_type, tasks.status, tasks.notes
        FROM tasks
        LEFT JOIN posts ON tasks.post_id = posts.id
        ORDER BY posts.id, tasks.id
    """)
    rows = cur.fetchall()

    if not rows:
        print("No tasks found.")
    else:
        current_post = None

        for task_id, day, title, task_type, status, notes in rows:
            post_label = f"{day} - {title}"

            if post_label != current_post:
                current_post = post_label
                print(f"\n{post_label}")
                print("-" * 60)

            print(f"[{task_id}] {task_type} | status: {status}")

    conn.close()

if __name__ == "__main__":
    main()