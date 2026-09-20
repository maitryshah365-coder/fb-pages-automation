import io
import json
import logging
import os
import time
from typing import List, Dict, Any, Optional, Set
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from src.retry import retry_with_backoff

logger = logging.getLogger("fb_automation")

SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
SUPPORTED_MIME_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/x-m4v",
    "video/webm",
    "video/x-matroska",
    "application/octet-stream"
}


class DriveClient:
    """Google Drive client using dedicated Service Account to read videos."""

    def __init__(self, service_account_json_or_path: str):
        self.service = self._init_service(service_account_json_or_path)

    def _init_service(self, creds_data: str):
        scopes = ["https://www.googleapis.com/auth/drive"]
        if os.path.exists(creds_data):
            credentials = service_account.Credentials.from_service_account_file(creds_data, scopes=scopes)
        else:
            try:
                info = json.loads(creds_data)
                credentials = service_account.Credentials.from_service_account_info(info, scopes=scopes)
            except Exception as e:
                raise ValueError(f"Invalid Google Drive service account credentials: {e}")

        return build("drive", "v3", credentials=credentials, cache_discovery=False)

    def list_folder_videos(self, folder_id: str) -> List[Dict[str, Any]]:
        """Lists video files inside folder ordered by oldest creation time first (FIFO)."""
        query = f"'{folder_id}' in parents and trashed = false"

        def _fetch():
            files = []
            page_token = None
            while True:
                response = self.service.files().list(
                    q=query,
                    spaces="drive",
                    fields="nextPageToken, files(id, name, mimeType, size, createdTime, md5Checksum)",
                    orderBy="createdTime asc",
                    pageToken=page_token,
                    pageSize=100
                ).execute()
                files.extend(response.get("files", []))
                page_token = response.get("nextPageToken")
                if not page_token:
                    break
            return files

        all_files = retry_with_backoff(_fetch, action_name="list_drive_folder_videos")

        video_files = []
        for f in all_files:
            name = f.get("name", "")
            ext = os.path.splitext(name)[1].lower()
            mime = f.get("mimeType", "")
            if ext in SUPPORTED_EXTENSIONS or mime in SUPPORTED_MIME_TYPES:
                video_files.append(f)

        # If empty, check subfolders
        if not video_files:
            for f in all_files:
                if f.get("mimeType") == "application/vnd.google-apps.folder":
                    sub_vids = self.list_folder_videos(f["id"])
                    video_files.extend(sub_vids)

        return video_files

    def select_next_video(
        self,
        folder_id: str,
        posted_ids: Set[str],
        permanent_failed_ids: Set[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Selects the next eligible unposted video using FIFO ordering.
        Returns None if no unposted video is found.
        """
        videos = self.list_folder_videos(folder_id)
        for video in videos:
            v_id = video["id"]
            if v_id in posted_ids:
                continue
            if v_id in permanent_failed_ids:
                logger.warning(f"Skipping permanently failed video: {video.get('name')} ({v_id})")
                continue
            # Skip empty or wiped files (0 bytes)
            v_size = int(video.get("size") or 0)
            if v_size == 0:
                logger.warning(f"Skipping 0-byte / wiped video: {video.get('name')} ({v_id})")
                continue
            return video
        return None

    def download_file(self, file_id: str, destination_path: str) -> str:
        """Downloads a video file chunk-by-chunk to the local destination and validates stability."""
        os.makedirs(os.path.dirname(os.path.abspath(destination_path)), exist_ok=True)

        def _download():
            request = self.service.files().get_media(fileId=file_id)
            with io.FileIO(destination_path, "wb") as fh:
                downloader = MediaIoBaseDownload(fh, request, chunksize=10 * 1024 * 1024)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        logger.info(f"Downloading Drive file {file_id}: {progress}%")

        retry_with_backoff(_download, action_name=f"download_drive_file_{file_id}")

        if not os.path.exists(destination_path):
            raise FileNotFoundError(f"Downloaded file not found at: {destination_path}")

        initial_size = os.path.getsize(destination_path)
        if initial_size == 0:
            raise ValueError(f"Downloaded file is empty (0 bytes): {destination_path}")

        # Section 22: verify file sync stability
        time.sleep(1.0)
        final_size = os.path.getsize(destination_path)
        if initial_size != final_size:
            raise ValueError(f"File size unstable during sync validation: {initial_size} != {final_size}")

        logger.info(f"Successfully downloaded and validated file: {destination_path} ({final_size} bytes)")
        return destination_path

    def delete_video(self, file_id: str) -> bool:
        """Permanently deletes video from Google Drive after successful post.
        1. Checks for Owner OAuth credentials (GDRIVE_OWNER_REFRESH_TOKEN / gdrive_owner.token)
           for true, permanent quota-reclaiming deletion.
        2. Falls back to Service Account delete/trash.
        3. As safe fallback, zeroes out file content to 0 bytes to protect cloud storage quota.
        """
        def _del():
            # 1. Attempt Owner OAuth permanent deletion (The bulletproof method for personal Google Drive)
            owner_token = (
                os.environ.get("GDRIVE_OWNER_REFRESH_TOKEN") or
                (open("gdrive_owner.token", encoding="utf-8").read().strip() if os.path.exists("gdrive_owner.token") else None)
            )
            owner_secret_data = os.environ.get("GDRIVE_CLIENT_SECRET_JSON")
            if not owner_secret_data:
                for candidate in ["client_secret.json", os.path.join(os.path.dirname(__file__), "..", "client_secret.json")]:
                    if os.path.exists(candidate):
                        owner_secret_data = candidate
                        break

            if owner_token and owner_secret_data:
                try:
                    from google.oauth2.credentials import Credentials
                    secret_info = json.loads(owner_secret_data) if "{" in owner_secret_data else json.load(open(owner_secret_data, encoding="utf-8"))
                    installed = secret_info.get("installed") or secret_info.get("web", secret_info)
                    creds = Credentials(
                        None,
                        refresh_token=owner_token,
                        token_uri="https://oauth2.googleapis.com/token",
                        client_id=installed["client_id"],
                        client_secret=installed["client_secret"],
                        scopes=["https://www.googleapis.com/auth/drive"]
                    )
                    owner_service = build("drive", "v3", credentials=creds, cache_discovery=False)
                    owner_service.files().delete(fileId=file_id).execute()
                    logger.info(f"PERMANENTLY DELETED Google Drive video file via Owner OAuth: {file_id}")
                    return True
                except Exception as owner_err:
                    logger.warning(f"Owner OAuth delete failed ({owner_err}), trying service account methods...")

            # 2. Permanent Hard Delete via Service Account (Works on Shared Drives or files owned by SA)
            try:
                self.service.files().delete(fileId=file_id, supportsAllDrives=True).execute()
                logger.info(f"PERMANENTLY DELETED Google Drive video file via Service Account: {file_id}")
                return True
            except Exception as e:
                logger.warning(f"Direct Service Account delete failed for {file_id} ({e}), trying Trash...")
                try:
                    # 3. If direct hard-delete blocked, attempt moving to Trash
                    self.service.files().update(fileId=file_id, body={"trashed": True}, supportsAllDrives=True).execute()
                    logger.info(f"Moved Google Drive video file {file_id} to Trash.")
                    return True
                except Exception as trash_err:
                    logger.warning(f"Move to trash blocked for {file_id} ({trash_err}), wiping content to 0 bytes...")
                    try:
                        from googleapiclient.http import MediaInMemoryUpload
                        # 4. Zero-out file content to free 100% cloud storage (safe mode)
                        media = MediaInMemoryUpload(b"", mimetype="application/octet-stream")
                        self.service.files().update(fileId=file_id, media_body=media, supportsAllDrives=True).execute()
                        logger.info(f"Successfully wiped video content to 0 bytes for: {file_id}")
                        return True
                    except Exception as wipe_err:
                        logger.error(f"Failed all deletion methods for {file_id}: {wipe_err}")
                        raise wipe_err

        return retry_with_backoff(_del, action_name=f"delete_drive_file_{file_id}")


