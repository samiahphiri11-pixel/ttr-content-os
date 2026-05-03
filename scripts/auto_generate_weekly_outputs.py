import os
import sqlite3
from pathlib import Path

import anthropic
from dotenv import load_dotenv

DB_PATH = Path("data/content.db")


def get_connection():
    return sqlite3.connect(DB_PATH)

def load_active_campaign():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            campaign_name,
            campaign_goal,
            campaign_start_date,
            campaign_end_date,
            campaign_priority,
            campaign_cta,
            campaign_notes
        FROM campaigns
        WHERE campaign_active = 1
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cur.fetchone()
    conn.close()

    return row


def build_prompt(post: tuple, campaign=None) -> str:
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

    campaign_text = ""

    if campaign:
        (
            campaign_name,
            campaign_goal,
            campaign_start,
            campaign_end,
            campaign_priority,
            campaign_cta,
            campaign_notes
        ) = campaign

        campaign_text = f"""

ACTIVE CAMPAIGN:
- Name: {campaign_name}
- Goal: {campaign_goal}
- Dates: {campaign_start} to {campaign_end}
- Priority: {campaign_priority}
- CTA: {campaign_cta}
- Notes: {campaign_notes}

INSTRUCTIONS:
- Naturally incorporate this campaign where relevant
- Do NOT force it into every post
- Add CTA only when it makes sense
- If the post is community or training, lightly connect to the campaign
- Generate 2–3 supporting story ideas related to the campaign
"""

    return f"""
You are an elite content team for TT&R Elite.

{campaign_text}

Create a fresh weekly concept and a better final title than the current working title.

Your job is to create a FRESH weekly content concept for this post.
Do NOT recycle common generic ideas from previous weeks unless the source material clearly calls for it.
Avoid repeating phrases like "every rep counts" unless the source folder strongly suggests that exact theme.

Brand:
TT&R Elite is a soccer performance brand focused on elite player development, mindset, discipline, training quality, confidence, and real growth.

Post info:
- Post ID: {post_id}
- Day: {day}
- Working title: {title}
- Pillar: {pillar}
- Format: {post_format}
- Goal: {goal}
- Source folder: {source_folder}
- Status: {status}

Freshness rules:
- Make this week's angle feel NEW
- Do not repeat the same concept used last week
- Keep the pillar the same, but change the angle, hook, and framing
- Use the source folder as inspiration, not as the final repeated concept
- Make it specific, modern, athletic, and useful for TT&R Elite

IMPORTANT:
Return your response using ONLY these exact section tags.
Do not use JSON.
Do not use markdown code fences.

[[TITLE]]
Write one strong, fresh content title for this post.
Keep it short, specific, and social-media friendly.
Do not just repeat the pillar name.

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
        "TITLE",
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
    title = extract_section(raw_text, "TITLE")
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
        SELECT pillar
        FROM posts
        WHERE id = ?
    """, (post_id,))
    pillar_row = cur.fetchone()
    pillar = pillar_row[0] if pillar_row else ""

    if pillar in {"mindset", "wellness"} and title:
        cur.execute("""
            UPDATE posts
            SET title = ?, caption_ig = ?, caption_tiktok = ?, hashtags = ?
            WHERE id = ?
        """, (
            title,
            instagram,
            tiktok,
            hashtags,
            post_id
        ))
    else:
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
    
    cur.execute("DELETE FROM agent_outputs")
    cur.execute("UPDATE posts SET caption_ig = NULL, caption_tiktok = NULL, hashtags = NULL")
    conn.commit()

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

    campaign = load_active_campaign()

    print("Starting fast auto-generation...\n")

    for i, post in enumerate(posts, start=1):
        post_id = post[0]

        print(f"[{i}/{len(posts)}] Processing Post {post_id}...")

        try:
            print("⚡ Sending to Claude...")
            prompt = build_prompt(post, campaign)

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