import json
import os
import sqlite3
from pathlib import Path

import anthropic
from dotenv import load_dotenv

DB_PATH = Path("data/content.db")

AGENT_MAP = {
    "Messi": "Strategist",
    "Ronaldo": "Video Director",
    "Neymar": "Graphic Designer",
    "Xavi": "Caption Writer",
    "Mbappé": "Story Manager",
    "Modrić": "Repurposer",
    "De Bruyne": "Analytics",
}

PERSONALITY = {
    "Strategist": "You think like Messi. You see the whole field, anticipate what works, and make smart, simple decisions that unlock everything.",
    "Video Director": "You think like Ronaldo. Precision, execution, elite performance. Every clip is intentional and powerful.",
    "Graphic Designer": "You think like Neymar. Creative, expressive, visually engaging, but still effective and clean.",
    "Caption Writer": "You think like Xavi. Intelligent, composed, and purposeful. Every word has meaning and flow.",
    "Story Manager": "You think like Mbappé. Fast, energetic, engaging, and attention-grabbing.",
    "Repurposer": "You think like Modrić. Control, balance, and flow. You maximize everything and connect ideas smoothly.",
    "Analytics": "You think like De Bruyne. Precision, awareness, and understanding what actually produces results.",
}


def get_connection():
    return sqlite3.connect(DB_PATH)


def get_agents_for_format(post_format: str) -> list[str]:
    if post_format == "video":
        return ["Messi", "Ronaldo", "Xavi", "Mbappé", "Modrić", "De Bruyne"]
    elif post_format == "graphic":
        return ["Messi", "Neymar", "Xavi", "Mbappé", "De Bruyne"]
    elif post_format == "mix":
        return ["Messi", "Ronaldo", "Neymar", "Xavi", "Mbappé", "Modrić", "De Bruyne"]
    return ["Messi", "Xavi", "De Bruyne"]


def build_agent_prompt(agent_name: str, post: tuple) -> tuple[str, str]:
    role = AGENT_MAP[agent_name]
    identity = PERSONALITY.get(role, "")

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

    base_info = f"""
You are helping create a TT&R Elite social media post.

Post details:
- Post ID: {post_id}
- Day: {day}
- Title: {title}
- Pillar: {pillar}
- Format: {post_format}
- Goal: {goal}
- Source folder: {source_folder}
- Status: {status}

Brand context:
TT&R Elite is a soccer training brand focused on player development, skills, mindset, and elite performance.
The content should be practical, modern, engaging, and optimized for growth, engagement, and conversion.
""".strip()

    if role == "Strategist":
        prompt = f"""{base_info}

{identity}

Your role: Strategist

Return ONLY valid JSON. No markdown. No explanation.

{{
  "best_angle": "...",
  "why_it_works": "...",
  "ideal_audience": "...",
  "cta": "...",
  "alternate_angle": "..."
}}
"""
        return role, prompt

    elif role == "Video Director":
        prompt = f"""{base_info}

{identity}

Your role: Video Director

Return ONLY valid JSON. No markdown. No explanation.

{{
  "hook_text": "...",
  "shot_by_shot_structure": "...",
  "clip_order": "...",
  "on_screen_text": "...",
  "editing_style": "...",
  "ending_cta": "...",
  "alternate_version": "..."
}}
"""
        return role, prompt

    elif role == "Graphic Designer":
        prompt = f"""{base_info}

{identity}

Your role: Graphic Designer

Return ONLY valid JSON. No markdown. No explanation.

{{
  "graphic_purpose": "...",
  "main_headline": "...",
  "supporting_text": "...",
  "layout_structure": "...",
  "style_direction": "...",
  "font_feel": "...",
  "visual_elements": "...",
  "cta_placement": "..."
}}
"""
        return role, prompt

    elif role == "Caption Writer":
        prompt = f"""{base_info}

{identity}

Your role: Caption Writer

Return ONLY valid JSON. No markdown. No explanation.

{{
  "instagram_caption": "...",
  "tiktok_caption": "...",
  "hashtags": "..."
}}
"""
        return role, prompt

    elif role == "Story Manager":
        prompt = f"""{base_info}

{identity}

Your role: Story Manager

Return ONLY valid JSON. No markdown. No explanation.

{{
  "story_sequence": "..."
}}
"""
        return role, prompt

    elif role == "Repurposer":
        prompt = f"""{base_info}

{identity}

Your role: Repurposer

Return ONLY valid JSON. No markdown. No explanation.

{{
  "repurpose_ideas": "..."
}}
"""
        return role, prompt

    elif role == "Analytics":
        prompt = f"""{base_info}

{identity}

Your role: Analytics

Return ONLY valid JSON. No markdown. No explanation.

{{
  "performance_read": "...",
  "main_metric_to_watch": "...",
  "best_platform_goal": "...",
  "improvement_idea": "...",
  "ab_test_idea": "..."
}}
"""
        return role, prompt

    return role, base_info


def call_claude(client: anthropic.Anthropic, model: str, prompt: str) -> str:
    response = client.messages.create(
        model=model,
        max_tokens=1000,
        system="You are an elite content operations assistant for TT&R Elite. Follow formatting instructions exactly.",
        messages=[{"role": "user", "content": prompt}],
    )

    parts = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "\n".join(parts).strip()


def parse_json_response(text: str) -> dict:
    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "", 1).strip()
    if text.startswith("```"):
        text = text.replace("```", "", 1).strip()
    if text.endswith("```"):
        text = text[:-3].strip()

    return json.loads(text)


def save_caption_outputs(cur, post_id: int, data: dict):
    instagram_caption = data.get("instagram_caption", "").strip()
    tiktok_caption = data.get("tiktok_caption", "").strip()
    hashtags = data.get("hashtags", "").strip()

    cur.execute("""
        UPDATE posts
        SET caption_ig = ?, caption_tiktok = ?, hashtags = ?
        WHERE id = ?
    """, (instagram_caption, tiktok_caption, hashtags, post_id))


def save_agent_output(cur, post_id: int, agent_name: str, role: str, output_type: str, content: str):
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
    else:
        cur.execute("""
            INSERT INTO agent_outputs (post_id, agent_name, role, output_type, content)
            VALUES (?, ?, ?, ?, ?)
        """, (post_id, agent_name, role, output_type, content))


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

    post_id = 94

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

    _, day, title, _, post_format, _, _, _ = post
    agents = get_agents_for_format(post_format)

    print(f"Testing one post: {post_id} - {day} - {title}")
    print(f"Agents: {', '.join(agents)}")

    for agent_name in agents:
        role, prompt = build_agent_prompt(agent_name, post)
        print(f"\n--- Running {agent_name} ({role}) ---")

        try:
            raw_text = call_claude(client, model, prompt)
            print("RAW RESPONSE:")
            print(raw_text[:500])

            data = parse_json_response(raw_text)

            if role == "Caption Writer":
                save_caption_outputs(cur, post_id, data)
                save_agent_output(cur, post_id, agent_name, role, "caption_package", json.dumps(data, ensure_ascii=False, indent=2))
            elif role == "Strategist":
                save_agent_output(cur, post_id, agent_name, role, "strategy", json.dumps(data, ensure_ascii=False, indent=2))
            elif role == "Video Director":
                save_agent_output(cur, post_id, agent_name, role, "video_plan", json.dumps(data, ensure_ascii=False, indent=2))
            elif role == "Graphic Designer":
                save_agent_output(cur, post_id, agent_name, role, "design_brief", json.dumps(data, ensure_ascii=False, indent=2))
            elif role == "Story Manager":
                save_agent_output(cur, post_id, agent_name, role, "story_sequence", json.dumps(data, ensure_ascii=False, indent=2))
            elif role == "Repurposer":
                save_agent_output(cur, post_id, agent_name, role, "repurpose_ideas", json.dumps(data, ensure_ascii=False, indent=2))
            elif role == "Analytics":
                save_agent_output(cur, post_id, agent_name, role, "analytics_read", json.dumps(data, ensure_ascii=False, indent=2))

            conn.commit()
            print(f"✓ {agent_name} saved")

        except Exception as e:
            print(f"✗ {agent_name} failed")
            print(f"ERROR: {e}")

    conn.close()
    print("\nDone.")
    

if __name__ == "__main__":
    main()