import os
import sqlite3
import contextlib
from datetime import datetime, timezone
from typing import Optional, Set, Dict, Any, List


class DatabaseManager:
    """Manages SQLite persistent state for Google Drive to Facebook automation."""

    def __init__(self, db_path: str = "data/posted_videos.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self.init_db()

    @contextlib.contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            # Enable WAL mode for safe concurrent access and high integrity
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            yield conn
        finally:
            conn.close()

    def init_db(self) -> None:
        """Initializes tables and indexes according to Master Spec."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    page_id TEXT NOT NULL,
                    drive_file_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    mime_type TEXT,
                    post_type TEXT,
                    status TEXT NOT NULL,
                    facebook_video_id TEXT,
                    duration_seconds REAL,
                    aspect_ratio TEXT,
                    first_seen_at TEXT NOT NULL,
                    selected_at TEXT,
                    posted_at TEXT,
                    last_attempt_at TEXT,
                    retry_count INTEGER DEFAULT 0,
                    failure_reason TEXT,
                    UNIQUE(page_id, drive_file_id)
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    page_id TEXT NOT NULL,
                    run_id TEXT,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    status TEXT NOT NULL,
                    drive_files_seen INTEGER DEFAULT 0,
                    selected_drive_file_id TEXT,
                    facebook_video_id TEXT,
                    error_message TEXT,
                    runner_ip TEXT,
                    runner_city TEXT,
                    runner_region TEXT,
                    runner_country TEXT,
                    runner_country_code TEXT,
                    runner_org TEXT
                );
            """)

            # Indices for quick lookups and fast queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_page_drive ON videos(page_id, drive_file_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_page_status ON videos(page_id, status);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_posted_at ON videos(posted_at);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_page_status ON runs(page_id, status);")
            conn.commit()

    def is_already_posted(self, page_id: str, drive_file_id: str) -> bool:
        """Checks if a drive file has already been successfully posted to this page."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM videos WHERE page_id = ? AND drive_file_id = ? AND status = 'posted';",
                (page_id, drive_file_id)
            )
            return cursor.fetchone() is not None

    def get_posted_drive_file_ids(self, page_id: str) -> Set[str]:
        """Returns a set of all drive file IDs successfully posted to this page."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT drive_file_id FROM videos WHERE page_id = ? AND status = 'posted';",
                (page_id,)
            )
            return {row["drive_file_id"] for row in cursor.fetchall()}

    def get_permanently_failed_file_ids(self, page_id: str) -> Set[str]:
        """Returns set of drive file IDs that failed permanently and should be skipped."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT drive_file_id FROM videos WHERE page_id = ? AND status = 'failed_permanent';",
                (page_id,)
            )
            return {row["drive_file_id"] for row in cursor.fetchall()}

    def get_today_upload_count(self, page_id: str) -> int:
        """Counts successful posts for today (UTC) for this page to enforce daily limits."""
        today_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) as count FROM videos WHERE page_id = ? AND status = 'posted' AND posted_at LIKE ?;",
                (page_id, f"{today_prefix}%")
            )
            row = cursor.fetchone()
            return int(row["count"]) if row else 0

    def record_selection(
        self,
        page_id: str,
        drive_file_id: str,
        filename: str,
        mime_type: str = ""
    ) -> None:
        """Records that a drive file was picked up by the automation."""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO videos (
                    page_id, drive_file_id, filename, mime_type, status,
                    first_seen_at, selected_at, last_attempt_at, retry_count
                )
                VALUES (?, ?, ?, ?, 'selected', ?, ?, ?, 0)
                ON CONFLICT(page_id, drive_file_id) DO UPDATE SET
                    selected_at = excluded.selected_at,
                    last_attempt_at = excluded.last_attempt_at,
                    filename = excluded.filename;
            """, (page_id, drive_file_id, filename, mime_type, now, now, now))
            conn.commit()

    def record_success(
        self,
        page_id: str,
        drive_file_id: str,
        facebook_video_id: str,
        post_type: str = "reel",
        duration_seconds: Optional[float] = None,
        aspect_ratio: Optional[str] = None
    ) -> None:
        """Records a confirmed successful Facebook post."""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE videos SET
                    status = 'posted',
                    facebook_video_id = ?,
                    post_type = ?,
                    duration_seconds = COALESCE(?, duration_seconds),
                    aspect_ratio = COALESCE(?, aspect_ratio),
                    posted_at = ?,
                    last_attempt_at = ?,
                    failure_reason = NULL
                WHERE page_id = ? AND drive_file_id = ?;
            """, (facebook_video_id, post_type, duration_seconds, aspect_ratio, now, now, page_id, drive_file_id))
            conn.commit()

    def record_failure(
        self,
        page_id: str,
        drive_file_id: str,
        reason: str,
        is_permanent: bool = False
    ) -> None:
        """Records an upload failure with retry count tracking."""
        now = datetime.now(timezone.utc).isoformat()
        status = "failed_permanent" if is_permanent else "failed_retryable"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE videos SET
                    status = ?,
                    last_attempt_at = ?,
                    retry_count = retry_count + 1,
                    failure_reason = ?
                WHERE page_id = ? AND drive_file_id = ?;
            """, (status, now, reason, page_id, drive_file_id))
            conn.commit()

    def start_run(
        self,
        page_id: str,
        run_id: str,
        runner_telemetry: Optional[Dict[str, Any]] = None
    ) -> int:
        """Creates a new run entry in SQLite audit log."""
        now = datetime.now(timezone.utc).isoformat()
        t = runner_telemetry or {}
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO runs (
                    page_id, run_id, started_at, status,
                    runner_ip, runner_city, runner_region,
                    runner_country, runner_country_code, runner_org
                )
                VALUES (?, ?, ?, 'running', ?, ?, ?, ?, ?, ?);
            """, (
                page_id, run_id, now,
                t.get("ip"), t.get("city"), t.get("region"),
                t.get("country"), t.get("country_code"), t.get("org")
            ))
            conn.commit()
            return cursor.lastrowid

    def finish_run(
        self,
        db_run_id: int,
        status: str,
        drive_files_seen: int = 0,
        selected_drive_file_id: Optional[str] = None,
        facebook_video_id: Optional[str] = None,
        error_message: Optional[str] = None,
        runner_telemetry: Optional[Dict[str, Any]] = None
    ) -> None:
        """Updates run audit log upon completion."""
        now = datetime.now(timezone.utc).isoformat()
        t = runner_telemetry or {}
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE runs SET
                    status = ?,
                    finished_at = ?,
                    drive_files_seen = ?,
                    selected_drive_file_id = ?,
                    facebook_video_id = ?,
                    error_message = ?,
                    runner_ip = COALESCE(?, runner_ip),
                    runner_city = COALESCE(?, runner_city),
                    runner_region = COALESCE(?, runner_region),
                    runner_country = COALESCE(?, runner_country),
                    runner_country_code = COALESCE(?, runner_country_code),
                    runner_org = COALESCE(?, runner_org)
                WHERE id = ?;
            """, (
                status, now, drive_files_seen, selected_drive_file_id,
                facebook_video_id, error_message,
                t.get("ip"), t.get("city"), t.get("region"),
                t.get("country"), t.get("country_code"), t.get("org"),
                db_run_id
            ))
            conn.commit()
