import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("data/content.db")
EXPORTS_DIR = Path("exports")

AGENT_MAP = {
    "Messi": "Strategist",
    "Ronaldo": "Video Director",
    "Neymar": "Graphic Designer",
    "Xavi": "Caption Writer",
    "Mbappé": "Story Manager",
    "Modrić": "Repurposer",
    "De Bruyne": "Analytics"
}

PERSONALITY = {
    "Strategist": "You think like Messi. You see the whole field, anticipate what works, and make smart, simple decisions that unlock everything.",
    "Video Director": "You think like Ronaldo. Precision, execution, elite performance. Every clip is intentional and powerful.",
    "Graphic Designer": "You think like Neymar. Creative, expressive, visually engaging, but still effective and clean.",
    "Caption Writer": "You think like Xavi. Intelligent, composed, and purposeful. Every word has meaning and flow.",
    "Story Manager": "You think like Mbappé. Fast, energetic, engaging, and attention-grabbing.",
    "Repurposer": "You think like Modrić. Control, balance, and flow. You maximize everything and connect ideas smoothly.",
    "Analytics": "You think like De Bruyne. Precision, awareness, and understanding what actually produces results."
}

VALID_AGENTS = set(AGENT_MAP.keys())


def build_prompt(role: str, post: tuple) -> str:
    post_id, day, title, pillar, post_format, goal, source_folder, status = post

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

    identity = PERSONALITY.get(role, "")

    if role == "Strategist":
        return f"""{base_info}

{identity}

Your role: Strategist

Create the strategic direction for this post.

Respond with:
1. The best angle for this content
2. Why this post should work
3. The ideal audience for this post
4. A recommended CTA
5. One optional alternate angle

Keep it concise, strategic, and useful.
"""

    elif role == "Video Director":
        return f"""{base_info}

{identity}

Your role: Video Director

Assume the source folder contains the raw clips for this post.
Create a short-form video editing plan.

Respond with:
1. Hook text for the first 1-2 seconds
2. Shot-by-shot structure
3. Clip order suggestion
4. On-screen text ideas
5. Pacing/editing style
6. Ending CTA
7. One alternate version

Be specific and practical so I can actually edit the video from your instructions.
"""

    elif role == "Graphic Designer":
        return f"""{base_info}

{identity}

Your role: Graphic Designer

Create a Canva-ready design brief for this post.

Respond with:
1. Graphic purpose
2. Main headline
3. Supporting text
4. Layout structure
5. Style direction
6. Font feel
7. Visual elements
8. CTA placement

Keep it aligned with TT&R Elite's brand and make it practical to execute in Canva.
"""

    elif role == "Caption Writer":
        return f"""{base_info}

{identity}

Your role: Caption Writer

Write:
1. An Instagram caption
2. A TikTok caption
3. 10 relevant hashtags

Rules:
- Strong hook at the start
- Clear value/message
- End with a CTA
- Keep the brand voice strong and modern
"""

    elif role == "Story Manager":
        return f"""{base_info}

{identity}

Your role: Story Manager

Create a 3-5 frame Instagram story sequence to support this post.

For each frame, include:
1. Exact text
2. Suggested background visual
3. Poll, slider, or Q&A if useful
4. Final CTA

Make it feel engaging and natural.
"""

    elif role == "Repurposer":
        return f"""{base_info}

{identity}

Your role: Repurposer

Turn this post idea into 5 additional content variations.

For each variation, include:
1. Format
2. Angle
3. Hook
4. Why it works
5. Quick execution note

Make the ideas realistic and useful for TT&R Elite content.
"""

    elif role == "Analytics":
        return f"""{base_info}

{identity}

Your role: Analytics

Analyze this post from a performance perspective.

Respond with:
1. Why this content could perform well
2. The main metric to watch
3. The best platform goal (followers, saves, shares, comments, conversion)
4. One improvement to increase performance
5. One A/B test idea for this post

Keep it practical and growth-focused.
"""

    return f"""{base_info}

No valid role found.
"""


def main():
    if len(sys.argv) != 3:
        print('Usage: python3 scripts/agent_prompt_builder.py <post_id> "<agent name>"')
        print('Example: python3 scripts/agent_prompt_builder.py 1 "Xavi"')
        print("\nValid agent names:")
        for agent_name in sorted(VALID_AGENTS):
            print(f"- {agent_name}")
        return

    post_id = sys.argv[1]
    agent_name = sys.argv[2]

    if agent_name not in VALID_AGENTS:
        print(f"Invalid agent: {agent_name}")
        print("\nValid agent names:")
        for valid_agent in sorted(VALID_AGENTS):
            print(f"- {valid_agent}")
        return

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

    role = AGENT_MAP[agent_name]
    prompt = build_prompt(role, post)

    print("\nAGENT PROMPT")
    print("=" * 70)
    print(f"Agent Name: {agent_name}")
    print(f"Agent Role: {role}")
    print("-" * 70)
    print(prompt)

    EXPORTS_DIR.mkdir(exist_ok=True)

    safe_agent_name = (
        agent_name.lower()
        .replace(" ", "_")
        .replace("é", "e")
        .replace("ć", "c")
    )

    output_path = EXPORTS_DIR / f"post_{post_id}_{safe_agent_name}_prompt.txt"
    output_path.write_text(prompt, encoding="utf-8")

    print(f"\nSaved prompt to: {output_path}")

    conn.close()


if __name__ == "__main__":
    main()