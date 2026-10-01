"""
Deep Recursive Scanner for Sejal Soni (USA 5) Google Drive Folder
Parent Folder ID: 1MfcfgaBAx-droknvCz6ziEem2Jrj3IHb

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
PARENT_FOLDER_ID = "1MfcfgaBAx-droknvCz6ziEem2Jrj3IHb"
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
        sub_vids, sub_subfolders = scan_folder_recursive(service, sub['id'], sub['name'])
        video_files.extend(sub_vids)

    return video_files, subfolders


def deep_scan_sejal():
    print("=================================================================")
    print("🔍 DEEP RECURSIVE SCANNER: SEJAL SONI GOOGLE DRIVE FOLDER")
    print(f"Parent Folder: {PARENT_FOLDER_ID}")
    print("=================================================================")

    service = get_drive_service()

    parent = service.files().get(
        fileId=PARENT_FOLDER_ID,
        fields="id, name",
        supportsAllDrives=True
    ).execute()
    print(f"Connected to Parent: '{parent['name']}' (ID: {parent['id']})\n")

    # Discover top-level folders
    top_children = list_children(service, PARENT_FOLDER_ID)
    channel_folders = [c for c in top_children if c.get('mimeType') == 'application/vnd.google-apps.folder']

    print(f"Found {len(channel_folders)} Channel Subfolders. Scanning each deeply with pagination...\n")

    folder_results = {}
    grand_total_videos = 0
    grand_total_bytes = 0

    for idx, folder in enumerate(channel_folders, 1):
        f_id = folder['id']
        f_name = folder['name'].strip()

        print(f"[{idx:02d}/{len(channel_folders)}] Deep scanning: {f_name:25s} (ID: {f_id})...", end="", flush=True)

        videos, subdirs = scan_folder_recursive(service, f_id, f_name)
        total_size = sum(int(v.get('size', 0)) for v in videos)
        size_mb = round(total_size / (1024 * 1024), 2)
        size_gb = round(total_size / (1024 * 1024 * 1024), 2)

        grand_total_videos += len(videos)
        grand_total_bytes += total_size

        print(f" -> {len(videos):4d} videos ({size_mb} MB)")

        folder_results[f_name] = {
            "folder_id": f_id,
            "folder_name": f_name,
            "video_count": len(videos),
            "size_bytes": total_size,
            "size_mb": size_mb,
            "size_gb": size_gb,
            "nested_subfolders_count": len(subdirs),
            "sample_files": [v['name'] for v in videos[:5]]
        }

    grand_gb = round(grand_total_bytes / (1024 * 1024 * 1024), 2)
    print("\n" + "=" * 65)
    print("📊 DEEP SCAN AUDIT SUMMARY - SEJAL SONI")
    print(f"Total Folders Scanned:    {len(channel_folders)}")
    print(f"TOTAL REAL VIDEOS FOUND:  {grand_total_videos:,} Videos")
    print(f"Total Cloud Data Volume:  {grand_gb} GB ({round(grand_total_bytes/(1024*1024), 1):,} MB)")
    print("=" * 65)

    output_data = {
        "scanned_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "account_owner": "Sejal Soni",
        "parent_folder_id": PARENT_FOLDER_ID,
        "total_folders": len(channel_folders),
        "total_videos": grand_total_videos,
        "total_bytes": grand_total_bytes,
        "total_gb": grand_gb,
        "folders": folder_results
    }

    out_file = os.path.join(BASE_DIR, "data", "sejal_soni_drive_folders.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Saved comprehensive deep scan audit to: {out_file}")

    return output_data


if __name__ == "__main__":
    deep_scan_sejal()
