import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")


def is_ready(post_format, caption_ig, caption_tiktok, hashtags, agent_output_count, total_tasks, done_tasks):
    has_ig_caption = bool(caption_ig and caption_ig.strip())
    has_tiktok_caption = bool(caption_tiktok and caption_tiktok.strip())
    has_hashtags = bool(hashtags and hashtags.strip())
    has_agent_outputs = agent_output_count > 0
    all_tasks_done = total_tasks > 0 and done_tasks == total_tasks

    if post_format == "video":
        return has_ig_caption and has_tiktok_caption and has_hashtags and has_agent_outputs and all_tasks_done
    elif post_format == "graphic":
        return has_ig_caption and has_hashtags and has_agent_outputs and all_tasks_done
    else:
        return has_ig_caption and has_hashtags and has_agent_outputs and all_tasks_done


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("\nREADY POSTS")
    print("=" * 80)

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

    ready_found = False

    for post in posts:
        post_id, day, title, post_format, status, caption_ig, caption_tiktok, hashtags = post

        cur.execute("SELECT COUNT(*) FROM tasks WHERE post_id = ?", (post_id,))
        total_tasks = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM tasks WHERE post_id = ? AND status = 'done'", (post_id,))
        done_tasks = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM agent_outputs WHERE post_id = ?", (post_id,))
        agent_output_count = cur.fetchone()[0]

        ready = is_ready(
            post_format,
            caption_ig,
            caption_tiktok,
            hashtags,
            agent_output_count,
            total_tasks,
            done_tasks
        )

        if ready:
            ready_found = True
            print(f"\n[Post {post_id}] {day} - {title}")
            print("-" * 80)
            print(f"Format: {post_format}")
            print(f"Status: {status}")
            print("Ready: yes")

    if not ready_found:
        print("No posts are fully ready yet.")

    conn.close()


if __name__ == "__main__":
    main()