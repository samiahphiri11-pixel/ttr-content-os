import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")


def recommend_status(tasks: list[tuple[str, str]]) -> str:
    if not tasks:
        return "planned"

    statuses = [status for _, status in tasks]

    if all(status == "todo" for status in statuses):
        return "planned"

    if all(status == "done" for status in statuses):
        return "scheduled"

    if any(status == "in_progress" for status in statuses):
        return "editing"

    task_map = {task_type: status for task_type, status in tasks}

    content_creation_tasks = {"edit video", "create graphic", "create content"}
    caption_task = "write caption"

    content_done = any(
        task_map.get(task_name) == "done"
        for task_name in content_creation_tasks
    )

    caption_done = task_map.get(caption_task) == "done"

    remaining_not_done = any(status != "done" for status in statuses)

    if content_done and not caption_done:
        return "editing"

    if caption_done and remaining_not_done:
        return "caption_ready"

    return "editing"


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("\nSYNCING POST STATUSES")
    print("=" * 80)

    cur.execute("""
        SELECT id, day_of_week, title, status
        FROM posts
        ORDER BY id
    """)
    posts = cur.fetchall()

    if not posts:
        print("No posts found.")
        conn.close()
        return

    updated_count = 0

    for post_id, day, title, current_status in posts:
        cur.execute("""
            SELECT task_type, status
            FROM tasks
            WHERE post_id = ?
            ORDER BY id
        """, (post_id,))
        tasks = cur.fetchall()

        recommended = recommend_status(tasks)

        if current_status != recommended:
            cur.execute("""
                UPDATE posts
                SET status = ?
                WHERE id = ?
            """, (recommended, post_id))

            print(f"Updated Post {post_id}: {day} - {title}")
            print(f"  {current_status} -> {recommended}")
            updated_count += 1
        else:
            print(f"No change for Post {post_id}: {day} - {title} ({current_status})")

    conn.commit()
    conn.close()

    print(f"\nDone. Updated {updated_count} posts.")