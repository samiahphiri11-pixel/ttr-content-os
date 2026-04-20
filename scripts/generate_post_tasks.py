import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")

def get_tasks_for_format(post_format: str) -> list[str]:
    if post_format == "video":
        return [
            "edit video",
            "write caption",
            "make stories",
            "schedule in buffer"
        ]
    elif post_format == "graphic":
        return [
            "create graphic",
            "write caption",
            "make stories",
            "schedule in buffer"
        ]
    elif post_format == "mix":
        return [
            "create content",
            "write caption",
            "make stories",
            "schedule in buffer"
        ]
    else:
        return [
            "create content",
            "write caption",
            "schedule in buffer"
        ]

def main():
    print("Generating post tasks...")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Clear old tasks so you don’t duplicate them every run
    cur.execute("DELETE FROM tasks")

    cur.execute("""
        SELECT id, day_of_week, title, format
        FROM posts
        ORDER BY id
    """)
    posts = cur.fetchall()

    if not posts:
        print("No posts found. Generate a weekly plan first.")
        conn.close()
        return

    for post_id, day_of_week, title, post_format in posts:
        task_list = get_tasks_for_format(post_format)

        for task in task_list:
            notes = f"{day_of_week}: {title}"

            cur.execute("""
                INSERT INTO tasks (post_id, task_type, status, notes)
                VALUES (?, ?, ?, ?)
            """, (
                post_id,
                task,
                "todo",
                notes
            ))

        print(f"Tasks created for {day_of_week} - {title}")

    conn.commit()
    conn.close()

    print("All post tasks generated.")

if __name__ == "__main__":
    main()