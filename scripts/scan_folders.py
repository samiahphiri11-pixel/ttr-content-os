import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")
RAW_CONTENT_DIR = Path("raw_content")

VIDEO_EXTENSIONS = [".mp4", ".mov", ".m4v", ".avi"]
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".heic"]

def get_content_type(file_suffix: str) -> str:
    suffix = file_suffix.lower()
    if suffix in VIDEO_EXTENSIONS:
        return "video"
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    return "other"

# 🔥 NEW: detect pillar from folder name
def detect_pillar(folder_name: str) -> str:
    name = folder_name.lower()

    if "skill" in name or "combo" in name or "faints" in name:
        return "skills"
    elif "1v1" in name or "game" in name:
        return "gameplay"
    elif "warmup" in name:
        return "wellness"
    elif "bloop" in name:
        return "viral"
    elif "camp" in name or "training" in name:
        return "real_training"
    elif "pic" in name:
        return "community"
    elif "rep" in name:
        return "mindset"
    else:
        return "general"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for folder in RAW_CONTENT_DIR.iterdir():
        if folder.is_dir():

            pillar = detect_pillar(folder.name)

            cur.execute("""
                INSERT OR IGNORE INTO content_folders (folder_name, folder_path, content_pillar)
                VALUES (?, ?, ?)
            """, (folder.name, str(folder), pillar))

            for file in folder.iterdir():
                if file.is_file():
                    content_type = get_content_type(file.suffix)

                    if content_type != "other":
                        cur.execute("""
                            INSERT OR IGNORE INTO clips
                            (file_name, file_path, folder_name, content_type)
                            VALUES (?, ?, ?, ?)
                        """, (
                            file.name,
                            str(file),
                            folder.name,
                            content_type
                        ))

    conn.commit()
    conn.close()

    print("Scan complete with pillar detection.")

if __name__ == "__main__":
    main()