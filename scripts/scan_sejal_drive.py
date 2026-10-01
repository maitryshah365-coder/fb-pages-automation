import os
import sys
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT_FOLDER_ID = "1MfcfgaBAx-droknvCz6ziEem2Jrj3IHb"
SA_PATH = os.path.join(BASE_DIR, "service_account.json")

def scan_sejal_drive():
    print("=================================================================")
    print(f"📂 SCANNING SEJAL SONI GOOGLE DRIVE PARENT: {PARENT_FOLDER_ID}")
    print("=================================================================")

    if not os.path.exists(SA_PATH):
        print(f"Error: Service account file missing at {SA_PATH}")
        return

    creds = Credentials.from_service_account_file(
        SA_PATH,
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )
    service = build('drive', 'v3', credentials=creds)

    try:
        parent = service.files().get(fileId=PARENT_FOLDER_ID, fields="id, name, mimeType").execute()
        print(f"Parent Folder Accessible: '{parent.get('name')}' (ID: {parent.get('id')})")
    except Exception as e:
        print(f"Error accessing parent folder: {e}")
        return

    query = f"'{PARENT_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    subfolders = []
    page_token = None

    while True:
        res = service.files().list(
            q=query,
            pageSize=100,
            fields="nextPageToken, files(id, name)",
            pageToken=page_token
        ).execute()

        subfolders.extend(res.get('files', []))
        page_token = res.get('nextPageToken')
        if not page_token:
            break

    print(f"\nDiscovered {len(subfolders)} Subfolders in Parent:")

    mapped_data = {}
    total_stock = 0

    for idx, f in enumerate(subfolders, 1):
        fid = f.get('id')
        fname = f.get('name').strip()

        # Count mp4 files inside this subfolder
        v_query = f"'{fid}' in parents and mimeType contains 'video/' and trashed = false"
        v_res = service.files().list(
            q=v_query,
            pageSize=100,
            fields="files(id, name, size)"
        ).execute()

        vids = v_res.get('files', [])
        v_count = len(vids)
        total_stock += v_count

        mapped_data[fname] = {
            "folder_id": fid,
            "video_count": v_count,
            "sample_videos": [v.get('name') for v in vids[:3]]
        }

        print(f"  #{idx:02d} {fname:25s} | ID: {fid} | Stock: {v_count} videos")

    print("-----------------------------------------------------------------")
    print(f"TOTAL SUBFOLDERS: {len(subfolders)} | TOTAL REELS IN DRIVE: {total_stock}")
    print("=================================================================")

    out_file = os.path.join(BASE_DIR, "data", "sejal_soni_drive_folders.json")
    with open(out_file, "w", encoding="utf-8") as out:
        json.dump(mapped_data, out, indent=2, ensure_ascii=False)
    print(f"Saved mapping to {out_file}")

if __name__ == "__main__":
    scan_sejal_drive()
