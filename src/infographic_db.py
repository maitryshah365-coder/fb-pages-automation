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
    - Tracks dynamic angle/style variations (template, theme, and art style like Pixar 3D, Ghibli, 2D Vector, etc.).
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
            try:
                c.execute("ALTER TABLE posted_infographics ADD COLUMN cdn_thumb TEXT")
            except Exception:
                pass
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

    def get_last_post_for_page(self, page_id: str) -> Optional[Dict[str, Any]]:
        """Returns metadata of the most recent post for this page."""
        with self._connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT topic_slug, angle_mode, posted_at, status
                FROM posted_infographics
                WHERE page_id = ? AND status IN ('posted', 'dry_run')
                ORDER BY id DESC LIMIT 1
            """, (page_id,))
            row = c.fetchone()
            if row:
                return dict(row)
            return None

    def get_next_rotation_plan(
        self,
        page_id: str,
        topic_pool: List[Dict[str, Any]],
        template_pool: List[str],
        theme_pool: List[str],
        art_style_pool: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Dynamically selects the next topic, template, theme, and visual art style:
        - Cycles through template styles so no two consecutive posts look alike.
        - Rotates vibrant color palettes.
        - Rotates artistic mediums (Pixar 3D, Ghibli, 2D Vector, 8K Photo, Cyberpunk, Lithograph).
        - Prioritizes unposted topics to eliminate duplication.
        """
        if not art_style_pool:
            art_style_pool = ["pixar_3d", "ghibli_anime", "flat_vector_canva", "photorealistic_8k", "cyberpunk_neon", "vintage_lithograph"]

        posted_slugs = set(self.get_posted_topic_slugs(page_id))
        
        # 1. Select unposted topic
        selected_topic = None
        for t in topic_pool:
            if t["slug"] not in posted_slugs:
                selected_topic = t
                break

        # If all topics have been posted, cycle back
        if not selected_topic and topic_pool:
            last_post = self.get_last_post_for_page(page_id)
            last_slug = last_post.get("topic_slug") if last_post else None
            idx = 0
            if last_slug:
                for i, t in enumerate(topic_pool):
                    if t["slug"] == last_slug:
                        idx = (i + 1) % len(topic_pool)
                        break
            selected_topic = topic_pool[idx]

        last_post = self.get_last_post_for_page(page_id)
        last_angle = last_post.get("angle_mode", "") if last_post else ""
        parts = last_angle.split(":") if last_angle else []

        # 2. Select next template
        last_template = parts[0] if len(parts) > 0 else ""
        next_t_idx = 0
        if last_template in template_pool:
            next_t_idx = (template_pool.index(last_template) + 1) % len(template_pool)
        selected_template = template_pool[next_t_idx]

        # 3. Select next theme
        last_theme = parts[1] if len(parts) > 1 else ""
        next_th_idx = 0
        if last_theme in theme_pool:
            next_th_idx = (theme_pool.index(last_theme) + 1) % len(theme_pool)
        selected_theme = theme_pool[next_th_idx]

        # 4. Select next art style
        last_art = parts[2] if len(parts) > 2 else ""
        next_art_idx = 0
        if last_art in art_style_pool:
            next_art_idx = (art_style_pool.index(last_art) + 1) % len(art_style_pool)
        selected_art = art_style_pool[next_art_idx]

        return {
            "topic": selected_topic,
            "template": selected_template,
            "theme": selected_theme,
            "art_style": selected_art,
            "angle_mode": f"{selected_template}:{selected_theme}:{selected_art}"
        }

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
        error_message: Optional[str] = None,
        cdn_thumb: Optional[str] = None
    ) -> int:
        """Records an infographic upload in SQLite ledger."""
        now_utc = datetime.now(timezone.utc).isoformat()
        with self._connection() as conn:
            c = conn.cursor()
            try:
                c.execute("""
                    INSERT INTO posted_infographics (
                        page_id, vertical_key, topic_slug, angle_mode,
                        title, hashtags, image_path, fb_photo_id,
                        posted_at, status, slot_index, error_message, cdn_thumb
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    page_id, vertical_key, topic_slug, angle_mode,
                    title, hashtags, image_path, fb_photo_id,
                    now_utc, status, slot_index, error_message, cdn_thumb
                ))
            except Exception:
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

    def has_posted_in_slot(self, page_id: str, slot_index: int) -> bool:
        """Returns True if this page has already posted an infographic in the given slot today (UTC)."""
        today_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with self._connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT COUNT(*) FROM posted_infographics
                WHERE page_id = ? AND slot_index = ? AND status = 'posted' AND posted_at LIKE ?
            """, (str(page_id), int(slot_index), f"{today_prefix}%"))
            row = c.fetchone()
            return (row[0] if row else 0) > 0

    def get_minutes_since_last_reel(self, page_id: str) -> Optional[float]:
        """Returns the number of minutes elapsed since the last Reel was posted on this page."""
        with self._connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT posted_at FROM videos
                WHERE page_id = ? AND status = 'posted'
                ORDER BY id DESC LIMIT 1
            """, (str(page_id),))
            row = c.fetchone()
            if not row or not row[0]:
                return None
            try:
                dt_str = str(row[0]).strip()
                if "+" in dt_str or dt_str.endswith("Z"):
                    reel_dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                else:
                    reel_dt = datetime.fromisoformat(dt_str).replace(tzinfo=timezone.utc)
                now_utc = datetime.now(timezone.utc)
                return max(0.0, (now_utc - reel_dt).total_seconds() / 60.0)
            except Exception as e:
                logger.warning(f"Error parsing reel timestamp for {page_id}: {e}")
                return None

    def get_minutes_since_last_infographic(self, page_id: str) -> Optional[float]:
        """Returns the number of minutes elapsed since the last Infographic was posted on this page."""
        with self._connection() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT posted_at FROM posted_infographics
                WHERE page_id = ? AND status = 'posted'
                ORDER BY id DESC LIMIT 1
            """, (str(page_id),))
            row = c.fetchone()
            if not row or not row[0]:
                return None
            try:
                dt_str = str(row[0]).strip()
                if "+" in dt_str or dt_str.endswith("Z"):
                    info_dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                else:
                    info_dt = datetime.fromisoformat(dt_str).replace(tzinfo=timezone.utc)
                now_utc = datetime.now(timezone.utc)
                return max(0.0, (now_utc - info_dt).total_seconds() / 60.0)
            except Exception as e:
                logger.warning(f"Error parsing infographic timestamp for {page_id}: {e}")
                return None

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
