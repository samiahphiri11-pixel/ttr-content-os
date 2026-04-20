import os
import sqlite3
from pathlib import Path

import anthropic
from dotenv import load_dotenv

DB_PATH = Path("data/content.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def build_prompt(post: tuple) -> str:
    (
        post_id,
        day,
        title,
        pillar,
        post_format,
        goal,
        source_folder,
        status,
    ) = post

    return f"""
You are an elite content team for TT&R Elite.

Create content outputs for this post.

Post:
- Day: {day}
- Title: {title}
- Pillar: {pillar}
- Format: {post_format}
- Goal: {goal}
- Source folder: {source_folder}
- Status: {status}

IMPORTANT:
Return your response using ONLY these exact section tags.
Do not use JSON.
Do not use markdown code fences.

[[STRATEGY]]
Best angle:
Why it works:
CTA:

[[VIDEO]]
Hook:
Structure:

[[DESIGN]]
Headline:
Style:

[[INSTAGRAM]]
Write the Instagram caption here.

[[TIKTOK]]
Write the TikTok caption here.

[[HASHTAGS]]
Write 10 hashtags here on one line.

[[STORY]]
Write the story sequence here.

[[REPURPOSE]]
Write repurpose ideas here.

[[INSIGHT]]
Write analytics insight here.
"""


def call_claude(client, model, prompt):
    response = client.messages.create(
        model=model,
        max_tokens=900,
        system="You are an elite content system. Follow section formatting exactly.",
        messages=[{"role": "user", "content": prompt}],
    )

    parts = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)

    return "\n".join(parts).strip()


def extract_section(text: str, tag: str) -> str:
    start_marker = f"[[{tag}]]"
    start_idx = text.find(start_marker)

    if start_idx == -1:
        return ""

    start_idx += len(start_marker)

    next_idx = len(text)
    for possible_tag in [
        "STRATEGY",
        "VIDEO",
        "DESIGN",
        "INSTAGRAM",
        "TIKTOK",
        "HASHTAGS",
        "STORY",
        "REPURPOSE",
        "INSIGHT",
    ]:
        marker = f"[[{possible_tag}]]"
        idx = text.find(marker, start_idx)
        if idx != -1 and idx < next_idx:
            next_idx = idx

    return text[start_idx:next_idx].strip()


def upsert_agent_output(cur, post_id, agent_name, output_type, content):
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
        """, (agent_name, content, post_id, agent_name, output_type))
    else:
        cur.execute("""
            INSERT INTO agent_outputs (post_id, agent_name, role, output_type, content)
            VALUES (?, ?, ?, ?, ?)
        """, (post_id, agent_name, agent_name, output_type, content))


def save_all(cur, post_id, raw_text):
    strategy = extract_section(raw_text, "STRATEGY")
    video = extract_section(raw_text, "VIDEO")
    design = extract_section(raw_text, "DESIGN")
    instagram = extract_section(raw_text, "INSTAGRAM")
    tiktok = extract_section(raw_text, "TIKTOK")
    hashtags = extract_section(raw_text, "HASHTAGS")
    story = extract_section(raw_text, "STORY")
    repurpose = extract_section(raw_text, "REPURPOSE")
    insight = extract_section(raw_text, "INSIGHT")

    cur.execute("""
        UPDATE posts
        SET caption_ig = ?, caption_tiktok = ?, hashtags = ?
        WHERE id = ?
    """, (
        instagram,
        tiktok,
        hashtags,
        post_id
    ))

    upsert_agent_output(cur, post_id, "Messi", "strategy", strategy)
    upsert_agent_output(cur, post_id, "Ronaldo", "video_plan", video)
    upsert_agent_output(cur, post_id, "Neymar", "design_brief", design)
    upsert_agent_output(cur, post_id, "Xavi", "caption_package", f"Instagram:\n{instagram}\n\nTikTok:\n{tiktok}\n\nHashtags:\n{hashtags}")
    upsert_agent_output(cur, post_id, "Mbappé", "story_sequence", story)
    upsert_agent_output(cur, post_id, "Modrić", "repurpose", repurpose)
    upsert_agent_output(cur, post_id, "De Bruyne", "analytics", insight)


def main():
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")

    if not api_key:
        print("Missing ANTHROPIC_API_KEY in .env")
        return

    client = anthropic.Anthropic(api_key=api_key, timeout=60.0)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            day_of_week,
            title,
            pillar,
            format,
            goal,
            source_folder,
            status
        FROM posts
        ORDER BY id
    """)
    posts = cur.fetchall()

    print("Starting fast auto-generation...\n")

    for i, post in enumerate(posts, start=1):
        post_id = post[0]

        print(f"[{i}/{len(posts)}] Processing Post {post_id}...")

        cur.execute("SELECT caption_ig FROM posts WHERE id = ?", (post_id,))
        existing = cur.fetchone()[0]

        if existing and str(existing).strip():
            print("⏭️ Skipped (already generated)\n")
            continue

        try:
            print("⚡ Sending to Claude...")
            prompt = build_prompt(post)

            response = call_claude(client, model, prompt)

            print("💾 Saving outputs...")
            save_all(cur, post_id, response)
            conn.commit()

            print("✅ Done\n")

        except Exception as e:
            print("❌ Failed:", e, "\n")

    conn.close()
    print("All posts complete.")


if __name__ == "__main__":
    main()