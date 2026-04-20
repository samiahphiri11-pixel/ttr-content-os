import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("\nAGENT OUTPUTS")
    print("=" * 90)

    cur.execute("""
        SELECT
            agent_outputs.id,
            agent_outputs.post_id,
            posts.day_of_week,
            posts.title,
            agent_outputs.agent_name,
            agent_outputs.role,
            agent_outputs.output_type,
            agent_outputs.content,
            agent_outputs.updated_at
        FROM agent_outputs
        LEFT JOIN posts ON agent_outputs.post_id = posts.id
        ORDER BY agent_outputs.post_id, agent_outputs.agent_name
    """)
    rows = cur.fetchall()

    if not rows:
        print("No agent outputs found.")
        conn.close()
        return

    for row in rows:
        output_id, post_id, day, title, agent_name, role, output_type, content, updated_at = row

        print(f"\n[Output {output_id}] Post {post_id} - {day} - {title}")
        print("-" * 90)
        print(f"Agent: {agent_name}")
        print(f"Role: {role}")
        print(f"Type: {output_type}")
        print(f"Content: {content}")
        print(f"Updated At: {updated_at}")

    conn.close()


if __name__ == "__main__":
    main()