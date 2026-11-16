#!/usr/bin/env python3
"""
scripts/post_torres_image.py
=============================================================================
Automated Image Upload Engine for Page: Torres Matthew (ID: 883354574851891)
- Account: USA Account 9 (Prince Shah)
- Strict Server-to-Server Meta Graph API v20.0
- SQLite tracking to prevent duplicate image posting
- Supports Google Drive image folder fetching and direct file posting
=============================================================================
"""

import os
import sys
import yaml
import json
import sqlite3
import logging
import argparse
import requests
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.drive_client import DriveClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("torres_image_uploader")

CONFIG_PATH = os.path.join(BASE_DIR, "config_usa_account9.yaml")
DB_PATH = os.path.join(BASE_DIR, "data", "posted_videos.db")
TARGET_PAGE_ID = "883354574851891"
TARGET_PAGE_NAME = "Torres  Matthew"

# Default culinary & pasta viral hashtags for Torres Matthew
DEFAULT_HASHTAGS = [
    "#pasta", "#italianfood", "#pastalover", "#foodporn", 
    "#homemade", "#pastarecipe", "#foodie", "#instafood", "#chef"
]

def init_photos_db(conn: sqlite3.Connection):
    """Ensures posted_photos tracking table exists."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posted_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_id TEXT NOT NULL,
            page_name TEXT NOT NULL,
            drive_file_id TEXT UNIQUE,
            filename TEXT NOT NULL,
            caption TEXT,
            fb_photo_id TEXT UNIQUE,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            error_message TEXT
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_photos_page ON posted_photos(page_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_photos_drive ON posted_photos(drive_file_id);")
    conn.commit()

def load_page_config() -> Dict[str, Any]:
    """Loads Torres Matthew configuration from config_usa_account9.yaml."""
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")
    
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
        
    for p in cfg.get("pages", []):
        if str(p.get("page_id")) == TARGET_PAGE_ID or "torres" in p.get("display_name", "").lower():
            return {
                "page_id": str(p["page_id"]),
                "display_name": p.get("display_name", TARGET_PAGE_NAME),
                "page_access_token": p.get("page_access_token"),
                "drive_folder_id": p.get("image_drive_folder_id") or p.get("drive_folder_id"),
                "service_account_json": cfg.get("google_service_account_json", "service_account.json"),
                "hashtags": p.get("default_hashtags") or DEFAULT_HASHTAGS
            }
            
    raise ValueError(f"Page {TARGET_PAGE_ID} ({TARGET_PAGE_NAME}) not found in {CONFIG_PATH}")

def get_already_posted_file_ids(conn: sqlite3.Connection) -> set:
    """Returns set of drive_file_ids already posted to Facebook."""
    cursor = conn.cursor()
    cursor.execute("SELECT drive_file_id FROM posted_photos WHERE page_id = ? AND status = 'posted'", (TARGET_PAGE_ID,))
    return {row[0] for row in cursor.fetchall() if row[0]}

def find_next_image_in_drive(drive_client: DriveClient, folder_id: str, posted_ids: set) -> Optional[Dict[str, Any]]:
    """Finds next unposted image (.jpg, .jpeg, .png, .webp) in Drive folder or subfolder."""
    logger.info(f"Scanning Drive folder {folder_id} for image files...")
    
    # 1. First check if a dedicated subfolder named 'Images' or 'Photos' exists
    subfolders_query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    sub_res = drive_client.service.files().list(q=subfolders_query, fields='files(id, name)').execute()
    candidate_folders = [folder_id]
    for sf in sub_res.get('files', []):
        if any(w in sf['name'].lower() for w in ['image', 'photo', 'pic', 'img']):
            logger.info(f"Found dedicated image subfolder: {sf['name']} ({sf['id']})")
            candidate_folders.insert(0, sf['id'])

    # 2. Search for images in candidate folders
    for f_id in candidate_folders:
        q = f"'{f_id}' in parents and trashed = false"
        results = drive_client.service.files().list(
            q=q, 
            fields='files(id, name, mimeType, size)', 
            pageSize=100
        ).execute()
        
        files = results.get('files', [])
        for f in files:
            name_lower = f['name'].lower()
            mime = f.get('mimeType', '').lower()
            is_image = (
                mime.startswith('image/') or 
                any(name_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp'])
            )
            if is_image and f['id'] not in posted_ids:
                return f

    return None

def post_photo_to_facebook(page_id: str, access_token: str, image_bytes: bytes, caption: str) -> str:
    """Publishes photo to Facebook Page via Meta Graph API v20.0."""
    url = f"https://graph.facebook.com/v20.0/{page_id}/photos"
    payload = {
        "caption": caption,
        "access_token": access_token
    }
    files = {"source": ("image.jpg", image_bytes, "image/jpeg")}
    
    res = requests.post(url, data=payload, files=files, timeout=45)
    if not res.ok:
        raise RuntimeError(f"Meta Graph API error ({res.status_code}): {res.text}")
        
    data = res.json()
    photo_id = data.get("id") or data.get("post_id")
    if not photo_id:
        raise RuntimeError(f"Incomplete photo publish response: {res.text}")
    return photo_id

def execute_torres_image_upload(dry_run: bool = False, local_image_path: Optional[str] = None):
    """Executes single image upload for Torres Matthew."""
    logger.info("===================================================================")
    logger.info(f"STARTING IMAGE UPLOAD ENGINE: {TARGET_PAGE_NAME} (ID: {TARGET_PAGE_ID})")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE'} | Time: {datetime.now(timezone.utc).isoformat()}")
    logger.info("===================================================================")

    page_cfg = load_page_config()
    page_id = page_cfg["page_id"]
    page_token = page_cfg["page_access_token"]
    folder_id = page_cfg["drive_folder_id"]

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    init_photos_db(conn)

    posted_ids = get_already_posted_file_ids(conn)
    logger.info(f"Total previously posted images for this page: {len(posted_ids)}")

    image_bytes = None
    file_id = None
    filename = None
    caption = ""

    # Option A: Local image passed directly
    if local_image_path and os.path.exists(local_image_path):
        filename = os.path.basename(local_image_path)
        file_id = f"local_{int(datetime.now(timezone.utc).timestamp())}"
        with open(local_image_path, "rb") as f:
            image_bytes = f.read()
        caption = os.path.splitext(filename)[0].strip()
        logger.info(f"Loaded local image: {local_image_path} ({len(image_bytes)} bytes) | Caption: {caption}")

    # Option B: Download next unposted image from Google Drive
    else:
        sa_data = os.environ.get("GDRIVE_SERVICE_ACCOUNT_JSON") or page_cfg.get("service_account_json", "service_account.json")
        if not sa_data.strip().startswith("{") and not os.path.isabs(sa_data):
            sa_data = os.path.join(BASE_DIR, sa_data)
            
        drive = DriveClient(sa_data)
        next_file = find_next_image_in_drive(drive, folder_id, posted_ids)

        if not next_file:
            msg = f"No unposted image files found in Drive folder {folder_id}. Please place .jpg/.png images in Drive."
            logger.warning(msg)
            return {"status": "no_images", "message": msg}

        file_id = next_file["id"]
        filename = next_file["name"]
        logger.info(f"Selected next image from Drive: '{filename}' (ID: {file_id})")

        # Download image into memory
        temp_dir = os.path.join(BASE_DIR, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        local_path = os.path.join(temp_dir, filename)
        drive.download_file(file_id, local_path)

        with open(local_path, "rb") as f:
            image_bytes = f.read()

        # Strict User Rule: Title/Caption is EXACTLY the file name (without extension)
        caption = os.path.splitext(filename)[0].strip()

    if dry_run:
        logger.info(f"[DRY-RUN] Would publish photo '{filename}' (ID: {file_id}) to Page {page_id}")
        logger.info(f"[DRY-RUN] Caption: {caption}")
        return {"status": "dry_run_success", "filename": filename, "file_id": file_id}

    # Live Publish to Meta Graph API
    logger.info(f"Publishing to Meta Graph API /{page_id}/photos...")
    fb_photo_id = post_photo_to_facebook(page_id, page_token, image_bytes, caption)
    logger.info(f"🟢 SUCCESS! Published to Facebook! Photo ID: {fb_photo_id}")

    # Record in database
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO posted_photos (page_id, page_name, drive_file_id, filename, caption, fb_photo_id, status)
        VALUES (?, ?, ?, ?, ?, ?, 'posted')
    """, (page_id, TARGET_PAGE_NAME, file_id, filename, caption, fb_photo_id))
    conn.commit()
    conn.close()

    return {"status": "success", "fb_photo_id": fb_photo_id, "filename": filename}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Torres Matthew Automated Image Uploader")
    parser.add_argument("--dry-run", action="store_true", help="Run without posting to Facebook")
    parser.add_argument("--local-image", type=str, default=None, help="Path to local image file")
    args = parser.parse_args()

    res = execute_torres_image_upload(dry_run=args.dry_run, local_image_path=args.local_image)
    print(json.dumps(res, indent=2))
