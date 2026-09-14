import os
import sys
import json
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
token_file = os.path.join(BASE_DIR, "gdrive_owner.token")
secret_file = os.path.join(BASE_DIR, "client_secret.json")

token = open(token_file, encoding="utf-8").read().strip()
secret = json.load(open(secret_file, encoding="utf-8"))
installed = secret.get("installed") or secret.get("web")

creds = Credentials(
    None,
    refresh_token=token,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=installed["client_id"],
    client_secret=installed["client_secret"],
    scopes=["https://www.googleapis.com/auth/drive"]
)
service = build("drive", "v3", credentials=creds)

SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}
SUPPORTED_MIME_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/x-m4v",
    "video/webm",
    "video/x-matroska",
    "application/octet-stream"
}

def scan_folder_recursive(folder_id, folder_name=""):
    """
    Recursively scans a Google Drive folder with FULL pagination.
    Loops through all pages until nextPageToken is exhausted.
    Returns: list of video dicts and list of subfolders.
    """
    all_videos = []
    subfolders = []
    page_token = None
    page_count = 0

    while True:
        page_count += 1
        query = f"'{folder_id}' in parents and trashed = false"
        res = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType, size, createdTime)",
            pageSize=1000, # Request maximum page size allowed by Google Drive API (up to 1000)
            pageToken=page_token
        ).execute()

        items = res.get("files", [])
        for it in items:
            mime = it.get("mimeType", "")
            name = it.get("name", "")
            ext = os.path.splitext(name)[1].lower()

            if mime == "application/vnd.google-apps.folder":
                subfolders.append(it)
            elif ext in SUPPORTED_EXTENSIONS or mime in SUPPORTED_MIME_TYPES or "video/" in mime:
                all_videos.append(it)

        page_token = res.get("nextPageToken")
        if not page_token:
            break

    # Recurse into subfolders if any
    for sf in subfolders:
        sub_vids, _ = scan_folder_recursive(sf["id"], sf.get("name", ""))
        all_videos.extend(sub_vids)

    return all_videos, subfolders

def main():
    parent_folder_id = "1IL8OAUOfOZpisnHiGV0cKeO6x7O_UYRS"
    print(f"=== FULL DEEP SCAN OF 'Usa Ids GITHUB' ({parent_folder_id}) ===")
    
    # 1. List all items in the main folder
    main_res = service.files().list(
        q=f"'{parent_folder_id}' in parents and trashed = false",
        fields="nextPageToken, files(id, name, mimeType)",
        pageSize=1000
    ).execute()
    
    folder_items = main_res.get("files", [])
    print(f"Found {len(folder_items)} subfolders/items in main directory.\n")
    
    scan_results = {}
    total_videos_found = 0
    
    for item in sorted(folder_items, key=lambda x: x.get("name", "")):
        fid = item["id"]
        fname = item["name"]
        mime = item.get("mimeType", "")
        
        if mime == "application/vnd.google-apps.folder":
            print(f"Scanning folder: '{fname}' (ID: {fid})...", flush=True)
            videos, subfolders = scan_folder_recursive(fid, fname)
            total_size_bytes = sum(int(v.get("size", 0) or 0) for v in videos)
            total_size_mb = round(total_size_bytes / (1024 * 1024), 2)
            
            scan_results[fname] = {
                "folder_id": fid,
                "video_count": len(videos),
                "total_size_mb": total_size_mb,
                "subfolders_count": len(subfolders),
                "sample_videos": [v.get("name") for v in videos[:3]]
            }
            total_videos_found += len(videos)
            print(f"  -> EXACT COUNT: {len(videos)} videos | Size: {total_size_mb} MB | Subfolders: {len(subfolders)}\n", flush=True)
        else:
            print(f"File in root: {fname} ({fid})")
            
    print("==========================================================")
    print(f"TOTAL VERIFIED VIDEOS ACROSS ALL 11 FOLDERS: {total_videos_found}")
    print("==========================================================")
    
    # Save detailed scan results to JSON
    output_path = os.path.join(BASE_DIR, "data", "drive_folders_audit.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scan_results, f, indent=2, ensure_ascii=False)
    print(f"Audit results saved to {output_path}")

if __name__ == "__main__":
    main()
