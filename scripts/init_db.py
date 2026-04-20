import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "content.db")
DB_PATH = os.path.abspath(DB_PATH)

def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS content_folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folder_name TEXT,
    folder_path TEXT UNIQUE,
    content_pillar TEXT
)
""")    

    cur.execute("""
    CREATE TABLE IF NOT EXISTS clips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT,
        file_path TEXT UNIQUE,
        folder_name TEXT,
        content_type TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    day_of_week TEXT,
    pillar TEXT,
    format TEXT,
    goal TEXT,
    source_folder TEXT,
    hook TEXT,
    caption_ig TEXT,
    caption_tiktok TEXT,
    hashtags TEXT,
    graphic_needed INTEGER DEFAULT 0,
    story_needed INTEGER DEFAULT 1,
    repurpose_notes TEXT,
    status TEXT DEFAULT 'idea',
    scheduled_date TEXT,
    posted_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    task_type TEXT NOT NULL,
    status TEXT DEFAULT 'todo',
    deadline TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(post_id) REFERENCES posts(id)
)
""")
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    platform TEXT NOT NULL,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    follows_gained INTEGER DEFAULT 0,
    link_clicks INTEGER DEFAULT 0,
    notes TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(post_id) REFERENCES posts(id)
)
""")
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS folder_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folder_id INTEGER NOT NULL,
    hook_strength TEXT,
    best_use TEXT,
    voiceover_needed INTEGER DEFAULT 0,
    face_cam INTEGER DEFAULT 0,
    carousel_ready INTEGER DEFAULT 0,
    priority_level TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(folder_id) REFERENCES content_folders(id)
)
""")
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS folder_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folder_name TEXT NOT NULL,
    post_id INTEGER,
    day_of_week TEXT,
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(post_id) REFERENCES posts(id)
)
""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS agent_outputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    agent_name TEXT NOT NULL,
    role TEXT NOT NULL,
    output_type TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(post_id) REFERENCES posts(id)
)
""")

    conn.commit()
    conn.close()

    print("Database created.")

if __name__ == "__main__":
    main()