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
        """Permanently deletes or wipes video from Google Drive after successful post.
        1. Attempts direct permanent hard-delete.
        2. If blocked by ownership, attempts moving to Trash.
        3. If trash is blocked (shared personal Drive), zeroes out content to 0 bytes
           (freeing cloud storage) and removes parent folders so file disappears from Drive.
        """
        def _del():
            try:
                # 1. Permanent Hard Delete (Completely removes file from Google Drive)
                self.service.files().delete(fileId=file_id, supportsAllDrives=True).execute()
                logger.info(f"PERMANENTLY DELETED Google Drive video file: {file_id}")
                return True
            except Exception as e:
                logger.warning(f"Direct permanent delete failed for {file_id} ({e}), trying Trash...")
                try:
                    # 2. If direct hard-delete blocked by personal drive ownership, move to Trash
                    self.service.files().update(fileId=file_id, body={"trashed": True}, supportsAllDrives=True).execute()
                    logger.info(f"Moved Google Drive video file {file_id} to Trash.")
                    return True
                except Exception as trash_err:
                    logger.warning(f"Move to trash blocked for {file_id} ({trash_err}), wiping content & unlinking parents...")
                    try:
                        from googleapiclient.http import MediaInMemoryUpload
                        # 3a. Zero-out file content to free 100% cloud storage
                        media = MediaInMemoryUpload(b"", mimetype="application/octet-stream")
                        self.service.files().update(fileId=file_id, media_body=media, supportsAllDrives=True).execute()

                        # 3b. Remove from parent folders so it disappears from user's Drive folder
                        f = self.service.files().get(fileId=file_id, fields="parents", supportsAllDrives=True).execute()
                        parents = f.get("parents", [])
                        if parents:
                            self.service.files().update(
                                fileId=file_id,
                                removeParents=",".join(parents),
                                supportsAllDrives=True
                            ).execute()
                        logger.info(f"Successfully wiped content to 0 bytes and removed parents for: {file_id}")
                        return True
                    except Exception as wipe_err:
                        logger.error(f"Failed all deletion methods for {file_id}: {wipe_err}")
                        raise wipe_err

        return retry_with_backoff(_del, action_name=f"delete_drive_file_{file_id}")

