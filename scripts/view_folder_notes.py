import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")


def yes_no(value: int) -> str:
    return "yes" if value == 1 else "no"


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("\nFOLDER NOTES")
    print("=" * 80)

    cur.execute("""
        SELECT
            content_folders.folder_name,
            content_folders.content_pillar,
            folder_notes.hook_strength,
            folder_notes.best_use,
            folder_notes.voiceover_needed,
            folder_notes.face_cam,
            folder_notes.carousel_ready,
            folder_notes.priority_level,
            folder_notes.notes,
            folder_notes.updated_at
        FROM folder_notes
        LEFT JOIN content_folders ON folder_notes.folder_id = content_folders.id
        ORDER BY content_folders.folder_name
    """)
    rows = cur.fetchall()

    if not rows:
        print("No folder notes found.")
    else:
        for row in rows:
            (
                folder_name,
                content_pillar,
                hook_strength,
                best_use,
                voiceover_needed,
                face_cam,
                carousel_ready,
                priority_level,
                notes,
                updated_at
            ) = row

            print(f"\nFolder: {folder_name}")
            print("-" * 80)
            print(f"Pillar: {content_pillar}")
            print(f"Hook Strength: {hook_strength}")
            print(f"Best Use: {best_use}")
            print(f"Voiceover Needed: {yes_no(voiceover_needed)}")
            print(f"Face Cam: {yes_no(face_cam)}")
            print(f"Carousel Ready: {yes_no(carousel_ready)}")
            print(f"Priority Level: {priority_level}")
            print(f"Notes: {notes}")
            print(f"Updated At: {updated_at}")

    conn.close()


if __name__ == "__main__":
    main()