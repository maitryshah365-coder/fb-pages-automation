"""
Autonomous 24/7 Pipeline Runner for USA Account 5 (Sejal Soni - Google Pixel 9 Pro)
Fetches video stock from Google Drive, invokes Anti-Detect Mobile Playwright Reels Composer,
and records publishing history into posted_videos.db without any Facebook tokens.
"""

import os
import sys
import json
import time
import random
import argparse
import sqlite3
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.anti_detect.device_profiles import PIXEL9_NEWYORK_PROFILE
from src.anti_detect.reels_uploader import AntiDetectReelsUploader
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

PAGES_CONFIG_PATH = os.path.join(BASE_DIR, "data", "usa_account5_sejal_permanent_pages.json")
COOKIES_PATH = os.path.join(BASE_DIR, "data", "profiles", "google_pixel9_newyork", "cookies.json")
DB_PATH = os.path.join(BASE_DIR, "data", "posted_videos.db")
TEMP_DIR = os.path.join(BASE_DIR, "temp", "sejal_pixel9")


def ensure_cookies():
    """Ensure cookie file exists, restoring from environment if necessary."""
    if os.path.exists(COOKIES_PATH) and os.path.getsize(COOKIES_PATH) > 10:
        return True

    env_cookies = os.environ.get("SEJAL_PIXEL9_COOKIES_JSON")
    if env_cookies:
        os.makedirs(os.path.dirname(COOKIES_PATH), exist_ok=True)
        with open(COOKIES_PATH, "w", encoding="utf-8") as f:
            f.write(env_cookies)
        print("Restored Sejal Soni cookies from environment variable.")
        return True

    print("Warning: Sejal Soni cookies.json not found.")
    return False


def get_gdrive_service():
    """Initialize Google Drive API service client."""
    creds_json = os.environ.get("GDRIVE_SERVICE_ACCOUNT_JSON")
    sa_path = os.path.join(BASE_DIR, "service_account.json")

    if creds_json:
        try:
            info = json.loads(creds_json)
            creds = service_account.Credentials.from_service_account_info(
                info, scopes=["https://www.googleapis.com/auth/drive.readonly"]
            )
            return build("drive", "v3", credentials=creds)
        except Exception as e:
            print(f"Error initializing Drive credentials from env: {e}")

    if os.path.exists(sa_path):
        try:
            creds = service_account.Credentials.from_service_account_file(
                sa_path, scopes=["https://www.googleapis.com/auth/drive.readonly"]
            )
            return build("drive", "v3", credentials=creds)
        except Exception as e:
            print(f"Error initializing Drive credentials from file: {e}")

    return None


def get_posted_file_names(page_id: str) -> set:
    """Query DB for already posted video names for this page."""
    posted = set()
    if not os.path.exists(DB_PATH):
        return posted
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        try:
            cur.execute("SELECT filename FROM videos WHERE (page_id = ? OR page_id LIKE ?) AND status = 'posted'", (page_id, f"%{page_id}%"))
            for r in cur.fetchall():
                if r[0]:
                    posted.add(r[0])
        except Exception:
            pass
        conn.close()
    except Exception as e:
        print(f"DB check warning: {e}")
    return posted


def download_next_reel(drive_service, folder_id: str, page_id: str) -> tuple:
    """Download the next unposted video file from Google Drive."""
    if not drive_service:
        return None, None, None

    os.makedirs(TEMP_DIR, exist_ok=True)
    posted_names = get_posted_file_names(page_id)

    query = f"'{folder_id}' in parents and mimeType contains 'video/' and trashed = false"
    res = drive_service.files().list(
        q=query,
        fields="files(id, name, size, createdTime)",
        pageSize=100,
        orderBy="createdTime"
    ).execute()
    files = res.get("files", [])

    candidate = None
    for f in files:
        if f["name"] not in posted_names:
            candidate = f
            break

    if not candidate:
        print(f"   No unposted videos found in folder {folder_id}")
        return None, None, None

    file_id = candidate["id"]
    file_name = candidate["name"]
    local_path = os.path.join(TEMP_DIR, f"{page_id}_{file_name}")

    if not os.path.exists(local_path):
        print(f"   Downloading: {file_name} ({round(int(candidate.get('size', 0))/(1024*1024), 2)} MB)...")
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.FileIO(local_path, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.close()
        print(f"   Downloaded to: {local_path}")

    return local_path, file_name, file_id


def record_successful_upload(page_id: str, page_name: str, file_name: str, drive_file_id: str = ""):
    """Save upload record to posted_videos.db."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        file_id_val = drive_file_id or f"sejal_drive_{int(time.time())}"
        cur.execute("""
            INSERT INTO videos (page_id, drive_file_id, filename, mime_type, post_type, status, first_seen_at, posted_at)
            VALUES (?, ?, ?, 'video/mp4', 'reel', 'posted', ?, ?)
        """, (page_id, file_id_val, file_name, now, now))
        conn.commit()
        conn.close()
        print(f"   [DB] Recorded '{file_name}' for {page_name} in videos table.")
    except Exception as e:
        print(f"Failed to record in videos: {e}")


def main():
    parser = argparse.ArgumentParser(description="Sejal Soni Pixel 9 Pro Automated Pipeline Runner")
    parser.add_argument("--page", help="Optional specific page name or ID")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without clicking publish")
    parser.add_argument("--headed", action="store_true", help="Run browser in visible mode")
    parser.add_argument("--limit", type=int, default=15, help="Max pages to process in this run")
    args = parser.parse_args()

    ensure_cookies()

    if not os.path.exists(PAGES_CONFIG_PATH):
        print(f"Error: {PAGES_CONFIG_PATH} does not exist.")
        return

    with open(PAGES_CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    pages = config.get("pages", [])
    if args.page:
        pages = [p for p in pages if args.page.lower() in p["name"].lower() or args.page == p["id"] or args.page == p.get("page_id")]

    pages = pages[:args.limit]
    print(f"\n=======================================================")
    print(f"🚀 SEJAL SONI GOOGLE PIXEL 9 PRO 24/7 REELS PIPELINE")
    print(f"   Total Pages Target: {len(pages)}")
    print(f"   Dry Run:            {args.dry_run}")
    print(f"   Timezone Profile:   America/New_York (Google Pixel 9 Pro)")
    print(f"=======================================================\n")

    drive_service = get_gdrive_service()
    results = []

    for idx, page in enumerate(pages, 1):
        p_name = page["name"]
        p_id = page["id"]
        real_page_id = page.get("page_id", p_id)
        folder_id = page.get("drive_folder_id")

        print(f"\n[{idx}/{len(pages)}] Processing: {p_name} (Page ID: {real_page_id})")

        # 1. Acquire Video
        video_path = None
        file_name = None
        drive_file_id = None
        if drive_service and folder_id:
            video_path, file_name, drive_file_id = download_next_reel(drive_service, folder_id, real_page_id)

        if not video_path or not os.path.exists(video_path):
            if args.dry_run:
                print("   Creating dummy test video for dry-run...")
                dummy_path = os.path.join(TEMP_DIR, "test_pixel9_reel.mp4")
                os.makedirs(TEMP_DIR, exist_ok=True)
                if not os.path.exists(dummy_path):
                    import subprocess
                    subprocess.run([
                        "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=1080x1920:d=3",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", dummy_path
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                video_path = dummy_path
                file_name = "test_pixel9_reel.mp4"
                drive_file_id = "test_pixel9_drive_id"
            else:
                print(f"   Skipping {p_name}: No video available to post.")
                continue

        # 2. Upload Reel via Anti-Detect Playwright
        uploader = AntiDetectReelsUploader(profile=PIXEL9_NEWYORK_PROFILE, asset_id=real_page_id)
        caption = f"Stay inspired ✨ #viral #reels #trending #fyp #{p_name.replace(' ', '')}"

        res = uploader.upload_reel(
            video_path=video_path,
            caption=caption,
            page_name=p_name,
            asset_id=real_page_id,
            headless=not args.headed,
            dry_run=args.dry_run
        )
        results.append({"page": p_name, "status": res.get("status"), "result": res})

        if res.get("status") == "success" and not args.dry_run:
            record_successful_upload(real_page_id, p_name, file_name, drive_file_id)

        # Clean up downloaded temp file
        if video_path and os.path.exists(video_path) and "test_pixel9_reel" not in video_path:
            try:
                os.remove(video_path)
            except Exception:
                pass

        # Humanized delay between consecutive page postings
        if idx < len(pages):
            sleep_sec = random.uniform(35.0, 65.0)
            print(f"   Natural pacing delay: sleeping {round(sleep_sec, 1)}s before next page...")
            time.sleep(sleep_sec)

    print("\n=======================================================")
    print("🏁 PIPELINE RUN COMPLETE")
    print(f"   Processed: {len(results)} pages")
    print("=======================================================\n")


if __name__ == "__main__":
    main()
