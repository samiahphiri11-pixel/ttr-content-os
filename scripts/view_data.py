import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("\nCONTENT FOLDERS:")
    print("-" * 40)

    cur.execute("SELECT id, folder_name, folder_path FROM content_folders ORDER BY folder_name")
    folders = cur.fetchall()

    if not folders:
        print("No folders found.")
    else:
        for folder_id, folder_name, folder_path in folders:
            print(f"ID: {folder_id}")
            print(f"Folder Name: {folder_name}")
            print(f"Folder Path: {folder_path}")

            cur.execute(
                "SELECT COUNT(*) FROM clips WHERE folder_name = ?",
                (folder_name,)
            )
            clip_count = cur.fetchone()[0]
            print(f"Clip Count: {clip_count}")
            print("-" * 40)

    print("\nCLIPS:")
    print("-" * 40)

    cur.execute("SELECT id, file_name, folder_name, content_type FROM clips ORDER BY folder_name, file_name")
    clips = cur.fetchall()

    if not clips:
        print("No clips found.")
    else:
        for clip_id, file_name, folder_name, content_type in clips:
            print(f"ID: {clip_id} | File: {file_name} | Folder: {folder_name} | Type: {content_type}")

    conn.close()

if __name__ == "__main__":
    main()