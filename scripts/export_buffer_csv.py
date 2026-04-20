import csv
import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")
EXPORTS_DIR = Path("exports")
OUTPUT_PATH = EXPORTS_DIR / "buffer_export.csv"


def get_default_platform(post_format: str) -> str:
    if post_format in {"video", "mix"}:
        return "Instagram,TikTok"
    elif post_format == "graphic":
        return "Instagram"
    return "Instagram"


def main():
    EXPORTS_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            day_of_week,
            title,
            pillar,
            format,
            goal,
            source_folder,
            status,
            scheduled_date,
            caption_ig,
            hashtags
        FROM posts
        ORDER BY id
    """)
    posts = cur.fetchall()

    if not posts:
        print("No posts found.")
        conn.close()
        return

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow([
            "post_id",
            "day_of_week",
            "scheduled_date",
            "title",
            "pillar",
            "format",
            "goal",
            "source_folder",
            "status",
            "platforms",
            "caption",
            "notes"
        ])

        for post in posts:
            (
                post_id,
                day_of_week,
                title,
                pillar,
                post_format,
                goal,
                source_folder,
                status,
                scheduled_date,
                caption_ig,
                hashtags
            ) = post
            platforms = get_default_platform(post_format)
            if caption_ig and hashtags:
                caption = f"{caption_ig}\n\n{hashtags}"
            elif caption_ig:
                caption = caption_ig
            elif hashtags:
                caption = hashtags
            else:
                caption = ""

            notes = f"Use content from folder: {source_folder}" if source_folder else "No source folder assigned"
            
            writer.writerow([
                post_id,
                day_of_week,
                scheduled_date,
                title,
                pillar,
                post_format,
                goal,
                source_folder,
                status,
                platforms,
                caption,
                notes
            ])

    conn.close()

    print(f"Buffer CSV exported to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()