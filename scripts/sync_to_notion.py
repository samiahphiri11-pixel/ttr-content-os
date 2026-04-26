import requests
import sqlite3
from pathlib import Path
import streamlit as st

DB_PATH = Path("data/content.db")

NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID = st.secrets["NOTION_DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}


def create_page(post):
    (
        post_id,
        day,
        title,
        pillar,
        post_format,
        goal,
        source_folder,
        caption_ig,
        caption_tiktok,
        hashtags
    ) = post

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {
                "title": [
                    {"text": {"content": title}}
                ]
            },
            "Day": {
                "select": {"name": day}
            },
            "Pillar": {
                "select": {"name": pillar}
            },
            "Format": {
                "select": {"name": post_format}
            },
            "Goal": {
                "select": {"name": goal}
            },
            "Source Folder": {
                "rich_text": [
                    {"text": {"content": str(source_folder or "")}}
                ]
            },
            "Instagram Caption": {
                "rich_text": [
                    {"text": {"content": caption_ig or ""}}
                ]
            },
            "TikTok Caption": {
                "rich_text": [
                    {"text": {"content": caption_tiktok or ""}}
                ]
            },
            "Hashtags": {
                "rich_text": [
                    {"text": {"content": hashtags or ""}}
                ]
            }
        }
    }

    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        json=data
    )

    if response.status_code != 200:
        print("Failed:", response.text)
    else:
        print(f"Synced: {title}")


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, day_of_week, title, pillar, format, goal,
               source_folder, caption_ig, caption_tiktok, hashtags
        FROM posts
    """)

    posts = cur.fetchall()

    for post in posts:
        create_page(post)

    conn.close()


if __name__ == "__main__":
    main()