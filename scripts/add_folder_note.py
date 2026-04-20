import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("data/content.db")


def to_int_bool(value: str) -> int:
    return 1 if value.lower() in {"1", "true", "yes", "y"} else 0


def main():
    if len(sys.argv) < 9:
        print("Usage:")
        print('python3 scripts/add_folder_note.py <folder_name> <hook_strength> <best_use> <voiceover_needed> <face_cam> <carousel_ready> <priority_level> "<notes>"')
        print("")
        print("Example:")
        print('python3 scripts/add_folder_note.py "Skill OTW" high reel yes no no high "Great for Tuesday skills post"')
        return

    folder_name = sys.argv[1]
    hook_strength = sys.argv[2]
    best_use = sys.argv[3]
    voiceover_needed = to_int_bool(sys.argv[4])
    face_cam = to_int_bool(sys.argv[5])
    carousel_ready = to_int_bool(sys.argv[6])
    priority_level = sys.argv[7]
    notes = sys.argv[8]

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, folder_name
        FROM content_folders
        WHERE folder_name = ?
    """, (folder_name,))
    folder = cur.fetchone()

    if not folder:
        print(f'No folder found with name "{folder_name}"')
        conn.close()
        return

    folder_id = folder[0]

    cur.execute("""
        SELECT id
        FROM folder_notes
        WHERE folder_id = ?
    """, (folder_id,))
    existing = cur.fetchone()

    if existing:
        cur.execute("""
            UPDATE folder_notes
            SET hook_strength = ?,
                best_use = ?,
                voiceover_needed = ?,
                face_cam = ?,
                carousel_ready = ?,
                priority_level = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE folder_id = ?
        """, (
            hook_strength,
            best_use,
            voiceover_needed,
            face_cam,
            carousel_ready,
            priority_level,
            notes,
            folder_id
        ))
        print(f'Updated notes for folder "{folder_name}".')
    else:
        cur.execute("""
            INSERT INTO folder_notes (
                folder_id,
                hook_strength,
                best_use,
                voiceover_needed,
                face_cam,
                carousel_ready,
                priority_level,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            folder_id,
            hook_strength,
            best_use,
            voiceover_needed,
            face_cam,
            carousel_ready,
            priority_level,
            notes
        ))
        print(f'Added notes for folder "{folder_name}".')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()