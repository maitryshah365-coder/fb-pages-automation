import sqlite3
import os
import logging
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

logger = logging.getLogger("fb_automation")

class InfographicDB:
    """
    SQLite Ledger for Automated Infographics:
    - Guarantees ZERO duplicate topics per page across infinite cycles.
    - Tracks dynamic angle variations (e.g. anatomy, funny habits, extreme stats).
    - Records upload history, post IDs, and timestamps.
    """

    def __init__(self, db_path: str = "data/posted_videos.db"):
        self.db_path = db_path
        self._init_tables()

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_tables(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        with self._connection() as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS posted_infographics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    page_id TEXT NOT NULL,
                    vertical_key TEXT NOT NULL,
                    topic_slug TEXT NOT NULL,
                    angle_mode TEXT NOT NULL,
                    title TEXT NOT NULL,
                    hashtags TEXT NOT NULL,
                    image_path TEXT,
                    fb_photo_id TEXT,
                    posted_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    slot_index INTEGER,
                    error_message TEXT
                )
            """)
            c.execute("""
                CREATE INDEX IF NOT EXISTS idx_infographics_page_topic
                ON posted_infographics (page_id, topic_slug, angle_mode)
            """)
            c.execute("""
                CREATE INDEX IF NOT EXISTS idx_infographics_posted_at
                ON posted_infographics (posted_at)
            """)
            conn.commit()

    def is_topic_angle_posted(self, page_id: str, topic_slug: str, angle_mode: str) -> bool:
        """Checks if this exact topic + angle was already posted on this page."""
        with self._connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id FROM posted_infographics
                WHERE page_id = ? AND topic_slug = ? AND angle_mode = ? AND status IN ('posted', 'dry_run')
                LIMIT 1
            """, (page_id, topic_slug, angle_mode))
            return c.fetchone() is not None

    def get_posted_topic_slugs(self, page_id: str) -> List[str]:
        """Returns all topic slugs already posted on this page."""
        with self._connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT DISTINCT topic_slug FROM posted_infographics
                WHERE page_id = ? AND status IN ('posted', 'dry_run')
            """, (page_id,))
            return [r[0] for r in c.fetchall()]

    def record_upload(
        self,
        page_id: str,
        vertical_key: str,
        topic_slug: str,
        angle_mode: str,
        title: str,
        hashtags: str,
        image_path: str,
        fb_photo_id: Optional[str],
        status: str = "posted",
        slot_index: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> int:
        """Records an infographic upload in SQLite ledger."""
        now_utc = datetime.now(timezone.utc).isoformat()
        with self._connection() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO posted_infographics (
                    page_id, vertical_key, topic_slug, angle_mode,
                    title, hashtags, image_path, fb_photo_id,
                    posted_at, status, slot_index, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                page_id, vertical_key, topic_slug, angle_mode,
                title, hashtags, image_path, fb_photo_id,
                now_utc, status, slot_index, error_message
            ))
            conn.commit()
            return c.lastrowid

    def get_today_upload_count(self, page_id: str) -> int:
        """Returns the number of infographics posted for this page today (UTC)."""
        today_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with self._connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT COUNT(*) FROM posted_infographics
                WHERE page_id = ? AND status = 'posted' AND posted_at LIKE ?
            """, (page_id, f"{today_prefix}%"))
            return c.fetchone()[0]

    def get_stats_summary(self) -> Dict[str, Any]:
        """Returns aggregated audit statistics for infographics."""
        with self._connection() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM posted_infographics WHERE status = 'posted'")
            total_posted = c.fetchone()[0]

            c.execute("SELECT COUNT(DISTINCT page_id) FROM posted_infographics WHERE status = 'posted'")
            active_pages = c.fetchone()[0]

            c.execute("SELECT vertical_key, COUNT(*) FROM posted_infographics WHERE status = 'posted' GROUP BY vertical_key")
            by_vertical = dict(c.fetchall())

            return {
                "total_infographics_posted": total_posted,
                "active_pages": active_pages,
                "by_vertical": by_vertical
            }
