import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("data/content.db")

AGENT_MAP = {
    "Messi": "Strategist",
    "Ronaldo": "Video Director",
    "Neymar": "Graphic Designer",
    "Xavi": "Caption Writer",
    "Mbappé": "Story Manager",
    "Modrić": "Repurposer",
    "De Bruyne": "Analytics"
}


def main():
    if len(sys.argv) != 5:
        print('Usage: python3 scripts/save_agent_output.py <post_id> "<agent_name>" <output_type> "<content>"')
        print('Example: python3 scripts/save_agent_output.py 51 "Ronaldo" video_plan "Hook: ... Clip order: ..."')
        return

    post_id = sys.argv[1]
    agent_name = sys.argv[2]
    output_type = sys.argv[3]
    content = sys.argv[4]

    if agent_name not in AGENT_MAP:
        print(f"Invalid agent name: {agent_name}")
        print("Valid agents:")
        for name in AGENT_MAP:
            print(f"- {name}")
        return

    role = AGENT_MAP[agent_name]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id, title FROM posts WHERE id = ?", (post_id,))
    post = cur.fetchone()

    if not post:
        print(f"No post found with ID {post_id}")
        conn.close()
        return

    cur.execute("""
        SELECT id
        FROM agent_outputs
        WHERE post_id = ? AND agent_name = ? AND output_type = ?
    """, (post_id, agent_name, output_type))
    existing = cur.fetchone()

    if existing:
        cur.execute("""
            UPDATE agent_outputs
            SET role = ?, content = ?, updated_at = CURRENT_TIMESTAMP
            WHERE post_id = ? AND agent_name = ? AND output_type = ?
        """, (role, content, post_id, agent_name, output_type))
        print(f'Updated {agent_name} output for post {post_id}.')
    else:
        cur.execute("""
            INSERT INTO agent_outputs (post_id, agent_name, role, output_type, content)
            VALUES (?, ?, ?, ?, ?)
        """, (post_id, agent_name, role, output_type, content))
        print(f'Saved {agent_name} output for post {post_id}.')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()