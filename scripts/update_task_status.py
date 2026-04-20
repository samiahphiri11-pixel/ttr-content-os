import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("data/content.db")

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/update_task_status.py <task_id> <status>")
        print("Example: python3 scripts/update_task_status.py 3 done")
        return

    task_id = sys.argv[1]
    new_status = sys.argv[2]

    allowed_statuses = {"todo", "done", "in_progress"}

    if new_status not in allowed_statuses:
        print(f"Invalid status: {new_status}")
        print("Allowed statuses: todo, in_progress, done")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        UPDATE tasks
        SET status = ?
        WHERE id = ?
    """, (new_status, task_id))

    conn.commit()

    if cur.rowcount == 0:
        print(f"No task found with ID {task_id}")
    else:
        print(f"Task {task_id} updated to '{new_status}'")

    conn.close()

if __name__ == "__main__":
    main()