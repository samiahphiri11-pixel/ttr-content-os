import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("data/content.db")
EXPORTS_DIR = Path("exports")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/export_post_package.py <post_id>")
        print("Example: python3 scripts/export_post_package.py 51")
        return

    post_id = sys.argv[1]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, day_of_week, title, pillar, format, goal, source_folder, status,
               caption_ig, caption_tiktok, hashtags
        FROM posts
        WHERE id = ?
    """, (post_id,))
    post = cur.fetchone()

    if not post:
        print(f"No post found with ID {post_id}")
        conn.close()
        return

    (
        post_id,
        day,
        title,
        pillar,
        post_format,
        goal,
        source_folder,
        status,
        caption_ig,
        caption_tiktok,
        hashtags
    ) = post

    cur.execute("""
        SELECT agent_name, role, output_type, content, updated_at
        FROM agent_outputs
        WHERE post_id = ?
        ORDER BY agent_name
    """, (post_id,))
    outputs = cur.fetchall()

    lines = []
    lines.append("TT&R ELITE POST PACKAGE")
    lines.append("=" * 90)
    lines.append(f"Post ID: {post_id}")
    lines.append(f"Day: {day}")
    lines.append(f"Title: {title}")
    lines.append(f"Pillar: {pillar}")
    lines.append(f"Format: {post_format}")
    lines.append(f"Goal: {goal}")
    lines.append(f"Source Folder: {source_folder}")
    lines.append(f"Status: {status}")
    lines.append("")
    lines.append("CAPTIONS")
    lines.append("-" * 90)
    lines.append(f"Instagram: {caption_ig if caption_ig else '[none]'}")
    lines.append(f"TikTok: {caption_tiktok if caption_tiktok else '[none]'}")
    lines.append(f"Hashtags: {hashtags if hashtags else '[none]'}")
    lines.append("")

    lines.append("AGENT OUTPUTS")
    lines.append("-" * 90)
    if not outputs:
        lines.append("[none]")
    else:
        for agent_name, role, output_type, content, updated_at in outputs:
            lines.append(f"{agent_name} ({role}) - {output_type}")
            lines.append(f"Updated: {updated_at}")
            lines.append(content)
            lines.append("")

    EXPORTS_DIR.mkdir(exist_ok=True)
    output_path = EXPORTS_DIR / f"post_{post_id}_package.txt"
    output_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Exported post package to: {output_path}")

    conn.close()


if __name__ == "__main__":
    main()