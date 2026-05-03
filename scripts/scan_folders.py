import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")
RAW_CONTENT_DIR = Path("raw_content")

VIDEO_EXTENSIONS = [".mp4", ".mov", ".m4v", ".avi"]
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".heic"]

DAY_FOLDER_MAP = {
    "monday_mindset": "mindset",
    "tuesday_skills": "skills",
    "wednesday_wellness": "wellness",
    "thursday_game_iq": "gameplay",
    "friday_fun": "viral",
    "saturday_training": "real_training",
    "sunday_community": "community",
}


def get_content_type(file_suffix: str) -> str:
    suffix = file_suffix.lower()

    if suffix in VIDEO_EXTENSIONS:
        return "video"

    if suffix in IMAGE_EXTENSIONS:
        return "image"

    return "other"


def detect_pillar_from_day_folder(day_folder: str) -> str:
    return DAY_FOLDER_MAP.get(day_folder.lower(), "general")

def get_default_cooldown(pillar: str) -> int:
    if pillar == "skills":
        return 3
    elif pillar == "gameplay":
        return 3
    elif pillar == "viral":
        return 2
    elif pillar == "real_training":
        return 2
    elif pillar == "community":
        return 2
    else:
        return 2


def folder_has_media(folder: Path) -> bool:
    for file in folder.iterdir():
        if file.is_file() and get_content_type(file.suffix) != "other":
            return True
    return False


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Clear old scanned folder/clip data so the DB matches your current folders
    cur.execute("DELETE FROM clips")
    cur.execute("DELETE FROM content_folders")
    cur.execute("DELETE FROM folder_usage")

    for day_folder in RAW_CONTENT_DIR.iterdir():
        if not day_folder.is_dir():
            continue

        day_folder_name = day_folder.name
        pillar = detect_pillar_from_day_folder(day_folder_name)

        # Scan folders INSIDE each day folder
        for content_folder in day_folder.iterdir():
            if not content_folder.is_dir():
                continue

            if not folder_has_media(content_folder):
                continue

            folder_name = content_folder.name
            folder_path = str(content_folder)

            cur.execute("""
                INSERT OR IGNORE INTO content_folders
                (folder_name, folder_path, content_pillar, cooldown_weeks)
                VALUES (?, ?, ?, ?)
            """, (
                folder_name,
                folder_path,
                pillar,
                get_default_cooldown(pillar)
            ))

            for file in content_folder.iterdir():
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
                            folder_name,
                            content_type
                        ))

    conn.commit()
    conn.close()

    print("Scan complete with day-folder detection.")


if __name__ == "__main__":
    main()