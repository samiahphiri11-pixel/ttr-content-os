import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("data/content.db")
EXPORTS_DIR = Path("exports")

def get_agent_workflow(post_format: str) -> list[str]:
    if post_format == "video":
        return ["Strategist", "Video Director", "Caption Writer", "Story Manager", "Repurposer"]
    elif post_format == "graphic":
        return ["Strategist", "Graphic Designer", "Caption Writer", "Story Manager"]
    elif post_format == "mix":
        return ["Strategist", "Graphic Designer", "Video Director", "Caption Writer", "Story Manager", "Repurposer"]
    return ["Strategist", "Caption Writer"]

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/generate_post_brief.py <post_id>")
        return

    post_id = sys.argv[1]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, day_of_week, title, pillar, format, goal, source_folder, status
        FROM posts
        WHERE id = ?
    """, (post_id,))
    post = cur.fetchone()

    if not post:
        print(f"No post found with ID {post_id}")
        conn.close()
        return

    _, day, title, pillar, post_format, goal, source_folder, status = post
    workflow = get_agent_workflow(post_format)

    lines = []
    lines.append("POST BRIEF")
    lines.append("=" * 60)
    lines.append(f"Post ID: {post_id}")
    lines.append(f"Day: {day}")
    lines.append(f"Title: {title}")
    lines.append(f"Pillar: {pillar}")
    lines.append(f"Format: {post_format}")
    lines.append(f"Goal: {goal}")
    lines.append(f"Source Folder: {source_folder}")
    lines.append(f"Status: {status}")
    lines.append("")
    lines.append("RECOMMENDED AI WORKFLOW")
    lines.append("-" * 60)

    for step_num, agent in enumerate(workflow, start=1):
        lines.append(f"{step_num}. {agent}")

    lines.append("")
    lines.append("CLAUDE HANDOFF PROMPT")
    lines.append("-" * 60)
    lines.append("You are working on a TT&R Elite content post.")
    lines.append("")
    lines.append("Post details:")
    lines.append(f"- Day: {day}")
    lines.append(f"- Title: {title}")
    lines.append(f"- Pillar: {pillar}")
    lines.append(f"- Format: {post_format}")
    lines.append(f"- Goal: {goal}")
    lines.append(f"- Source folder: {source_folder}")
    lines.append("")
    lines.append("Your job is to help create this post in a practical, execution-ready way.")
    lines.append("Respond based on the agent needed for this stage of the workflow.")
    lines.append("Keep everything specific, concise, and optimized for TT&R Elite social media.")

    output = "\n".join(lines)

    print("\n" + output)

    EXPORTS_DIR.mkdir(exist_ok=True)
    output_path = EXPORTS_DIR / f"post_{post_id}_brief.txt"
    output_path.write_text(output, encoding="utf-8")

    print(f"\nSaved brief to: {output_path}")

    conn.close()

if __name__ == "__main__":
    main()