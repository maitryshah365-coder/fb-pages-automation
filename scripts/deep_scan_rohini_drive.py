"""
Deep Recursive Scanner for Rohini Dutt Google Drive Folder
Parent Folder ID: 13bVMjww0C2jHHjrhTz4yb0OKw1jK2_qk

Features:
- Full pagination (pageToken loops until none left, up to 1000 pageSize)
- Recursive subfolder discovery (scans nested folders)
- Comprehensive video detection (mimeType video/* OR extension .mp4, .mov, etc.)
- Outputs exact counts, file samples, and size statistics
"""

import os
import sys
import json
import time
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT_FOLDER_ID = "13bVMjww0C2jHHjrhTz4yb0OKw1jK2_qk"
SA_PATH = os.path.join(BASE_DIR, "service_account.json")

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

VIDEO_EXTENSIONS = ('.mp4', '.mov', '.mkv', '.webm', '.avi', '.m4v', '.3gp')


def is_video(item):
    name = (item.get('name') or '').lower()
    mime = (item.get('mimeType') or '').lower()
    if 'video/' in mime:
        return True
    if any(name.endswith(ext) for ext in VIDEO_EXTENSIONS):
        return True
    return False


def get_drive_service():
    if os.path.exists(SA_PATH):
        creds = Credentials.from_service_account_file(
            SA_PATH,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        return build('drive', 'v3', credentials=creds)

    creds_json = os.environ.get('GDRIVE_SERVICE_ACCOUNT_JSON')
    if creds_json:
        creds = Credentials.from_service_account_info(
            json.loads(creds_json),
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        return build('drive', 'v3', credentials=creds)

    raise RuntimeError(f"Service account not found at {SA_PATH} and GDRIVE_SERVICE_ACCOUNT_JSON env empty.")


def list_children(service, folder_id):
    """Fetch ALL direct children of a folder with full pagination."""
    items = []
    page_token = None
    query = f"'{folder_id}' in parents and trashed = false"

    while True:
        res = service.files().list(
            q=query,
            pageSize=1000,
            fields="nextPageToken, files(id, name, mimeType, size, createdTime)",
            pageToken=page_token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()

        items.extend(res.get('files', []))
        page_token = res.get('nextPageToken')
        if not page_token:
            break

    return items


def scan_folder_recursive(service, folder_id, folder_name=""):
    """Recursively scan a folder and all nested subfolders for video files."""
    children = list_children(service, folder_id)

    video_files = []
    subfolders = []

    for child in children:
        mime = child.get('mimeType', '')
        if mime == 'application/vnd.google-apps.folder':
            subfolders.append(child)
        elif is_video(child):
            video_files.append(child)

    # Recurse into subfolders
    for sub in subfolders:
        sub_name = f"{folder_name}/{sub.get('name')}" if folder_name else sub.get('name')
        sub_vids, sub_nested_folders = scan_folder_recursive(service, sub.get('id'), sub_name)
        video_files.extend(sub_vids)

    return video_files, subfolders


def deep_scan():
    print("=" * 70)
    print("🔍 INITIATING DEEP RECURSIVE SCAN OF ROHINI DUTT GOOGLE DRIVE")
    print(f"   Parent Folder ID: {PARENT_FOLDER_ID}")
    print("=" * 70)

    service = get_drive_service()

    # Step 1: Discover all top-level items in parent
    parent_meta = service.files().get(
        fileId=PARENT_FOLDER_ID,
        fields="id, name, mimeType",
        supportsAllDrives=True
    ).execute()
    print(f"✅ Root Folder: '{parent_meta.get('name')}' (ID: {parent_meta.get('id')})\n")

    top_items = list_children(service, PARENT_FOLDER_ID)
    top_folders = [f for f in top_items if f.get('mimeType') == 'application/vnd.google-apps.folder']
    top_loose_videos = [f for f in top_items if is_video(f)]

    print(f"📁 Found {len(top_folders)} top-level subfolders in parent.")
    if top_loose_videos:
        print(f"🎬 Found {len(top_loose_videos)} loose videos in root directory.")

    results = {}
    grand_total_videos = len(top_loose_videos)
    grand_total_bytes = sum(int(f.get('size', 0)) for f in top_loose_videos)

    print("\nScanning each folder deeply with full pagination and subfolder traversal...")
    print("-" * 70)

    for idx, folder in enumerate(top_folders, 1):
        f_id = folder.get('id')
        f_name = folder.get('name').strip()

        vids, sub_dirs = scan_folder_recursive(service, f_id, f_name)
        v_count = len(vids)
        total_size_mb = sum(int(v.get('size', 0)) for v in vids) / (1024 * 1024)

        grand_total_videos += v_count
        grand_total_bytes += sum(int(v.get('size', 0)) for v in vids)

        results[f_name] = {
            "folder_id": f_id,
            "folder_name": f_name,
            "video_count": v_count,
            "nested_subfolders_count": len(sub_dirs),
            "size_mb": round(total_size_mb, 2),
            "first_few": [v.get('name') for v in vids[:3]],
            "last_few": [v.get('name') for v in vids[-3:]] if len(vids) > 3 else []
        }

        nested_info = f" (+ {len(sub_dirs)} nested folders)" if sub_dirs else ""
        print(f"[{idx:02d}/{len(top_folders):02d}] {f_name:24s} ➔ {v_count:>4d} videos ({total_size_mb:>7.1f} MB){nested_info}")

    print("-" * 70)
    grand_total_gb = grand_total_bytes / (1024 * 1024 * 1024)
    print(f"🎯 DEEP SCAN COMPLETE:")
    print(f"   Total Subfolders Scanned: {len(top_folders)}")
    print(f"   Total Real Videos Found:  {grand_total_videos:,} Reels")
    print(f"   Total Storage:            {grand_total_gb:.2f} GB")
    print("=" * 70)

    # Save to JSON
    out_path = os.path.join(BASE_DIR, "data", "rohini_dutt_drive_folders.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "parent_folder_id": PARENT_FOLDER_ID,
            "total_folders": len(top_folders),
            "total_videos": grand_total_videos,
            "scanned_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "folders": results
        }, f, indent=2, ensure_ascii=False)

    print(f"\nSaved deep scan results to: {out_path}")
    return results, grand_total_videos


if __name__ == "__main__":
    deep_scan()
