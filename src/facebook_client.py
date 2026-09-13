import os
import time
import json
import logging
import requests
from typing import Dict, Any, Optional
from src.retry import retry_with_backoff, PermanentError, RetryableError

logger = logging.getLogger("fb_automation")

DEFAULT_GRAPH_API_VERSION = "v20.0"
BASE_GRAPH_URL = f"https://graph.facebook.com/{DEFAULT_GRAPH_API_VERSION}"


class FacebookClient:
    """Handles publishing to Facebook Pages via Graph API (Reels & Classic Video)."""

    def __init__(self, page_access_token: str, api_version: str = DEFAULT_GRAPH_API_VERSION):
        if not page_access_token:
            raise ValueError("Facebook Page Access Token is required.")
        self.page_access_token = page_access_token
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{api_version}"

    def _handle_api_error(self, response: requests.Response, context: str) -> None:
        """Parses Facebook API error structure and classifies into Permanent or Retryable."""
        try:
            err_data = response.json().get("error", {})
        except Exception:
            err_data = {}

        code = err_data.get("code")
        subcode = err_data.get("error_subcode")
        message = err_data.get("message", response.text)
        err_type = err_data.get("type", "Unknown")

        error_summary = f"[{context}] Graph API Error {code} (subcode: {subcode}, type: {err_type}): {message}"

        # Rate limits & transient 5xx errors -> Retryable
        if response.status_code in [429, 500, 502, 503, 504] or code in [4, 17, 32, 613]:
            raise RetryableError(error_summary)

        # Invalid token / permissions / auth revoked -> Permanent
        if code in [190, 10, 200] or response.status_code in [401, 403]:
            raise PermanentError(f"Authentication/Permission error: {error_summary}")

        # Invalid file / payload
        if response.status_code == 400:
            raise PermanentError(f"Bad Request: {error_summary}")

        # Default fallback
        raise RetryableError(error_summary)

    # ----------------------------------------------------------------------
    # Reels Publishing Flow (Primary Path for 9:16, 3-90s)
    # ----------------------------------------------------------------------
    def publish_reel(
        self,
        page_id: str,
        video_path: str,
        caption: str,
        max_retries: int = 3
    ) -> str:
        """
        Publishes a video to Facebook Reels using the 3-step Resumable Reels API:
        1. Initialize session -> video_id, upload_url
        2. Upload binary video stream to upload_url
        3. Finish session -> video_state=PUBLISHED
        """
        file_size = os.path.getsize(video_path)
        logger.info(f"[{page_id}] Starting Reels upload for {os.path.basename(video_path)} ({file_size} bytes)...")

        # Step 1: Start
        def _start_session():
            url = f"{self.base_url}/{page_id}/video_reels"
            payload = {
                "upload_phase": "start",
                "access_token": self.page_access_token
            }
            res = requests.post(url, data=payload, timeout=30)
            if not res.ok:
                self._handle_api_error(res, "Reels Start Phase")
            data = res.json()
            video_id = data.get("video_id")
            upload_url = data.get("upload_url")
            if not video_id or not upload_url:
                raise RetryableError(f"Incomplete start response: {res.text}")
            return video_id, upload_url

        video_id, upload_url = retry_with_backoff(_start_session, max_attempts=max_retries, action_name="reels_start")
        logger.info(f"[{page_id}] Reels session initialized. Video ID: {video_id}")

        # Step 2: Upload bytes
        def _upload_bytes():
            with open(video_path, "rb") as fh:
                headers = {
                    "Authorization": f"OAuth {self.page_access_token}",
                    "offset": "0",
                    "file_size": str(file_size)
                }
                res = requests.post(upload_url, data=fh, headers=headers, timeout=180)
                if not res.ok:
                    self._handle_api_error(res, "Reels Upload Bytes Phase")
                return res.json()

        retry_with_backoff(_upload_bytes, max_attempts=max_retries, action_name="reels_upload_bytes")
        logger.info(f"[{page_id}] Reels video bytes uploaded successfully.")

        # Step 3: Finish and Publish
        def _finish_session():
            url = f"{self.base_url}/{page_id}/video_reels"
            payload = {
                "upload_phase": "finish",
                "video_id": video_id,
                "video_state": "PUBLISHED",
                "description": caption,
                "access_token": self.page_access_token
            }
            res = requests.post(url, data=payload, timeout=30)
            if not res.ok:
                self._handle_api_error(res, "Reels Finish Phase")
            data = res.json()
            if not data.get("success", True):
                raise RetryableError(f"Reels publish did not return success: {res.text}")
            return video_id

        published_video_id = retry_with_backoff(_finish_session, max_attempts=max_retries, action_name="reels_finish")
        logger.info(f"[{page_id}] Reel successfully published! Video ID: {published_video_id}")
        return published_video_id

    # ----------------------------------------------------------------------
    # Classic Video Flow (Fallback Path for >90s or non-9:16)
    # ----------------------------------------------------------------------
    def publish_classic_video(
        self,
        page_id: str,
        video_path: str,
        title: str,
        description: str,
        max_retries: int = 3
    ) -> str:
        """
        Publishes a video to Facebook Page via Classic /videos endpoint.
        Uses Resumable chunked upload for robust handling of large videos (5-7 minutes).
        """
        file_size = os.path.getsize(video_path)
        logger.info(f"[{page_id}] Starting Classic Video upload for {os.path.basename(video_path)} ({file_size} bytes)...")

        # Step 1: Start Resumable Upload
        def _start():
            url = f"{self.base_url}/{page_id}/videos"
            payload = {
                "upload_phase": "start",
                "file_size": file_size,
                "access_token": self.page_access_token
            }
            res = requests.post(url, data=payload, timeout=30)
            if not res.ok:
                self._handle_api_error(res, "Classic Video Start Phase")
            data = res.json()
            session_id = data.get("upload_session_id")
            video_id = data.get("video_id")
            if not session_id:
                raise RetryableError(f"Failed to obtain upload_session_id: {res.text}")
            return session_id, video_id

        session_id, video_id = retry_with_backoff(_start, max_attempts=max_retries, action_name="classic_video_start")
        logger.info(f"[{page_id}] Classic Video session started: {session_id}")

        # Step 2: Transfer Chunks
        chunk_size = 10 * 1024 * 1024  # 10MB chunks
        start_offset = 0

        with open(video_path, "rb") as fh:
            while start_offset < file_size:
                fh.seek(start_offset)
                chunk_data = fh.read(chunk_size)
                current_start = start_offset

                def _transfer(offset=current_start, data=chunk_data):
                    url = f"{self.base_url}/{page_id}/videos"
                    files = {"video_file_chunk": ("chunk", data, "application/octet-stream")}
                    payload = {
                        "upload_phase": "transfer",
                        "upload_session_id": session_id,
                        "start_offset": offset,
                        "access_token": self.page_access_token
                    }
                    res = requests.post(url, data=payload, files=files, timeout=120)
                    if not res.ok:
                        self._handle_api_error(res, f"Classic Video Transfer Offset {offset}")
                    return res.json()

                transfer_res = retry_with_backoff(_transfer, max_attempts=max_retries, action_name=f"classic_transfer_{start_offset}")
                next_start = transfer_res.get("start_offset")
                next_end = transfer_res.get("end_offset")

                if next_start is not None and next_end is not None and int(next_start) == int(next_end):
                    logger.info(f"[{page_id}] All video chunks transferred.")
                    break
                elif next_start is not None:
                    start_offset = int(next_start)
                else:
                    start_offset += len(chunk_data)

        # Step 3: Finish and Publish
        def _finish():
            url = f"{self.base_url}/{page_id}/videos"
            payload = {
                "upload_phase": "finish",
                "upload_session_id": session_id,
                "title": title,
                "description": description,
                "access_token": self.page_access_token
            }
            res = requests.post(url, data=payload, timeout=30)
            if not res.ok:
                self._handle_api_error(res, "Classic Video Finish Phase")
            data = res.json()
            if not data.get("success", True):
                raise RetryableError(f"Classic video publish did not return success: {res.text}")
            return video_id or data.get("id")

        final_video_id = retry_with_backoff(_finish, max_attempts=max_retries, action_name="classic_video_finish")
        logger.info(f"[{page_id}] Classic Video successfully published! Video ID: {final_video_id}")
        return str(final_video_id)

    # ----------------------------------------------------------------------
    # Section 16: Verification & Ambiguous Failure Recovery
    # ----------------------------------------------------------------------
    def check_recent_posts(self, page_id: str, limit: int = 5) -> list:
        """Retrieves recent published videos on the Page to check for ambiguous posts."""
        url = f"{self.base_url}/{page_id}/videos"
        params = {
            "fields": "id,title,description,created_time",
            "limit": limit,
            "access_token": self.page_access_token
        }
        res = requests.get(url, params=params, timeout=20)
        if res.ok:
            return res.json().get("data", [])
        return []
