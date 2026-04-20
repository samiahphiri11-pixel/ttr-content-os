import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("\nPOST COMPLETION CHECKLIST")
    print("=" * 100)

    cur.execute("""
        SELECT
            id,
            day_of_week,
            title,
            format,
            status,
            caption_ig,
            caption_tiktok,
            hashtags
        FROM posts
        ORDER BY id
    """)
    posts = cur.fetchall()

    if not posts:
        print("No posts found.")
        conn.close()
        return

    for post in posts:
        (
            post_id,
            day,
            title,
            post_format,
            status,
            caption_ig,
            caption_tiktok,
            hashtags
        ) = post

        cur.execute("""
            SELECT COUNT(*)
            FROM tasks
            WHERE post_id = ?
        """, (post_id,))
        total_tasks = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*)
            FROM tasks
            WHERE post_id = ? AND status = 'done'
        """, (post_id,))
        done_tasks = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*)
            FROM agent_outputs
            WHERE post_id = ?
        """, (post_id,))
        agent_output_count = cur.fetchone()[0]

        has_ig_caption = bool(caption_ig and caption_ig.strip())
        has_tiktok_caption = bool(caption_tiktok and caption_tiktok.strip())
        has_hashtags = bool(hashtags and hashtags.strip())
        has_agent_outputs = agent_output_count > 0
        all_tasks_done = total_tasks > 0 and done_tasks == total_tasks

        if post_format == "video":
            ready_to_schedule = has_ig_caption and has_tiktok_caption and has_hashtags and has_agent_outputs and all_tasks_done
        elif post_format == "graphic":
            ready_to_schedule = has_ig_caption and has_hashtags and has_agent_outputs and all_tasks_done
        else:
            ready_to_schedule = has_ig_caption and has_hashtags and has_agent_outputs and all_tasks_done

        print(f"\n[Post {post_id}] {day} - {title}")
        print("-" * 100)
        print(f"Format: {post_format}")
        print(f"Status: {status}")
        print(f"IG Caption: {yes_no(has_ig_caption)}")
        print(f"TikTok Caption: {yes_no(has_tiktok_caption)}")
        print(f"Hashtags: {yes_no(has_hashtags)}")
        print(f"Agent Outputs Saved: {yes_no(has_agent_outputs)} ({agent_output_count})")
        print(f"Tasks Done: {done_tasks}/{total_tasks}")
        print(f"All Tasks Complete: {yes_no(all_tasks_done)}")
        print(f"Ready to Schedule: {yes_no(ready_to_schedule)}")

        missing_items = []
        if not has_ig_caption:
            missing_items.append("IG caption")
        if post_format == "video" and not has_tiktok_caption:
            missing_items.append("TikTok caption")
        if not has_hashtags:
            missing_items.append("hashtags")
        if not has_agent_outputs:
            missing_items.append("agent outputs")
        if not all_tasks_done:
            missing_items.append("unfinished tasks")

        print("Missing:")
        if missing_items:
            for item in missing_items:
                print(f"- {item}")
        else:
            print("- nothing missing")

    conn.close()


if __name__ == "__main__":
    main()