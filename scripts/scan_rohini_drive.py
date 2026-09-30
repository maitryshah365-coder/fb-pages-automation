"""
Scan Rohini Dutt's Google Drive parent folder and map subfolders to pages.
Parent Folder ID: 13bVMjww0C2jHHjrhTz4yb0OKw1jK2_qk
"""

import os
import sys
import json
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


def scan_rohini_drive():
    print("=================================================================")
    print(f"📂 SCANNING ROHINI DUTT GOOGLE DRIVE PARENT: {PARENT_FOLDER_ID}")
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
        # Check parent folder access
        parent = service.files().get(fileId=PARENT_FOLDER_ID, fields="id, name, mimeType").execute()
        print(f"✅ Parent Folder Accessible: '{parent.get('name')}' (ID: {parent.get('id')})")
    except Exception as e:
        print(f"❌ Error accessing parent folder with service account: {e}")
        print("\nNote: Please make sure the folder is shared with:")
        print("drive-bot@neon-poetry-508515-t7.iam.gserviceaccount.com")
        print("OR set to 'Anyone with the link can view'.")
        return

    # List all child folders
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

    print(f"\n📁 Discovered {len(subfolders)} Subfolders in Parent:")

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

        print(f"  #{idx:02d} {fname:22s} | ID: {fid} | Stock: {v_count} videos")

    print("-----------------------------------------------------------------")
    print(f"🎉 TOTAL SUBFOLDERS: {len(subfolders)} | TOTAL REELS IN DRIVE: {total_stock}")
    print("=================================================================")

    # Save to data directory
    out_file = os.path.join(BASE_DIR, "data", "rohini_dutt_drive_folders.json")
    with open(out_file, "w", encoding="utf-8") as fp:
        json.dump(mapped_data, fp, indent=2, ensure_ascii=False)
    print(f"✅ Saved folder mapping to: {out_file}")

    return mapped_data


if __name__ == "__main__":
    scan_rohini_drive()
