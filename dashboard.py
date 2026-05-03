import base64
import sqlite3
import subprocess
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


if "player_filter" not in st.session_state:
    st.session_state.player_filter = "All"

DB_PATH = Path("data/content.db")
ASSETS = Path("assets")


def get_base64_image(image_path: Path) -> str:
    if not image_path.exists():
        return ""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


FIELD_IMAGE = get_base64_image(ASSETS / "field.jpg")

st.set_page_config(
    page_title="TT&R Elite AI Command Center",
    page_icon="⚽",
    layout="wide",
)

st.markdown(
    f"""
    <style>
        :root {{
            --text-main: #f5f7fb;
            --text-soft: #b9c2d0;
        }}

        .stApp {{
            background:
                radial-gradient(circle at top left, rgba(22,163,74,0.14), transparent 32%),
                radial-gradient(circle at top right, rgba(198,40,40,0.10), transparent 28%),
                linear-gradient(180deg, #061018 0%, #09131f 45%, #0a1420 100%);
            color: var(--text-main);
        }}

        .main .block-container {{
            padding-top: 2rem;
            padding-bottom: 4rem;
            max-width: 1450px;
        }}

        h1, h2, h3, h4 {{
            color: var(--text-main) !important;
            letter-spacing: -0.02em;
        }}

        .hero-wrap {{
            padding: 24px 28px;
            border-radius: 28px;
            border: 1px solid rgba(255,255,255,0.08);
            background:
                linear-gradient(135deg, rgba(13,92,44,0.35), rgba(9,19,31,0.92) 42%, rgba(139,30,36,0.20));
            box-shadow: 0 10px 30px rgba(0,0,0,0.25);
            margin-bottom: 18px;
        }}

        .hero-kicker {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            color: #c9d6e3;
            opacity: 0.85;
            margin-bottom: 10px;
        }}

        .hero-title {{
            font-size: 3rem;
            font-weight: 900;
            line-height: 1;
            margin-bottom: 0.5rem;
            color: white;
        }}

        .hero-sub {{
            font-size: 1rem;
            color: #d7deea;
            opacity: 0.9;
            max-width: 900px;
        }}

        .section-title {{
            font-size: 1.45rem;
            font-weight: 800;
            margin-top: 0.4rem;
            margin-bottom: 0.8rem;
            color: white;
        }}

        .section-hint {{
            color: var(--text-soft);
            font-size: 0.95rem;
            margin-top: -4px;
            margin-bottom: 12px;
        }}

        div[data-testid="stMetric"] {{
            background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.025));
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 14px 16px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
        }}

        div[data-testid="stMetricLabel"] {{
            color: #c8d1de !important;
        }}

        div[data-testid="stMetricValue"] {{
            color: white !important;
            font-weight: 800 !important;
        }}

        div[data-testid="stTextInput"] input {{
            background-color: rgba(255,255,255,0.04) !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            border-radius: 14px !important;
            color: white !important;
        }}

        div.stButton > button {{
            width: 100%;
            border-radius: 14px !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            background: linear-gradient(135deg, rgba(13,92,44,0.85), rgba(22,163,74,0.75)) !important;
            color: white !important;
            font-weight: 700 !important;
            padding: 0.65rem 1rem !important;
            box-shadow: 0 8px 22px rgba(0,0,0,0.18);
        }}

        div.stButton > button:hover {{
            border-color: rgba(255,255,255,0.20) !important;
            filter: brightness(1.05);
        }}

        div[data-testid="stExpander"] {{
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            background: rgba(255,255,255,0.025);
            overflow: hidden;
        }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 16px;
            overflow: hidden;
        }}

        div[data-testid="stImage"] img {{
            border-radius: 50%;
            border: 3px solid rgba(255,255,255,0.22);
            box-shadow: 0 0 18px rgba(255,255,255,0.08);
            object-fit: cover;
        }}

        .pill-good {{
            display: inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            background: rgba(22,163,74,0.18);
            border: 1px solid rgba(22,163,74,0.35);
            color: #b9f7c8;
            font-size: 0.84rem;
            font-weight: 600;
            margin-right: 6px;
            margin-bottom: 6px;
        }}

        .pill-bad {{
            display: inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            background: rgba(198,40,40,0.16);
            border: 1px solid rgba(198,40,40,0.32);
            color: #ffd0d0;
            font-size: 0.84rem;
            font-weight: 600;
            margin-right: 6px;
            margin-bottom: 6px;
        }}

        hr {{
            border-color: rgba(255,255,255,0.08);
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


def get_connection():
    return sqlite3.connect(DB_PATH)

def ensure_campaign_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_name TEXT,
            campaign_goal TEXT,
            campaign_start_date TEXT,
            campaign_end_date TEXT,
            campaign_priority TEXT,
            campaign_cta TEXT,
            campaign_notes TEXT,
            campaign_active INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def update_task_status(task_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET status = ? WHERE id = ?",
        (new_status, task_id),
    )
    conn.commit()
    conn.close()

def load_posts():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            id,
            day_of_week,
            scheduled_date,
            title,
            pillar,
            format,
            goal,
            source_folder,
            status,
            caption_ig,
            caption_tiktok,
            hashtags
        FROM posts
        ORDER BY id
        """,
        conn,
    )
    conn.close()
    return df


def load_tasks():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            tasks.id,
            tasks.post_id,
            tasks.task_type,
            tasks.status,
            tasks.notes,
            posts.day_of_week,
            posts.title
        FROM tasks
        LEFT JOIN posts ON tasks.post_id = posts.id
        ORDER BY tasks.id
        """,
        conn,
    )
    conn.close()
    return df


def load_agent_outputs():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            id,
            post_id,
            agent_name,
            role,
            output_type,
            content,
            updated_at
        FROM agent_outputs
        ORDER BY post_id, agent_name
        """,
        conn,
    )
    conn.close()
    return df


def load_analytics():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            analytics.id,
            analytics.post_id,
            analytics.platform,
            analytics.views,
            analytics.likes,
            analytics.comments,
            analytics.shares,
            analytics.saves,
            analytics.follows_gained,
            analytics.link_clicks,
            analytics.notes,
            posts.title,
            posts.pillar
        FROM analytics
        LEFT JOIN posts ON analytics.post_id = posts.id
        ORDER BY analytics.id DESC
        """,
        conn,
    )
    conn.close()
    return df

def load_active_campaign():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            campaign_name,
            campaign_goal,
            campaign_start_date,
            campaign_end_date,
            campaign_priority,
            campaign_cta,
            campaign_notes,
            campaign_active
        FROM campaigns
        WHERE campaign_active = 1
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cur.fetchone()
    conn.close()

    return row


def save_campaign(
    campaign_name,
    campaign_goal,
    campaign_start_date,
    campaign_end_date,
    campaign_priority,
    campaign_cta,
    campaign_notes,
    campaign_active,
):
    conn = get_connection()
    cur = conn.cursor()

    if campaign_active:
        cur.execute("UPDATE campaigns SET campaign_active = 0")

    cur.execute("""
        INSERT INTO campaigns (
            campaign_name,
            campaign_goal,
            campaign_start_date,
            campaign_end_date,
            campaign_priority,
            campaign_cta,
            campaign_notes,
            campaign_active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        campaign_name,
        campaign_goal,
        campaign_start_date,
        campaign_end_date,
        campaign_priority,
        campaign_cta,
        campaign_notes,
        1 if campaign_active else 0,
    ))

    conn.commit()
    conn.close()


def run_command(command, label, input_text=None):
    with st.spinner(label):
        result = subprocess.run(
            command,
            input=input_text,
            capture_output=True,
            text=True,
        )

    if result.returncode == 0:
        st.success(f"{label} finished!")
    else:
        st.error(f"{label} had errors.")

    with st.expander(f"View logs: {label}"):
        if result.stdout:
            st.text(result.stdout)
        if result.stderr:
            st.text("ERRORS:\n" + result.stderr)


def get_ready_posts(posts_df, tasks_df, outputs_df):
    ready_post_ids = []

    for _, post in posts_df.iterrows():
        post_id = post["id"]
        post_format = post["format"]

        post_tasks = tasks_df[tasks_df["post_id"] == post_id]
        post_outputs = outputs_df[outputs_df["post_id"] == post_id]

        has_ig = pd.notna(post["caption_ig"]) and str(post["caption_ig"]).strip() != ""
        has_tiktok = pd.notna(post["caption_tiktok"]) and str(post["caption_tiktok"]).strip() != ""
        has_hashtags = pd.notna(post["hashtags"]) and str(post["hashtags"]).strip() != ""
        has_outputs = len(post_outputs) > 0
        all_tasks_done = len(post_tasks) > 0 and (post_tasks["status"] == "done").all()

        if post_format == "video":
            ready = has_ig and has_tiktok and has_hashtags and has_outputs and all_tasks_done
        elif post_format == "graphic":
            ready = has_ig and has_hashtags and has_outputs and all_tasks_done
        else:
            ready = has_ig and has_hashtags and has_outputs and all_tasks_done

        if ready:
            ready_post_ids.append(post_id)

    return posts_df[posts_df["id"].isin(ready_post_ids)]

def export_buffer_csv(mode, filtered_posts_df=None, ready_posts_df=None):
    if mode == "full":
        command = [sys.executable, "scripts/export_buffer_csv.py"]

    elif mode == "ready":
        if ready_posts_df is None or ready_posts_df.empty:
            st.warning("No ready posts to export.")
            return
        command = [sys.executable, "scripts/export_buffer_csv.py", "ready"]

    elif mode == "filtered":
        if filtered_posts_df is None or filtered_posts_df.empty:
            st.warning("No filtered posts to export.")
            return
        command = [sys.executable, "scripts/export_buffer_csv.py", "filtered"]

    else:
        st.error("Invalid export mode.")
        return

    run_command(command, f"Buffer Export: {mode.title()}")


def build_missing_items(posts_df, tasks_df, outputs_df):
    rows = []

    for _, post in posts_df.iterrows():
        post_id = post["id"]
        post_format = post["format"]

        post_tasks = tasks_df[tasks_df["post_id"] == post_id]
        post_outputs = outputs_df[outputs_df["post_id"] == post_id]

        has_ig = pd.notna(post["caption_ig"]) and str(post["caption_ig"]).strip() != ""
        has_tiktok = pd.notna(post["caption_tiktok"]) and str(post["caption_tiktok"]).strip() != ""
        has_hashtags = pd.notna(post["hashtags"]) and str(post["hashtags"]).strip() != ""
        has_outputs = len(post_outputs) > 0
        all_tasks_done = len(post_tasks) > 0 and (post_tasks["status"] == "done").all()

        missing = []

        if not has_ig:
            missing.append("IG caption")
        if post_format == "video" and not has_tiktok:
            missing.append("TikTok caption")
        if not has_hashtags:
            missing.append("hashtags")
        if not has_outputs:
            missing.append("agent outputs")
        if not all_tasks_done:
            missing.append("unfinished tasks")

        rows.append(
            {
                "Post ID": post_id,
                "Day": post["day_of_week"],
                "Title": post["title"],
                "Missing": ", ".join(missing) if missing else "Nothing missing",
            }
        )

    return pd.DataFrame(rows)


def get_sunday_match_day_plan(posts_df, tasks_df, outputs_df):
    total_posts = len(posts_df)

    ready_posts = 0
    missing_captions = 0
    missing_tasks = 0
    missing_outputs = 0

    needs_editing = 0
    ready_to_schedule = 0
    scheduled = 0
    posted = 0

    for _, post in posts_df.iterrows():
        post_id = post["id"]
        post_format = post["format"]
        status = post["status"]

        post_tasks = tasks_df[tasks_df["post_id"] == post_id]
        post_outputs = outputs_df[outputs_df["post_id"] == post_id]

        has_ig = pd.notna(post["caption_ig"]) and str(post["caption_ig"]).strip() != ""
        has_tiktok = pd.notna(post["caption_tiktok"]) and str(post["caption_tiktok"]).strip() != ""
        has_hashtags = pd.notna(post["hashtags"]) and str(post["hashtags"]).strip() != ""
        has_outputs = len(post_outputs) > 0
        all_tasks_done = len(post_tasks) > 0 and (post_tasks["status"] == "done").all()

        if status == "needs_editing":
            needs_editing += 1
        elif status == "ready_to_schedule":
            ready_to_schedule += 1
        elif status == "scheduled":
            scheduled += 1
        elif status == "posted":
            posted += 1

        if not has_ig or (post_format == "video" and not has_tiktok) or not has_hashtags:
            missing_captions += 1

        if not all_tasks_done:
            missing_tasks += 1

        if not has_outputs:
            missing_outputs += 1

        if post_format == "video":
            ready = has_ig and has_tiktok and has_hashtags and has_outputs and all_tasks_done
        elif post_format == "graphic":
            ready = has_ig and has_hashtags and has_outputs and all_tasks_done
        else:
            ready = has_ig and has_hashtags and has_outputs and all_tasks_done

        if ready:
            ready_posts += 1

    if ready_posts == total_posts and total_posts > 0:
        headline = "✅ Match day complete. The whole week is ready for Buffer."
    elif ready_posts > 0:
        headline = f"⚽ {ready_posts} of {total_posts} posts are ready for Buffer."
    else:
        headline = "⚠️ Nothing is fully ready yet. Time to lock in."

    checklist = [
        "Run Full Week Workflow",
        "Run AI Content Team",
        "Review captions and hooks",
        "Finish video edits",
        "Approve or create graphics",
        "Update post statuses",
        "Export posts for Buffer",
        "Queue the full week in Buffer",
    ]

    return {
        "headline": headline,
        "ready_posts": ready_posts,
        "total_posts": total_posts,
        "missing_captions": missing_captions,
        "missing_tasks": missing_tasks,
        "missing_outputs": missing_outputs,
        "needs_editing": needs_editing,
        "ready_to_schedule": ready_to_schedule,
        "scheduled": scheduled,
        "posted": posted,
        "checklist": checklist,
    }


def render_starting_xi_html(posts_df: pd.DataFrame, analytics_df: pd.DataFrame) -> str:
    field_b64 = get_base64_image(ASSETS / "field.jpg")

    player_images = {
        "Neymar": get_base64_image(ASSETS / "neymar.png"),
        "Messi": get_base64_image(ASSETS / "messi.png"),
        "Mbappé": get_base64_image(ASSETS / "mbappe.png"),
        "Modrić": get_base64_image(ASSETS / "modric.png"),
        "Xavi": get_base64_image(ASSETS / "xavi.png"),
        "De Bruyne": get_base64_image(ASSETS / "de_bruyne.png"),
        "Ronaldo": get_base64_image(ASSETS / "ronaldo.png"),
    }

    video_posts = posts_df[posts_df["format"] == "video"]
    graphic_posts = posts_df[posts_df["format"] == "graphic"]
    mix_posts = posts_df[posts_df["format"] == "mix"]
    missing_ig = posts_df[
        posts_df["caption_ig"].isna()
        | (posts_df["caption_ig"].fillna("").str.strip() == "")
    ]

    stats = {
        "Neymar": len(graphic_posts) + len(mix_posts),
        "Messi": len(posts_df),
        "Mbappé": len(posts_df),
        "Modrić": len(video_posts) + len(mix_posts),
        "Xavi": len(missing_ig),
        "De Bruyne": len(analytics_df),
        "Ronaldo": len(video_posts),
    }

    roles = {
        "Neymar": "Creative / Design",
        "Messi": "Strategy / Playmaker",
        "Mbappé": "Stories / Energy",
        "Modrić": "Repurpose / Flow",
        "Xavi": "Captions / Vision",
        "De Bruyne": "Analytics / Precision",
        "Ronaldo": "Video / Execution",
    }

    captions = {
        "Neymar": "graphics + visuals",
        "Messi": "controls the system",
        "Mbappé": "daily engagement",
        "Modrić": "content recycling",
        "Xavi": "writing control",
        "De Bruyne": "data + insight",
        "Ronaldo": "finishing content",
    }

    def card(name: str) -> str:
        img = player_images[name]
        img_html = (
            f'<img src="data:image/png;base64,{img}" class="player-img" />'
            if img
            else '<div class="player-fallback">⚽</div>'
        )

        if name == "Xavi":
            badge_class = "badge-missing"
            badge_text = "MISSING"
        elif name == "Ronaldo":
            badge_class = "badge-progress"
            badge_text = "IN PROGRESS"
        elif name == "De Bruyne" and stats[name] > 0:
            badge_class = "badge-ready"
            badge_text = "READY"
        else:
            badge_class = "badge-ready"
            badge_text = "READY"

        return f"""
        <div class="player-card-html">
            <div class="badge {badge_class}">{badge_text}</div>
            <div class="img-wrap">{img_html}</div>
            <div class="player-name">{name}</div>
            <div class="player-role">{roles[name]}</div>
            <div class="stat-box-html">
                <div class="stat-label-html">Workload</div>
                <div class="stat-value-html">{stats[name]}</div>
            </div>
            <div class="player-foot-html">{captions[name]}</div>
        </div>
        """

    field_bg = (
        f'background-image: linear-gradient(rgba(0,0,0,0.50), rgba(0,0,0,0.72)), '
        f'url("data:image/jpeg;base64,{field_b64}");'
        if field_b64
        else 'background: linear-gradient(180deg, rgba(20,110,48,0.92), rgba(9,64,28,0.96));'
    )

    return f"""
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            font-family: Inter, system-ui, sans-serif;
            color: #f5f7fb;
            background: transparent;
        }}
        .xi-wrap {{
            position: relative;
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 28px;
            padding: 26px;
            overflow: hidden;
            {field_bg}
            background-size: cover;
            background-position: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.22);
        }}
        .xi-wrap::before {{
            content: "";
            position: absolute;
            inset: 0;
            background:
                repeating-linear-gradient(
                    to bottom,
                    rgba(255,255,255,0.035) 0px,
                    rgba(255,255,255,0.035) 2px,
                    transparent 2px,
                    transparent 54px
                );
            pointer-events: none;
        }}
        .xi-wrap::after {{
            content: "";
            position: absolute;
            inset: 18px;
            border: 2px solid rgba(255,255,255,0.10);
            border-radius: 20px;
            pointer-events: none;
        }}
        .caption {{
            position: relative;
            z-index: 2;
            color: #e1ebf5;
            opacity: 0.9;
            font-size: 14px;
            margin-bottom: 18px;
        }}
        .row {{
            position: relative;
            z-index: 2;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 24px;
            margin-bottom: 26px;
        }}
        .row.striker {{
            grid-template-columns: 1fr 1fr 1fr;
        }}
        .row.striker .center {{
            grid-column: 2;
        }}
        .midline {{
            position: relative;
            z-index: 2;
            height: 70px;
            margin: 4px 0 8px;
        }}
        .midline::before {{
            content: "";
            position: absolute;
            left: 50%;
            top: -10px;
            bottom: -10px;
            width: 2px;
            transform: translateX(-50%);
            background: rgba(255,255,255,0.12);
        }}
        .midline::after {{
            content: "";
            position: absolute;
            left: 50%;
            top: 50%;
            width: 70px;
            height: 70px;
            transform: translate(-50%, -50%);
            border: 2px solid rgba(255,255,255,0.12);
            border-radius: 50%;
        }}
        .player-card-html {{
            position: relative;
            background: rgba(6, 17, 27, 0.55);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 22px;
            padding: 16px;
            backdrop-filter: blur(6px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.18);
            min-height: 240px;
        }}
        .badge {{
            position: absolute;
            top: 14px;
            right: 14px;
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.04em;
        }}
        .badge-ready {{
            background: rgba(22,163,74,0.18);
            border: 1px solid rgba(22,163,74,0.35);
            color: #b9f7c8;
        }}
        .badge-missing {{
            background: rgba(198,40,40,0.16);
            border: 1px solid rgba(198,40,40,0.32);
            color: #ffd0d0;
        }}
        .badge-progress {{
            background: rgba(244,197,66,0.16);
            border: 1px solid rgba(244,197,66,0.32);
            color: #ffe8a3;
        }}
        .img-wrap {{
            text-align: center;
            margin-bottom: 12px;
        }}
        .player-img {{
            width: 74px;
            height: 74px;
            object-fit: cover;
            border-radius: 50%;
            border: 3px solid rgba(255,255,255,0.22);
            box-shadow: 0 0 18px rgba(255,255,255,0.08);
        }}
        .player-fallback {{
            font-size: 32px;
        }}
        .player-name {{
            font-size: 22px;
            font-weight: 800;
            margin-bottom: 6px;
            color: white;
        }}
        .player-role {{
            font-size: 14px;
            color: #d7deea;
            margin-bottom: 14px;
        }}
        .stat-box-html {{
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 12px 14px;
            background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.025));
            margin-bottom: 12px;
        }}
        .stat-label-html {{
            font-size: 13px;
            color: #c8d1de;
            margin-bottom: 4px;
        }}
        .stat-value-html {{
            font-size: 22px;
            font-weight: 800;
            color: white;
        }}
        .player-foot-html {{
            font-size: 13px;
            color: #d7deea;
            opacity: 0.9;
        }}
    </style>
    </head>
    <body>
        <div class="xi-wrap">
            <div class="caption">Formation view of your content team roles.</div>

            <div class="row">
                {card("Neymar")}
                {card("Messi")}
                {card("Mbappé")}
            </div>

            <div class="midline"></div>

            <div class="row">
                {card("Modrić")}
                {card("Xavi")}
                {card("De Bruyne")}
            </div>

            <div class="row striker">
                <div></div>
                <div class="center">{card("Ronaldo")}</div>
                <div></div>
            </div>
        </div>
    </body>
    </html>
    """


def ensure_monthly_strategy_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS monthly_strategy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month_name TEXT,
            monthly_theme TEXT,
            main_goal TEXT,
            secondary_goal TEXT,
            priority_pillars TEXT,
            campaign_focus TEXT,
            strategy_notes TEXT,
            strategy_active INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


ensure_campaign_table()
ensure_monthly_strategy_table()


posts_df = load_posts()
tasks_df = load_tasks()
outputs_df = load_agent_outputs()
analytics_df = load_analytics()
active_campaign = load_active_campaign()

ready_posts_df = get_ready_posts(posts_df, tasks_df, outputs_df)
missing_df = build_missing_items(posts_df, tasks_df, outputs_df)
sunday_plan = get_sunday_match_day_plan(posts_df, tasks_df, outputs_df)

st.markdown(
    """
    <div class="hero-wrap">
        <div class="hero-kicker">TT&R Elite • AI Operations • Matchday Control</div>
        <div class="hero-title">⚽ TT&R Elite AI Command Center</div>
        <div class="hero-sub">
            Your soccer-themed content HQ for planning, AI creation, execution, scheduling, and review.
            Sunday is match day. Build the whole week and queue it in Buffer.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title">🗓️ Monthly Strategy</div>', unsafe_allow_html=True)
st.caption("Set the direction for this month’s content.")

def load_active_strategy():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            month_name,
            monthly_theme,
            main_goal,
            secondary_goal,
            priority_pillars,
            campaign_focus,
            strategy_notes
        FROM monthly_strategy
        WHERE strategy_active = 1
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cur.fetchone()
    conn.close()
    return row

def save_strategy(month, theme, main_goal, secondary_goal, pillars, campaign_focus, notes):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("UPDATE monthly_strategy SET strategy_active = 0")

    cur.execute("""
        INSERT INTO monthly_strategy (
            month_name,
            monthly_theme,
            main_goal,
            secondary_goal,
            priority_pillars,
            campaign_focus,
            strategy_notes,
            strategy_active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        month,
        theme,
        main_goal,
        secondary_goal,
        pillars,
        campaign_focus,
        notes
    ))

    conn.commit()
    conn.close()

active_strategy = load_active_strategy()

with st.container(border=True):
    default_month = active_strategy[0] if active_strategy else ""
    default_theme = active_strategy[1] if active_strategy else ""
    default_main = active_strategy[2] if active_strategy else ""
    default_secondary = active_strategy[3] if active_strategy else ""
    default_pillars = active_strategy[4] if active_strategy else ""
    default_campaign = active_strategy[5] if active_strategy else ""
    default_notes = active_strategy[6] if active_strategy else ""

    col1, col2 = st.columns(2)

    with col1:
        month = st.text_input("Month", value=default_month)
        theme = st.text_input("Monthly Theme", value=default_theme)
        main_goal = st.text_input("Main Goal", value=default_main)

    with col2:
        secondary_goal = st.text_input("Secondary Goal", value=default_secondary)
        pillars = st.text_input("Priority Pillars", value=default_pillars)
        campaign_focus = st.text_input("Campaign Focus", value=default_campaign)

    notes = st.text_area("Strategy Notes", value=default_notes)

    if st.button("💾 Save Monthly Strategy", use_container_width=True):
        save_strategy(month, theme, main_goal, secondary_goal, pillars, campaign_focus, notes)
        st.success("Monthly strategy saved.")
        st.rerun()

if active_strategy:
    st.success(f"Active Strategy: {active_strategy[0]} — {active_strategy[1]}")
else:
    st.info("No monthly strategy set.")

st.markdown('<div class="section-title">📣 Campaign Mode</div>', unsafe_allow_html=True)
st.caption("Use this when TT&R is promoting a camp, tournament, private training, tryouts, or special offer.")

with st.container(border=True):
    campaign_active = st.checkbox("Campaign Mode ON", value=active_campaign is not None)

    default_name = active_campaign[1] if active_campaign else ""
    default_goal = active_campaign[2] if active_campaign else ""
    default_start = active_campaign[3] if active_campaign else ""
    default_end = active_campaign[4] if active_campaign else ""
    default_priority = active_campaign[5] if active_campaign else "Medium"
    default_cta = active_campaign[6] if active_campaign else ""
    default_notes = active_campaign[7] if active_campaign else ""

    c1, c2 = st.columns(2)

    with c1:
        campaign_name = st.text_input("Campaign Name", value=default_name)
        campaign_goal = st.text_input("Campaign Goal", value=default_goal)
        campaign_start_date = st.text_input("Start Date", value=default_start)

    with c2:
        campaign_end_date = st.text_input("End Date", value=default_end)
        campaign_priority = st.selectbox(
            "Priority",
            ["Low", "Medium", "High"],
            index=["Low", "Medium", "High"].index(default_priority)
            if default_priority in ["Low", "Medium", "High"]
            else 1,
        )
        campaign_cta = st.text_input("Campaign CTA", value=default_cta)

    campaign_notes = st.text_area("Campaign Notes", value=default_notes)

    if st.button("💾 Save Campaign Settings", use_container_width=True):
        save_campaign(
            campaign_name,
            campaign_goal,
            campaign_start_date,
            campaign_end_date,
            campaign_priority,
            campaign_cta,
            campaign_notes,
            campaign_active,
        )
        st.success("Campaign settings saved.")
        st.rerun()

if active_campaign:
    st.success(f"Campaign Mode Active: {active_campaign[1]}")
else:
    st.info("Campaign Mode is currently off.")

st.markdown('<div class="section-title">🗓️ Week Setup</div>', unsafe_allow_html=True)

workflow_col1, workflow_col2 = st.columns([1, 1])

with workflow_col1:
    monday_date = st.text_input(
        "Week Monday Date (YYYY-MM-DD)",
        value="2026-04-13",
    )

    if st.button("🗓️ Run Full Week Workflow", key="run_full_week", use_container_width=True):
        with st.spinner("Running Full Week Workflow..."):
            result = subprocess.run(
                [sys.executable, "scripts/run_full_week.py"],
                input=monday_date + "\n",
                capture_output=True,
                text=True,
                cwd="."
            )

        st.write("Return code:", result.returncode)

        with st.expander("View logs: Full Week Workflow", expanded=True):
            st.markdown("### STDOUT")
            st.text(result.stdout if result.stdout else "[no stdout]")

            st.markdown("### STDERR")
            st.text(result.stderr if result.stderr else "[no stderr]")

        if result.returncode == 0:
            st.success("Full Week Workflow finished!")
        else:
            st.error("Full Week Workflow had errors.")

with workflow_col2:
    if st.button("🚀 Run AI Content Team", key="run_ai_team", use_container_width=True):
        run_command(
            [sys.executable, "scripts/auto_generate_weekly_outputs.py"],
            "AI Content Team",
        )
        st.rerun()

st.divider()
st.markdown('<div class="section-title">🏁 Sunday Match Day Plan</div>', unsafe_allow_html=True)
st.caption("Your Sunday setup board for getting the whole week ready.")

plan_left, plan_right = st.columns([2, 1])

with plan_left:
    with st.container(border=True):
        st.success(sunday_plan["headline"])

        st.markdown("### Match Day Checklist")
        for item in sunday_plan["checklist"]:
            st.write(f"- {item}")

with plan_right:
    with st.container(border=True):
        st.metric("Ready for Buffer", f"{sunday_plan['ready_posts']}/{sunday_plan['total_posts']}")
        st.metric("Needs Editing", sunday_plan["needs_editing"])
        st.metric("Ready to Schedule", sunday_plan["ready_to_schedule"])
        st.metric("Scheduled", sunday_plan["scheduled"])
        st.metric("Posted", sunday_plan["posted"])
        st.metric("Posts Missing Captions", sunday_plan["missing_captions"])
        st.metric("Posts Missing Tasks", sunday_plan["missing_tasks"])
        st.metric("Posts Missing AI Outputs", sunday_plan["missing_outputs"])

st.divider()
st.markdown('<div class="section-title">✅ Ready for Buffer</div>', unsafe_allow_html=True)
st.caption("These posts are ready to queue for the week.")

if len(ready_posts_df) == 0:
    st.info("No posts are fully ready for Buffer yet.")
else:
    ready_cols = st.columns(2)
    for i, (_, row) in enumerate(ready_posts_df.iterrows()):
        with ready_cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"### {row['day_of_week']} — {row['title']}")
                st.write(f"**Format:** {row['format']}")
                st.write(f"**Goal:** {row['goal']}")
                st.write(f"**Date:** {row['scheduled_date']}")
                st.success("Ready to queue")

st.divider()
st.markdown("## 🏟️ Starting XI")
st.caption("Your AI team lined up on the pitch.")

components.html(
    render_starting_xi_html(posts_df, analytics_df),
    height=1120,
    scrolling=False,
)

st.markdown("### 🎮 Control Panel")
st.caption("Filter the dashboard by team role.")

filter_cols = st.columns(7)
players = ["All", "Xavi", "Ronaldo", "Neymar", "Modrić", "De Bruyne", "Messi"]

for i, player in enumerate(players):
    if filter_cols[i].button(player, key=f"filter_{player}", use_container_width=True):
        st.session_state.player_filter = player

st.divider()
st.markdown('<div class="section-title">📋 Weekly Content Output</div>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col2:
    if st.button("📤 Sync to Notion"):
        import subprocess, sys
        subprocess.run([sys.executable, "scripts/sync_to_notion.py"])
        st.success("Synced!")
        
st.caption(f"Current filter: {st.session_state.player_filter}")

filtered_posts = posts_df.copy()
selected_player = st.session_state.player_filter

if selected_player == "Ronaldo":
    filtered_posts = filtered_posts[filtered_posts["format"] == "video"]

elif selected_player == "Neymar":
    filtered_posts = filtered_posts[filtered_posts["format"].isin(["graphic", "mix"])]

# For Xavi, Messi, Modrić, De Bruyne, and All:
# keep all posts visible, because the main difference should be
# which agent outputs are shown inside each post.

for _, post in filtered_posts.iterrows():
    post_id = post["id"]
    day = post["day_of_week"]
    title = post["title"]
    ig = post["caption_ig"]
    tiktok = post["caption_tiktok"]
    hashtags = post["hashtags"]

    post_tasks = tasks_df[tasks_df["post_id"] == post_id]
    post_outputs = outputs_df[outputs_df["post_id"] == post_id]
    post_missing_row = missing_df[missing_df["Post ID"] == post_id]
    missing_text = (
        post_missing_row.iloc[0]["Missing"]
        if len(post_missing_row) > 0
        else "Nothing missing"
    )

    with st.expander(f"{day} — {title}"):
        action_col1, action_col2, action_col3 = st.columns(3)

        with action_col1:
            if st.button(
                f"🔁 Rerun AI for Post {post_id}",
                key=f"rerun_{post_id}",
                use_container_width=True,
            ):
                run_command(
                    [sys.executable, "scripts/auto_generate_single_post.py", str(post_id)],
                    f"Rerun AI for Post {post_id}",
                )
                st.rerun()

        with action_col2:
            if st.button(
                f"📦 Export Package {post_id}",
                key=f"export_{post_id}",
                use_container_width=True,
            ):
                run_command(
                    [sys.executable, "scripts/export_post_package.py", str(post_id)],
                    f"Export Package for Post {post_id}",
                )

        with action_col3:
            st.info(f"Missing: {missing_text}")

        selected_player = st.session_state.player_filter

        meta_col1, meta_col2, meta_col3, meta_col4 = st.columns(4)
        meta_col1.write(f"**Format:** {post['format']}")
        meta_col2.write(f"**Goal:** {post['goal']}")
        status_options = [
            "planned",
            "ai_generated",
            "needs_editing",
            "editing",
            "ready_to_schedule",
            "scheduled",
            "posted",
            "reviewed"
        ]

        current_status = post["status"] if post["status"] in status_options else "planned"

        new_status = meta_col3.selectbox(
            "Status",
            status_options,
            index=status_options.index(current_status),
            key=f"status_{post_id}"
        )

        if new_status != current_status:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "UPDATE posts SET status = ? WHERE id = ?",
                (new_status, post_id)
            )
            conn.commit()
            conn.close()
            st.rerun()
        meta_col4.write(f"**Date:** {post['scheduled_date']}")

        # ALL view = show everything
        if selected_player == "All":
            st.markdown("### ✍🏽 Instagram Caption")
            st.write(ig if pd.notna(ig) and str(ig).strip() else "Not generated")

            st.markdown("### 🎬 TikTok Caption")
            st.write(tiktok if pd.notna(tiktok) and str(tiktok).strip() else "Not generated")

            st.markdown("### #️⃣ Hashtags")
            st.write(hashtags if pd.notna(hashtags) and str(hashtags).strip() else "Not generated")

            st.markdown("### ✅ Tasks")

            if len(post_tasks) == 0:
                st.info("No tasks found.")
            else:
                for _, task in post_tasks.iterrows():
                    task_id = task["id"]
                    task_name = task["task_type"]
                    is_done = task["status"] == "done"

                    checked = st.checkbox(
                        task_name,
                        value=is_done,
                        key=f"task_{post_id}_{task_id}"
                    )

                    if checked != is_done:
                        new_status = "done" if checked else "todo"
                        update_task_status(task_id, new_status)
                        st.rerun()

        # XAVI = captions only
        elif selected_player == "Xavi":
            st.markdown("### ✍🏽 Caption Package")
            st.write(ig if pd.notna(ig) and str(ig).strip() else "No Instagram caption yet")
            st.write("")
            st.write(tiktok if pd.notna(tiktok) and str(tiktok).strip() else "No TikTok caption yet")
            st.write("")
            st.write(hashtags if pd.notna(hashtags) and str(hashtags).strip() else "No hashtags yet")

            xavi_outputs = post_outputs[
                post_outputs["agent_name"].fillna("").str.strip().str.lower() == "xavi"
            ]

            st.markdown("### 🤖 Xavi Output")
            if len(xavi_outputs) == 0:
                st.info("No Xavi output saved for this post yet.")
            else:
                for _, row in xavi_outputs.iterrows():
                    with st.expander(f"{row['agent_name']} — {row['output_type']}"):
                        st.text(row["content"])

        # RONALDO = video/editing only
        elif selected_player == "Ronaldo":
            ronaldo_outputs = post_outputs[
                post_outputs["agent_name"].fillna("").str.strip().str.lower() == "ronaldo"
            ]

            st.markdown("### 🎬 Video Edit Plan")

            video_tasks = post_tasks[
                post_tasks["task_type"].fillna("").str.lower().str.contains("video|edit", regex=True)
            ]

            if len(video_tasks) > 0:
                st.markdown("#### Related Tasks")
                st.dataframe(
                    video_tasks[["task_type", "status"]],
                    use_container_width=True,
                    hide_index=True,
                )

            if len(ronaldo_outputs) == 0:
                st.info("No Ronaldo output saved for this post yet.")
            else:
                for _, row in ronaldo_outputs.iterrows():
                    with st.expander(f"{row['agent_name']} — {row['output_type']}", expanded=True):
                        st.text(row["content"])

        # NEYMAR = design/graphic only
        elif selected_player == "Neymar":
            neymar_outputs = post_outputs[
                post_outputs["agent_name"].fillna("").str.strip().str.lower() == "neymar"
            ]

            st.markdown("### 🎨 Design Brief")

            design_tasks = post_tasks[
                post_tasks["task_type"].fillna("").str.lower().str.contains("graphic|design|create", regex=True)
            ]

            if len(design_tasks) > 0:
                st.markdown("#### Related Tasks")
                st.dataframe(
                    design_tasks[["task_type", "status"]],
                    use_container_width=True,
                    hide_index=True,
                )

            if len(neymar_outputs) == 0:
                st.info("No Neymar output saved for this post yet.")
            else:
                for _, row in neymar_outputs.iterrows():
                    with st.expander(f"{row['agent_name']} — {row['output_type']}", expanded=True):
                        st.text(row["content"])

        # MBAPPE = stories only
        elif selected_player == "Mbappé":
            mbappe_outputs = post_outputs[
                post_outputs["agent_name"].fillna("").str.strip().str.lower() == "mbappé"
            ]

            if len(mbappe_outputs) == 0:
                mbappe_outputs = post_outputs[
                    post_outputs["agent_name"].fillna("").str.strip().str.lower() == "mbappe"
                ]

            st.markdown("### 📲 Story Sequence")

            story_tasks = post_tasks[
                post_tasks["task_type"].fillna("").str.lower().str.contains("stor", regex=True)
            ]

            if len(story_tasks) > 0:
                st.markdown("#### Related Tasks")
                st.dataframe(
                    story_tasks[["task_type", "status"]],
                    use_container_width=True,
                    hide_index=True,
                )

            if len(mbappe_outputs) == 0:
                st.info("No Mbappé output saved for this post yet.")
            else:
                for _, row in mbappe_outputs.iterrows():
                    with st.expander(f"{row['agent_name']} — {row['output_type']}", expanded=True):
                        st.text(row["content"])

        # MESSI = strategy only
        elif selected_player == "Messi":
            messi_outputs = post_outputs[
                post_outputs["agent_name"].fillna("").str.strip().str.lower() == "messi"
            ]

            st.markdown("### 🧠 Strategy Notes")

            if len(messi_outputs) == 0:
                st.info("No Messi output saved for this post yet.")
            else:
                for _, row in messi_outputs.iterrows():
                    with st.expander(f"{row['agent_name']} — {row['output_type']}", expanded=True):
                        st.text(row["content"])

        # MODRIC = repurpose only
        elif selected_player == "Modrić":
            modric_outputs = post_outputs[
                post_outputs["agent_name"].fillna("").str.strip().str.lower() == "modrić"
            ]

            if len(modric_outputs) == 0:
                modric_outputs = post_outputs[
                    post_outputs["agent_name"].fillna("").str.strip().str.lower() == "modric"
                ]

            st.markdown("### 🔁 Repurpose Ideas")

            if len(modric_outputs) == 0:
                st.info("No Modrić output saved for this post yet.")
            else:
                for _, row in modric_outputs.iterrows():
                    with st.expander(f"{row['agent_name']} — {row['output_type']}", expanded=True):
                        st.text(row["content"])

        # DE BRUYNE = analytics only
        elif selected_player == "De Bruyne":
            debruyne_outputs = post_outputs[
                post_outputs["agent_name"].fillna("").str.strip().str.lower() == "de bruyne"
            ]

            if len(debruyne_outputs) == 0:
                debruyne_outputs = post_outputs[
                    post_outputs["agent_name"].fillna("").str.strip().str.lower() == "debruyne"
                ]

            st.markdown("### 📊 Analytics Notes")

            if len(debruyne_outputs) == 0:
                st.info("No De Bruyne output saved for this post yet.")
            else:
                for _, row in debruyne_outputs.iterrows():
                    with st.expander(f"{row['agent_name']} — {row['output_type']}", expanded=True):
                        st.text(row["content"])

total_posts = len(posts_df)
total_tasks = len(tasks_df)
done_tasks = len(tasks_df[tasks_df["status"] == "done"])
ready_posts = len(ready_posts_df)
completion_rate = round((done_tasks / total_tasks) * 100, 1) if total_tasks else 0

st.divider()
st.markdown('<div class="section-title">📤 Buffer Export Zone</div>', unsafe_allow_html=True)
st.caption("Export posts for Buffer based on your Sunday match day workflow.")

export_col1, export_col2, export_col3 = st.columns(3)

with export_col1:
    if st.button("📦 Export Full Week", key="export_full_week", use_container_width=True):
        export_buffer_csv("full")

with export_col2:
    if st.button("✅ Export Ready Posts Only", key="export_ready_only", use_container_width=True):
        export_buffer_csv("ready", ready_posts_df=ready_posts_df)

with export_col3:
    if st.button("🎯 Export Current Filter", key="export_current_filter", use_container_width=True):
        export_buffer_csv("filtered", filtered_posts_df=filtered_posts)

st.divider()
st.markdown('<div class="section-title">📊 Weekly Progress</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Posts", total_posts)
c2.metric("Tasks", total_tasks)
c3.metric("Done Tasks", done_tasks)
c4.metric("Completion %", f"{completion_rate}%")

st.divider()

left, right = st.columns([2, 1])

with left:
    st.markdown('<div class="section-title">⚠️ Missing Items</div>', unsafe_allow_html=True)
    st.dataframe(missing_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">🗓️ Weekly Schedule</div>', unsafe_allow_html=True)
    schedule_cols = ["scheduled_date", "day_of_week", "title", "format", "status", "goal"]
    st.dataframe(posts_df[schedule_cols], use_container_width=True, hide_index=True)

with right:
    st.markdown('<div class="section-title">📌 Quick Summary</div>', unsafe_allow_html=True)
    st.info(f"{len(ready_posts_df)} posts ready for Buffer")
    st.info(f"{len(missing_df[missing_df['Missing'] != 'Nothing missing'])} posts still need work")

st.divider()
st.markdown('<div class="section-title">📝 Task Board</div>', unsafe_allow_html=True)
st.dataframe(
    tasks_df[["post_id", "day_of_week", "title", "task_type", "status"]],
    use_container_width=True,
    hide_index=True,
)

st.markdown('<div class="section-title">📊 Log Post Performance</div>', unsafe_allow_html=True)
st.caption("Enter performance after posting to help the system learn what works.")

with st.container(border=True):
    post_options = posts_df[["id", "title"]].values.tolist()
    post_map = {f"{title} (ID {pid})": pid for pid, title in post_options}

    selected_post_label = st.selectbox("Select Post", list(post_map.keys()))
    selected_post_id = post_map[selected_post_label]

    col1, col2, col3 = st.columns(3)

    with col1:
        views = st.number_input("Views", min_value=0, step=1)
        likes = st.number_input("Likes", min_value=0, step=1)

    with col2:
        comments = st.number_input("Comments", min_value=0, step=1)
        shares = st.number_input("Shares", min_value=0, step=1)

    with col3:
        saves = st.number_input("Saves", min_value=0, step=1)
        follows = st.number_input("Follows Gained", min_value=0, step=1)

    notes = st.text_area("Notes (optional)")

    if st.button("💾 Save Performance", use_container_width=True):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO analytics (
                post_id,
                platform,
                views,
                likes,
                comments,
                shares,
                saves,
                follows_gained,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            selected_post_id,
            "instagram",
            views,
            likes,
            comments,
            shares,
            saves,
            follows,
            notes
        ))

        conn.commit()
        conn.close()

        st.success("Performance saved.")
        st.rerun()

if not analytics_df.empty:
    st.divider()
    st.markdown('<div class="section-title">📈 Analytics Snapshot</div>', unsafe_allow_html=True)
    st.dataframe(
        analytics_df[
            [
                "title",
                "pillar",
                "platform",
                "views",
                "likes",
                "comments",
                "shares",
                "saves",
                "follows_gained",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
st.markdown('<div class="section-title">🧠 Weekly Insights</div>', unsafe_allow_html=True)

if analytics_df.empty:
    st.info("No analytics data yet.")
else:
    # Best by views
    top_post = analytics_df.sort_values(by="views", ascending=False).iloc[0]

    # Best by saves
    best_save_post = analytics_df.sort_values(by="saves", ascending=False).iloc[0]

    st.write(f"🔥 Best performing post (views): {top_post['title']}")
    st.write(f"💾 Most saved post: {best_save_post['title']}")

    st.write("### Key Takeaways")
    st.write("- Replicate the format of the highest performing post")
    st.write("- Focus more on content that gets saves and shares")
    st.write("- Improve hooks on lower performing posts")