import json
import os
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sa_path = "service_account.json"
creds = service_account.Credentials.from_service_account_file(
    sa_path, scopes=["https://www.googleapis.com/auth/drive"]
)
service = build("drive", "v3", credentials=creds, cache_discovery=False)

root_id = "1sg_kvPou11Tmi1Xn-mnfdHgh1OgEv-6v"
print(f"=== SCANNING KALPESH SHAH ROOT GOOGLE DRIVE FOLDER: {root_id} ===")

video_exts = (".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm")

def list_folder_contents(fid):
    items = []
    page_token = None
    q = f"'{fid}' in parents and trashed = false"
    while True:
        res = service.files().list(
            q=q,
            pageSize=1000,
            fields="nextPageToken, files(id, name, mimeType, size)",
            pageToken=page_token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        items.extend(res.get("files", []))
        page_token = res.get("nextPageToken")
        if not page_token:
            break
    return items

# 1. Get root contents
root_items = list_folder_contents(root_id)
print(f"Total direct items inside Root: {len(root_items)}")

subfolders = [i for i in root_items if i.get("mimeType") == "application/vnd.google-apps.folder"]
direct_files = [i for i in root_items if i.get("mimeType") != "application/vnd.google-apps.folder"]
print(f"Subfolders count: {len(subfolders)}")
print(f"Direct files count: {len(direct_files)}")

# Check any direct video files in root
root_videos = [f for f in direct_files if int(f.get("size") or 0) > 0 and (f.get("name", "").lower().endswith(video_exts) or f.get("mimeType", "").startswith("video/"))]
if root_videos:
    print(f"WARNING: Root contains {len(root_videos)} direct playable videos!")

print("\n--- SUBFOLDERS DETAILED SCAN ---")
total_playable = 0
total_zero = 0

for idx, folder in enumerate(subfolders, 1):
    fid = folder.get("id")
    fname = folder.get("name")
    contents = list_folder_contents(fid)
    
    valid_vids = [f for f in contents if int(f.get("size") or 0) > 0 and (f.get("name", "").lower().endswith(video_exts) or f.get("mimeType", "").startswith("video/"))]
    zero_files = [f for f in contents if int(f.get("size") or 0) == 0]
    nested_folders = [f for f in contents if f.get("mimeType") == "application/vnd.google-apps.folder"]
    
    total_playable += len(valid_vids)
    total_zero += len(zero_files)
    
    print(f"[{idx:02d}] Folder: {fname:25} | ID: {fid} | Valid Videos: {len(valid_vids):4} | Zero-byte: {len(zero_files):3} | Nested Folders: {len(nested_folders)}")
    
    # If nested folders exist, scan them too!
    if nested_folders:
        for nf in nested_folders:
            n_fid = nf.get("id")
            n_fname = nf.get("name")
            n_contents = list_folder_contents(n_fid)
            n_vids = [f for f in n_contents if int(f.get("size") or 0) > 0 and (f.get("name", "").lower().endswith(video_exts) or f.get("mimeType", "").startswith("video/"))]
            print(f"     └── Nested: {n_fname:20} | ID: {n_fid} | Videos: {len(n_vids):4}")
            total_playable += len(n_vids)

print("\n" + "="*60)
print(f"KALPESH SHAH DRIVE GRAND TOTAL:")
print(f"Total Folders: {len(subfolders)}")
print(f"Total Playable Stock Videos: {total_playable}")
print(f"Total 0-byte Wiped: {total_zero}")
print("="*60)
