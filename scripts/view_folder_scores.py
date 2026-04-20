import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("data/content.db")


def score_value(value: str) -> int:
    if not value:
        return 0

    value = value.lower()

    if value == "high":
        return 3
    elif value == "medium":
        return 2
    elif value == "low":
        return 1

    return 0


def score_folder_for_post(folder_data: tuple, post_format: str) -> tuple[int, list[str]]:
    (
        folder_name,
        hook_strength,
        best_use,
        voiceover_needed,
        face_cam,
        carousel_ready,
        priority_level
    ) = folder_data

    score = 0
    reasons = []

    priority_score = score_value(priority_level)
    hook_score = score_value(hook_strength)

    score += priority_score
    score += hook_score

    if priority_score:
        reasons.append(f"priority_level={priority_level} (+{priority_score})")
    if hook_score:
        reasons.append(f"hook_strength={hook_strength} (+{hook_score})")

    best_use = (best_use or "").lower()

    if post_format == "video" and best_use in {"reel", "video"}:
        score += 3
        reasons.append(f"best_use match ({best_use}) (+3)")
    elif post_format == "graphic" and best_use in {"graphic", "carousel"}:
        score += 3
        reasons.append(f"best_use match ({best_use}) (+3)")
    elif post_format == "mix" and best_use in {"mix", "carousel", "video", "reel"}:
        score += 2
        reasons.append(f"best_use partial match ({best_use}) (+2)")

    if post_format in {"graphic", "mix"} and carousel_ready == 1:
        score += 2
        reasons.append("carousel_ready=yes (+2)")

    if post_format == "video" and voiceover_needed == 1:
        score += 1
        reasons.append("voiceover_needed=yes (+1)")

    if post_format == "video" and face_cam == 1:
        score += 1
        reasons.append("face_cam=yes (+1)")

    return score, reasons


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/view_folder_scores.py <pillar> <format>")
        print("Example: python3 scripts/view_folder_scores.py skills video")
        return

    pillar = sys.argv[1]
    post_format = sys.argv[2]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            content_folders.folder_name,
            folder_notes.hook_strength,
            folder_notes.best_use,
            folder_notes.voiceover_needed,
            folder_notes.face_cam,
            folder_notes.carousel_ready,
            folder_notes.priority_level
        FROM content_folders
        LEFT JOIN folder_notes ON content_folders.id = folder_notes.folder_id
        WHERE content_folders.content_pillar = ?
        ORDER BY content_folders.folder_name
    """, (pillar,))
    rows = cur.fetchall()

    if not rows:
        print(f"No folders found for pillar '{pillar}'")
        conn.close()
        return

    scored = []
    for row in rows:
        folder_name = row[0]
        score, reasons = score_folder_for_post(row, post_format)
        scored.append((folder_name, score, reasons))

    scored.sort(key=lambda x: x[1], reverse=True)

    print(f"\nFOLDER SCORES FOR pillar={pillar} format={post_format}")
    print("=" * 80)

    for folder_name, score, reasons in scored:
        print(f"\nFolder: {folder_name}")
        print(f"Score: {score}")
        if reasons:
            for reason in reasons:
                print(f"- {reason}")
        else:
            print("- No folder notes contributing yet")

    conn.close()


if __name__ == "__main__":
    main()