import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")
EXPORTS_DIR = Path("exports")
PROMPTS_DIR = EXPORTS_DIR / "weekly_prompts"
DASHBOARD_PATH = EXPORTS_DIR / "weekly_dashboard.txt"


def get_task_counts(cur):
    cur.execute("""
        SELECT status, COUNT(*)
        FROM tasks
        GROUP BY status
    """)
    rows = cur.fetchall()

    counts = {
        "todo": 0,
        "in_progress": 0,
        "done": 0
    }

    for status, count in rows:
        counts[status] = count

    return counts


def get_prompt_files_for_post(post_id: int) -> list[str]:
    if not PROMPTS_DIR.exists():
        return []

    matching_files = []
    prefix = f"post_{post_id}_"

    for file_path in PROMPTS_DIR.iterdir():
        if file_path.is_file() and file_path.name.startswith(prefix):
            matching_files.append(file_path.name)

    return sorted(matching_files)


def main():
    EXPORTS_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, day_of_week, title, pillar, format, goal, source_folder, status
        FROM posts
        ORDER BY id
    """)
    posts = cur.fetchall()

    task_counts = get_task_counts(cur)

    lines = []
    lines.append("TT&R ELITE WEEKLY DASHBOARD")
    lines.append("=" * 80)
    lines.append("")

    total_tasks = task_counts["todo"] + task_counts["in_progress"] + task_counts["done"]

    lines.append("OVERVIEW")
    lines.append("-" * 80)
    lines.append(f"Total Posts: {len(posts)}")
    lines.append(f"Total Tasks: {total_tasks}")
    lines.append(f"Todo Tasks: {task_counts['todo']}")
    lines.append(f"In Progress Tasks: {task_counts['in_progress']}")
    lines.append(f"Done Tasks: {task_counts['done']}")
    lines.append("")

    if total_tasks > 0:
        completion_rate = round((task_counts["done"] / total_tasks) * 100, 1)
        lines.append(f"Completion Rate: {completion_rate}%")
    else:
        lines.append("Completion Rate: 0%")

    lines.append("")
    lines.append("WEEKLY POSTS")
    lines.append("=" * 80)

    if not posts:
        lines.append("No posts found.")
    else:
        for post in posts:
            post_id, day, title, pillar, post_format, goal, source_folder, status = post

            lines.append("")
            lines.append(f"[Post {post_id}] {day}")
            lines.append("-" * 80)
            lines.append(f"Title: {title}")
            lines.append(f"Pillar: {pillar}")
            lines.append(f"Format: {post_format}")
            lines.append(f"Goal: {goal}")
            lines.append(f"Source Folder: {source_folder}")
            lines.append(f"Post Status: {status}")
            lines.append("")

            cur.execute("""
                SELECT id, task_type, status
                FROM tasks
                WHERE post_id = ?
                ORDER BY id
            """, (post_id,))
            tasks = cur.fetchall()

            lines.append("Tasks:")
            if not tasks:
                lines.append("- No tasks found")
            else:
                for task_id, task_type, task_status in tasks:
                    lines.append(f"- [{task_id}] {task_type} | {task_status}")

            lines.append("")
            prompt_files = get_prompt_files_for_post(post_id)
            lines.append("Prompt Files:")
            if not prompt_files:
                lines.append("- No prompt files found")
            else:
                for file_name in prompt_files:
                    lines.append(f"- {file_name}")

    lines.append("")
    lines.append("=" * 80)
    lines.append("NEXT ACTIONS")
    lines.append("-" * 80)

    cur.execute("""
        SELECT tasks.id, posts.day_of_week, posts.title, tasks.task_type
        FROM tasks
        LEFT JOIN posts ON tasks.post_id = posts.id
        WHERE tasks.status = 'todo'
        ORDER BY tasks.id
        LIMIT 10
    """)
    todo_tasks = cur.fetchall()

    if not todo_tasks:
        lines.append("No remaining todo tasks. Great job.")
    else:
        for task_id, day, title, task_type in todo_tasks:
            lines.append(f"- Task {task_id}: {task_type} for {day} - {title}")

    output = "\n".join(lines)
    DASHBOARD_PATH.write_text(output, encoding="utf-8")

    print(output)
    print(f"\nSaved dashboard to: {DASHBOARD_PATH}")

    conn.close()


if __name__ == "__main__":
    main()