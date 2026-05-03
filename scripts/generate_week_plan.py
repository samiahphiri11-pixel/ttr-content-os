import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path("data/content.db")

WEEKLY_STRUCTURE = [
    {"day": "Monday", "pillar": "mindset", "format": "graphic", "goal": "engagement"},
    {"day": "Tuesday", "pillar": "skills", "format": "video", "goal": "followers"},
    {"day": "Wednesday", "pillar": "wellness", "format": "graphic", "goal": "saves"},
    {"day": "Thursday", "pillar": "gameplay", "format": "video", "goal": "engagement"},
    {"day": "Friday", "pillar": "viral", "format": "video", "goal": "followers"},
    {"day": "Saturday", "pillar": "real_training", "format": "video", "goal": "conversion"},
    {"day": "Sunday", "pillar": "community", "format": "mix", "goal": "engagement"},
]


def title_from_folder(folder_name: str, day: str, pillar: str) -> str:
    clean_name = folder_name.replace("_", " ").strip()

    lower_clean = clean_name.lower()
    lower_day = day.lower()

    if lower_clean.startswith(lower_day):
        clean_name = clean_name[len(day):].strip()

    if clean_name.startswith("-"):
        clean_name = clean_name[1:].strip()

    return f"{day} — {clean_name}"


def is_ai_led_pillar(pillar: str) -> bool:
    return pillar in {"mindset", "wellness"}


def score_value(value: str) -> int:
    if not value:
        return 0

    value = value.lower()

    if value == "high":
        return 3
    if value == "medium":
        return 2
    if value == "low":
        return 1

    return 0


def is_on_cooldown(last_used_date, cooldown_weeks) -> bool:
    if not last_used_date:
        return False

    if not cooldown_weeks:
        cooldown_weeks = 2

    try:
        last_used = datetime.strptime(last_used_date, "%Y-%m-%d")
    except ValueError:
        return False

    return datetime.now() < last_used + timedelta(weeks=int(cooldown_weeks))


def score_folder_for_post(folder_data: tuple, post_format: str) -> int:
    (
        folder_name,
        hook_strength,
        best_use,
        voiceover_needed,
        face_cam,
        carousel_ready,
        priority_level,
        usage_count,
        last_used_date,
        cooldown_weeks,
    ) = folder_data

    score = 0

    score += score_value(priority_level)
    score += score_value(hook_strength)

    best_use = (best_use or "").lower()
    usage_count = usage_count or 0

    if post_format == "video" and best_use in {"reel", "video"}:
        score += 3
    elif post_format == "graphic" and best_use in {"graphic", "carousel"}:
        score += 3
    elif post_format == "mix" and best_use in {"mix", "carousel", "video", "reel"}:
        score += 2

    if post_format in {"graphic", "mix"} and carousel_ready == 1:
        score += 2

    if post_format == "video" and voiceover_needed == 1:
        score += 1

    if post_format == "video" and face_cam == 1:
        score += 1

    score -= usage_count

    return score


def get_best_folder_for_day(cur, pillar: str, post_format: str, used_folders: set[str]):
    cur.execute("""
        SELECT
            content_folders.folder_name,
            folder_notes.hook_strength,
            folder_notes.best_use,
            folder_notes.voiceover_needed,
            folder_notes.face_cam,
            folder_notes.carousel_ready,
            folder_notes.priority_level,
            COUNT(folder_usage.id) as usage_count,
            content_folders.last_used_date,
            content_folders.cooldown_weeks
        FROM content_folders
        LEFT JOIN folder_notes
            ON content_folders.id = folder_notes.folder_id
        LEFT JOIN folder_usage
            ON content_folders.folder_name = folder_usage.folder_name
        WHERE content_folders.content_pillar = ?
        GROUP BY
            content_folders.folder_name,
            folder_notes.hook_strength,
            folder_notes.best_use,
            folder_notes.voiceover_needed,
            folder_notes.face_cam,
            folder_notes.carousel_ready,
            folder_notes.priority_level,
            content_folders.last_used_date,
            content_folders.cooldown_weeks
        ORDER BY content_folders.folder_name
    """, (pillar,))

    rows = cur.fetchall()

    if not rows:
        return None

    available_rows = [
        row for row in rows
        if row[0] not in used_folders and not is_on_cooldown(row[8], row[9])
    ]

    # Fallback: if everything is on cooldown, allow reuse instead of leaving the day empty.
    if not available_rows:
        available_rows = [row for row in rows if row[0] not in used_folders]

    if not available_rows:
        return None

    scored_rows = []
    for row in available_rows:
        folder_name = row[0]
        score = score_folder_for_post(row, post_format)
        scored_rows.append((folder_name, score))

    scored_rows.sort(key=lambda x: x[1], reverse=True)

    return scored_rows[0][0]


def mark_folder_used(cur, folder_name: str):
    today = datetime.now().strftime("%Y-%m-%d")

    cur.execute("""
        UPDATE content_folders
        SET last_used_date = ?
        WHERE folder_name = ?
    """, (today, folder_name))

    cur.execute("""
        INSERT INTO folder_usage (folder_name, used_at)
        VALUES (?, ?)
    """, (folder_name, today))


def main():
    print("Starting smart weekly planner...")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM posts")
    print("Old posts cleared.")

    used_folders = set()

    for day_plan in WEEKLY_STRUCTURE:
        day = day_plan["day"]
        pillar = day_plan["pillar"]
        post_format = day_plan["format"]
        goal = day_plan["goal"]

        if is_ai_led_pillar(pillar):
            source_folder = None
            title = f"{day} - {pillar.replace('_', ' ').title()} Post"
        else:
            source_folder = get_best_folder_for_day(cur, pillar, post_format, used_folders)

            if source_folder:
                used_folders.add(source_folder)
                mark_folder_used(cur, source_folder)
                title = title_from_folder(source_folder, day, pillar)
            else:
                title = f"{day} - {pillar.replace('_', ' ').title()} Post"

        graphic_needed = 1 if post_format == "graphic" else 0

        cur.execute("""
            INSERT INTO posts (
                title,
                day_of_week,
                pillar,
                format,
                goal,
                source_folder,
                graphic_needed,
                story_needed,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            day,
            pillar,
            post_format,
            goal,
            source_folder,
            graphic_needed,
            1,
            "planned",
        ))

        print(f"{day}: selected -> {source_folder}")

    conn.commit()
    conn.close()

    print("Smart weekly content plan generated.")


if __name__ == "__main__":
    main()