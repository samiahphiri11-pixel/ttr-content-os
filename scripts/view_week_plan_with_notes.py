import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")


def yes_no(value: int) -> str:
    return "yes" if value == 1 else "no"


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("\nWEEKLY PLAN WITH FOLDER NOTES")
    print("=" * 90)

    cur.execute("""
        SELECT
            posts.id,
            posts.day_of_week,
            posts.title,
            posts.pillar,
            posts.format,
            posts.goal,
            posts.source_folder,
            posts.status
        FROM posts
        ORDER BY posts.id
    """)
    posts = cur.fetchall()

    if not posts:
        print("No weekly posts found.")
        conn.close()
        return

    for post in posts:
        post_id, day, title, pillar, post_format, goal, source_folder, status = post

        print(f"\n[Post {post_id}] {day}")
        print("-" * 90)
        print(f"Title: {title}")
        print(f"Pillar: {pillar}")
        print(f"Format: {post_format}")
        print(f"Goal: {goal}")
        print(f"Source Folder: {source_folder}")
        print(f"Status: {status}")

        if source_folder:
            cur.execute("""
                SELECT
                    folder_notes.hook_strength,
                    folder_notes.best_use,
                    folder_notes.voiceover_needed,
                    folder_notes.face_cam,
                    folder_notes.carousel_ready,
                    folder_notes.priority_level,
                    folder_notes.notes
                FROM folder_notes
                LEFT JOIN content_folders ON folder_notes.folder_id = content_folders.id
                WHERE content_folders.folder_name = ?
            """, (source_folder,))
            note = cur.fetchone()

            print("\nFolder Notes:")
            if note:
                (
                    hook_strength,
                    best_use,
                    voiceover_needed,
                    face_cam,
                    carousel_ready,
                    priority_level,
                    notes
                ) = note

                print(f"- Hook Strength: {hook_strength}")
                print(f"- Best Use: {best_use}")
                print(f"- Voiceover Needed: {yes_no(voiceover_needed)}")
                print(f"- Face Cam: {yes_no(face_cam)}")
                print(f"- Carousel Ready: {yes_no(carousel_ready)}")
                print(f"- Priority Level: {priority_level}")
                print(f"- Notes: {notes}")
            else:
                print("- No notes yet for this folder.")

    conn.close()


if __name__ == "__main__":
    main()