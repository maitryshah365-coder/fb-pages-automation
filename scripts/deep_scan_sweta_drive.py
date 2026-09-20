import os
import sys
import json
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

with open(os.path.join(BASE_DIR, "data", "sweta_drive_folders.json"), "r", encoding="utf-8") as f:
    drive_data = json.load(f)

subfolders = drive_data.get("subfolders", [])

print(f"==================================================")
print(f"DEEP SCANNING {len(subfolders)} SUB-FOLDERS IN GOOGLE DRIVE...")
print(f"==================================================")

deep_results = []
total_videos_all_folders = 0
total_size_bytes = 0

for idx, folder in enumerate(subfolders, 1):
    fid = folder["id"]
    fname = folder["name"]
    print(f"\n[{idx}/{len(subfolders)}] Deep scanning folder: '{fname}' (ID: {fid})")
    
    # Query all non-trashed files in this folder
    files = []
    page_token = None
    while True:
        res = service.files().list(
            q=f"'{fid}' in parents and trashed = false",
            fields="nextPageToken, files(id, name, mimeType, size, createdTime)",
            pageSize=1000,
            pageToken=page_token
        ).execute()
        files.extend(res.get("files", []))
        page_token = res.get("nextPageToken")
        if not page_token:
            break
            
    video_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v')
    video_files = []
    other_files = []
    nested_folders = []
    folder_size = 0
    
    for f in files:
        f_name = f.get("name", "")
        f_mime = f.get("mimeType", "")
        f_size = int(f.get("size", 0)) if f.get("size") else 0
        folder_size += f_size
        
        if f_mime == "application/vnd.google-apps.folder":
            nested_folders.append(f)
        elif f_mime.startswith("video/") or f_name.lower().endswith(video_extensions):
            video_files.append(f)
        else:
            other_files.append(f)
            
    total_videos_all_folders += len(video_files)
    total_size_bytes += folder_size
    
    size_mb = round(folder_size / (1024 * 1024), 2)
    sample_files = [f.get("name") for f in video_files[:3]]
    
    print(f"  -> Total Items: {len(files)}")
    print(f"  -> Video Files (.mp4/reels): {len(video_files)}")
    print(f"  -> Total Size: {size_mb} MB")
    if sample_files:
        print(f"  -> Sample Videos: {sample_files}")
    if other_files:
        print(f"  -> Other Files ({len(other_files)}): {[f.get('name') for f in other_files[:3]]}")
    if nested_folders:
        print(f"  -> Nested Subfolders ({len(nested_folders)}): {[f.get('name') for f in nested_folders]}")

    deep_results.append({
        "folder_name": fname,
        "folder_id": fid,
        "total_items": len(files),
        "video_count": len(video_files),
        "folder_size_bytes": folder_size,
        "folder_size_mb": size_mb,
        "sample_videos": sample_files,
        "nested_folders_count": len(nested_folders),
        "other_files_count": len(other_files)
    })

audit_summary = {
    "parent_folder_id": drive_data.get("parent", {}).get("id"),
    "parent_folder_name": drive_data.get("parent", {}).get("name"),
    "total_subfolders": len(subfolders),
    "total_videos": total_videos_all_folders,
    "total_size_mb": round(total_size_bytes / (1024 * 1024), 2),
    "total_size_gb": round(total_size_bytes / (1024 * 1024 * 1024), 2),
    "folders": deep_results
}

out_path = os.path.join(BASE_DIR, "data", "sweta_drive_deep_audit.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(audit_summary, f, indent=2)

print("\n==================================================")
print(f"DEEP SCAN COMPLETE!")
print(f"Total Videos across 12 Folders: {total_videos_all_folders}")
print(f"Total Storage Size: {audit_summary['total_size_gb']} GB ({audit_summary['total_size_mb']} MB)")
print(f"Detailed audit saved to: {out_path}")
print("==================================================")
