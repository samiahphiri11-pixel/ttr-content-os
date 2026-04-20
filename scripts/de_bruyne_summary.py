import sqlite3
from pathlib import Path

DB_PATH = Path("data/content.db")
EXPORTS_DIR = Path("exports")
OUTPUT_PATH = EXPORTS_DIR / "de_bruyne_summary.txt"


def main():
    EXPORTS_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            posts.id,
            posts.day_of_week,
            posts.title,
            posts.pillar,
            posts.format,
            analytics.platform,
            analytics.views,
            analytics.likes,
            analytics.comments,
            analytics.shares,
            analytics.saves,
            analytics.follows_gained,
            analytics.link_clicks,
            analytics.notes
        FROM analytics
        LEFT JOIN posts ON analytics.post_id = posts.id
        ORDER BY analytics.views DESC
    """)
    rows = cur.fetchall()

    if not rows:
        output = "No analytics found yet. Add analytics first."
        print(output)
        OUTPUT_PATH.write_text(output, encoding="utf-8")
        conn.close()
        return

    total_posts = len(rows)
    total_views = sum(row[6] or 0 for row in rows)
    total_likes = sum(row[7] or 0 for row in rows)
    total_comments = sum(row[8] or 0 for row in rows)
    total_shares = sum(row[9] or 0 for row in rows)
    total_saves = sum(row[10] or 0 for row in rows)
    total_follows = sum(row[11] or 0 for row in rows)

    avg_views = round(total_views / total_posts, 1)
    avg_likes = round(total_likes / total_posts, 1)
    avg_comments = round(total_comments / total_posts, 1)
    avg_shares = round(total_shares / total_posts, 1)
    avg_saves = round(total_saves / total_posts, 1)
    avg_follows = round(total_follows / total_posts, 1)

    top_post = rows[0]

    lines = []
    lines.append("DE BRUYNE ANALYTICS SUMMARY")
    lines.append("=" * 80)
    lines.append("")
    lines.append("OVERVIEW")
    lines.append("-" * 80)
    lines.append(f"Tracked Posts: {total_posts}")
    lines.append(f"Total Views: {total_views}")
    lines.append(f"Total Likes: {total_likes}")
    lines.append(f"Total Comments: {total_comments}")
    lines.append(f"Total Shares: {total_shares}")
    lines.append(f"Total Saves: {total_saves}")
    lines.append(f"Total Follows Gained: {total_follows}")
    lines.append("")
    lines.append("AVERAGES PER POST")
    lines.append("-" * 80)
    lines.append(f"Average Views: {avg_views}")
    lines.append(f"Average Likes: {avg_likes}")
    lines.append(f"Average Comments: {avg_comments}")
    lines.append(f"Average Shares: {avg_shares}")
    lines.append(f"Average Saves: {avg_saves}")
    lines.append(f"Average Follows Gained: {avg_follows}")
    lines.append("")
    lines.append("TOP PERFORMING POST")
    lines.append("-" * 80)
    lines.append(f"Post: {top_post[1]} - {top_post[2]}")
    lines.append(f"Pillar: {top_post[3]}")
    lines.append(f"Format: {top_post[4]}")
    lines.append(f"Platform: {top_post[5]}")
    lines.append(f"Views: {top_post[6]}")
    lines.append(f"Likes: {top_post[7]}")
    lines.append(f"Comments: {top_post[8]}")
    lines.append(f"Shares: {top_post[9]}")
    lines.append(f"Saves: {top_post[10]}")
    lines.append(f"Follows Gained: {top_post[11]}")
    lines.append(f"Notes: {top_post[13]}")
    lines.append("")
    lines.append("DE BRUYNE'S READ")
    lines.append("-" * 80)

    if total_shares > total_comments and total_saves > total_comments:
        lines.append("- Your content seems to be stronger at value delivery than conversation. Educational or useful posts may be resonating best.")
    if top_post[3] == "skills":
        lines.append("- Skills content is currently leading. Consider making skills a priority growth lever.")
    elif top_post[3] == "viral":
        lines.append("- Viral/fun content is driving the most reach. Use it to bring people in, then convert them with stronger value posts.")
    elif top_post[3] == "community":
        lines.append("- Community content is performing best. That suggests relatability and identity are connecting well.")
    elif top_post[3] == "mindset":
        lines.append("- Mindset content is standing out. This could mean your audience connects strongly with motivational identity-based content.")

    lines.append("- Watch saves and shares closely. Those are especially important for TT&R Elite because they signal practical value and future client trust.")
    lines.append("- Compare post pillars over time to see what consistently drives followers versus what drives engagement.")
    lines.append("- Use notes to track why a post worked, not just that it worked.")

    output = "\n".join(lines)
    print(output)
    OUTPUT_PATH.write_text(output, encoding="utf-8")

    print(f"\nSaved summary to: {OUTPUT_PATH}")

    conn.close()


if __name__ == "__main__":
    main()