import sqlite3
import logging

from video_to_text.constants import TABLE_NAME

logger = logging.getLogger(__name__)

def init_db(db_filepath):
    with sqlite3.connect(db_filepath) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        logger.info("Creating new DB table if it doesn't exist")
        conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_url TEXT UNIQUE,
            title TEXT,
            published_at TEXT,
            transcript_path TEXT
        )
        """)
        conn.commit()

def save_to_db(video_url, title, published_at, transcript_path, db_filepath) -> int:
    try:
        with sqlite3.connect(db_filepath, timeout=30) as conn:
            logger.info("Writing to DB")

            cur = conn.cursor()
            cur.execute(
                "INSERT OR REPLACE INTO transcripts (video_url, title, published_at, transcript_path) VALUES (?, ?, ?, ?)",
                (video_url, title, published_at, transcript_path)
            )
            new_id = cur.lastrowid
            conn.commit()

            return new_id

    except sqlite3.OperationalError as e:
        print(f"Could not write to DB: {e}")
