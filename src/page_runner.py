import os
import shutil
import tempfile
import uuid
import logging
from typing import Dict, Any, Optional
from src.config import PageConfig, AppConfig
from src.db import DatabaseManager
from src.drive_client import DriveClient
from src.video_utils import inspect_video, determine_post_route
from src.facebook_client import FacebookClient
from src.notifier import DiscordNotifier

logger = logging.getLogger("fb_automation")


def build_caption(page: PageConfig, filename: str) -> str:
    """Constructs caption/title based on configuration rules."""
    base_name = os.path.splitext(filename)[0]
    if page.title_mode == "fixed" and page.fixed_title:
        title = page.fixed_title
    else:
        title = base_name

    parts = [title]
    if page.description_footer:
        parts.append(page.description_footer)

    if page.default_hashtags:
        tags_str = " ".join(
            tag if tag.startswith("#") else f"#{tag}" for tag in page.default_hashtags
        )
        parts.append(tags_str)

    return "\n\n".join(parts).strip()


class PageRunner:
    """Executes the automated posting pipeline for Facebook Pages."""

    def __init__(
        self,
        config: AppConfig,
        db: DatabaseManager,
        drive_client: DriveClient,
        notifier: DiscordNotifier,
        dry_run: bool = False,
        runner_telemetry: Optional[Dict[str, Any]] = None
    ):
        self.config = config
        self.db = db
        self.drive_client = drive_client
        self.notifier = notifier
        self.dry_run = dry_run
        self.runner_telemetry = runner_telemetry or {}

    def run_page(self, page: PageConfig) -> Dict[str, Any]:
        """
        Executes pipeline for a single Facebook Page.
        Guarantees isolation: Errors here will be logged and recorded, but won't crash callers.
        """
        page_id = page.page_id
        page_name = page.name
        run_uuid = str(uuid.uuid4())

        logger.info(f"--- Processing Page: {page_name} (ID: {page_id}, Dry-Run: {self.dry_run}) ---")

        if not page.enabled:
            logger.info(f"[{page_name}] Page is disabled in configuration. Skipping.")
            return {"status": "skipped", "page": page_name, "reason": "disabled"}

        db_run_id = self.db.start_run(page_id, run_id=run_uuid, runner_telemetry=self.runner_telemetry)

        # 1. Enforce daily limit guard
        today_posts = self.db.get_today_upload_count(page_id)
        if today_posts >= page.daily_limit:
            msg = f"Daily limit reached ({today_posts}/{page.daily_limit} posts today). Skipping."
            logger.info(f"[{page_name}] {msg}")
            self.db.finish_run(db_run_id, status="skipped", error_message=msg, runner_telemetry=self.runner_telemetry)
            return {"status": "skipped", "page": page_name, "reason": msg}

        # 2. Resolve Page Access Token
        access_token = page.get_access_token()
        if not access_token and not self.dry_run:
            err = f"Missing Page Access Token (expected env var {page.token_env_var} or FB_PAGE_ACCESS_TOKEN)."
            logger.error(f"[{page_name}] {err}")
            self.db.finish_run(db_run_id, status="failed", error_message=err, runner_telemetry=self.runner_telemetry)
            self.notifier.send_failure(page_name, None, err)
            return {"status": "failed", "page": page_name, "error": err}

        # 3. Find next unposted video in Drive
        if not page.drive_folder_id or "REPLACE" in page.drive_folder_id:
            err = "Google Drive folder ID not configured."
            logger.error(f"[{page_name}] {err}")
            self.db.finish_run(db_run_id, status="failed", error_message=err, runner_telemetry=self.runner_telemetry)
            return {"status": "failed", "page": page_name, "error": err}

        posted_ids = self.db.get_posted_drive_file_ids(page_id)
        permanent_failed_ids = self.db.get_permanently_failed_file_ids(page_id)

        try:
            all_videos = self.drive_client.list_folder_videos(page.drive_folder_id)
            total_seen = len(all_videos)
            selected_video = self.drive_client.select_next_video(
                page.drive_folder_id, posted_ids, permanent_failed_ids
            )
        except Exception as e:
            err = f"Failed to list or select files from Drive: {e}"
            logger.error(f"[{page_name}] {err}")
            self.db.finish_run(db_run_id, status="failed", error_message=err, runner_telemetry=self.runner_telemetry)
            self.notifier.send_failure(page_name, None, err)
            return {"status": "failed", "page": page_name, "error": err}

        if not selected_video:
            logger.info(f"[{page_name}] No unposted video found in Drive folder (Seen {total_seen} files).")
            self.db.finish_run(
                db_run_id, status="no_content", drive_files_seen=total_seen,
                runner_telemetry=self.runner_telemetry
            )
            return {"status": "no_content", "page": page_name, "drive_files_seen": total_seen}

        drive_file_id = selected_video["id"]
        filename = selected_video.get("name", "video.mp4")
        mime_type = selected_video.get("mimeType", "video/mp4")

        logger.info(f"[{page_name}] Selected unposted file: '{filename}' (ID: {drive_file_id})")

        # 4. Duplicate Guard (Double check)
        if self.db.is_already_posted(page_id, drive_file_id):
            logger.warning(f"[{page_name}] File {drive_file_id} already marked posted in SQLite. Skipping.")
            self.db.finish_run(
                db_run_id, status="skipped", selected_drive_file_id=drive_file_id,
                runner_telemetry=self.runner_telemetry
            )
            return {"status": "skipped", "page": page_name, "reason": "already_posted"}

        if not self.dry_run:
            self.db.record_selection(page_id, drive_file_id, filename, mime_type)

        caption = build_caption(page, filename)

        # 5. Dry-Run Mode Intercept (Section 13 & Test A)
        if self.dry_run:
            logger.info("================ DRY RUN SUMMARY ================")
            logger.info(f"Page Name: {page_name} (ID: {page_id})")
            logger.info(f"Drive File: {filename} (ID: {drive_file_id})")
            logger.info(f"MIME Type: {mime_type}")
            logger.info(f"Caption / Description:\n{caption}")
            logger.info(f"Estimated Route: Reels (3-90s 9:16) or Classic Video (>90s)")
            logger.info("Would Publish: YES")
            logger.info("Actual Publish: NO (Dry-Run Mode Active)")
            logger.info("=================================================")
            self.db.finish_run(
                db_run_id, status="dry_run", drive_files_seen=total_seen,
                selected_drive_file_id=drive_file_id, runner_telemetry=self.runner_telemetry
            )
            return {
                "status": "dry_run_success",
                "page": page_name,
                "file": filename,
                "drive_file_id": drive_file_id
            }

        # 6. Download Video to temporary runner storage
        temp_dir = tempfile.mkdtemp(prefix=f"fb_post_{page_name}_")
        temp_file_path = os.path.join(temp_dir, filename)

        try:
            self.drive_client.download_file(drive_file_id, temp_file_path)

            # 7. File Validation & Video Route Detection (Section 9 & 22)
            video_info = inspect_video(temp_file_path)
            post_route = determine_post_route(video_info)
            duration = video_info.get("duration_seconds")
            aspect_ratio_str = video_info.get("aspect_ratio_str")

            logger.info(
                f"[{page_name}] Video inspection: Duration={duration:.1f}s, Dimensions={aspect_ratio_str}, "
                f"Chosen Route: {post_route.upper()}"
            )

            # 8. Facebook Graph API Client Initialization
            fb_client = FacebookClient(page_access_token=access_token)

            # 9. Publish based on detected route
            if post_route == "reel":
                fb_video_id = fb_client.publish_reel(
                    page_id=page_id,
                    video_path=temp_file_path,
                    caption=caption,
                    max_retries=self.config.retry.max_attempts
                )
            else:
                fb_video_id = fb_client.publish_classic_video(
                    page_id=page_id,
                    video_path=temp_file_path,
                    title=os.path.splitext(filename)[0],
                    description=caption,
                    max_retries=self.config.retry.max_attempts
                )

            # 10. Record Success in DB (Section 15: Commit safety)
            self.db.record_success(
                page_id=page_id,
                drive_file_id=drive_file_id,
                facebook_video_id=fb_video_id,
                post_type=post_route,
                duration_seconds=duration,
                aspect_ratio=aspect_ratio_str
            )

            self.db.finish_run(
                db_run_id,
                status="success",
                drive_files_seen=total_seen,
                selected_drive_file_id=drive_file_id,
                facebook_video_id=fb_video_id,
                runner_telemetry=self.runner_telemetry
            )

            # 11. Permanently delete video from Google Drive if configured
            if getattr(self.config, "delete_after_post", True) and not self.dry_run:
                try:
                    logger.info(f"[{page_name}] Permanently deleting video from Google Drive after successful post: {drive_file_id}")
                    self.drive_client.delete_video(drive_file_id)
                except Exception as del_err:
                    logger.warning(f"[{page_name}] Failed to delete video from Drive ({drive_file_id}): {del_err}")

            # 12. Send notification
            self.notifier.send_success(page_name, filename, fb_video_id, post_type=post_route)
            logger.info(f"[{page_name}] Post completed successfully! Video ID: {fb_video_id}")

            return {
                "status": "success",
                "page": page_name,
                "drive_file_id": drive_file_id,
                "facebook_video_id": fb_video_id,
                "filename": filename,
                "post_type": post_route
            }

        except Exception as e:
            err_msg = str(e)
            logger.error(f"[{page_name}] Post failed: {err_msg}", exc_info=True)
            self.db.record_failure(page_id, drive_file_id, reason=err_msg, is_permanent=False)
            self.db.finish_run(
                db_run_id,
                status="failed",
                drive_files_seen=total_seen,
                selected_drive_file_id=drive_file_id,
                error_message=err_msg,
                runner_telemetry=self.runner_telemetry
            )
            self.notifier.send_failure(page_name, filename, err_msg)
            return {"status": "failed", "page": page_name, "error": err_msg}

        finally:
            # Rule 10 & 13: Clean temporary runner storage; do NOT delete Drive source file
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info(f"[{page_name}] Cleaned temporary runner directory.")
