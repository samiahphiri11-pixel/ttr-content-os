import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("\nPOST ANALYTICS")
    print("=" * 80)

    cur.execute("""
        SELECT
            analytics.id,
            posts.day_of_week,
            posts.title,
            analytics.platform,
            analytics.views,
            analytics.likes,
            analytics.comments,
            analytics.shares,
            analytics.saves,
            analytics.follows_gained,
            analytics.link_clicks,
            analytics.notes,
            analytics.recorded_at
        FROM analytics
        LEFT JOIN posts ON analytics.post_id = posts.id
        ORDER BY analytics.id
    """)
    rows = cur.fetchall()

    if not rows:
        print("No analytics found.")
    else:
        for row in rows:
            (
                analytics_id,
                day,
                title,
                platform,
                views,
                likes,
                comments,
                shares,
                saves,
                follows_gained,
                link_clicks,
                notes,
                recorded_at
            ) = row

            print(f"\nAnalytics ID: {analytics_id}")
            print("-" * 80)
            print(f"Post: {day} - {title}")
            print(f"Platform: {platform}")
            print(f"Views: {views}")
            print(f"Likes: {likes}")
            print(f"Comments: {comments}")
            print(f"Shares: {shares}")
            print(f"Saves: {saves}")
            print(f"Follows Gained: {follows_gained}")
            print(f"Link Clicks: {link_clicks}")
            print(f"Notes: {notes}")
            print(f"Recorded At: {recorded_at}")

    conn.close()


if __name__ == "__main__":
    main()