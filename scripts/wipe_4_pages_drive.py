import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from googleapiclient.http import MediaInMemoryUpload
from googleapiclient.discovery import build
from google.oauth2 import service_account

sys.path.insert(0, ".")

TARGET_FOLDERS = {
    "Happy place (Kalpesh Shah)": "12TzotKAwMMV2M6Gt1vBAF9UFX-Fmw3XO",
    "Flute Tomography Nature (Sejal Soni)": "1FIoYms_6U3QdS35BHu7Cbblymf-JSZTk",
    "Tag The (Sejal Soni)": "1sNeSPh3H1oXsUzw_YDmX05785CfSZM7Z",
    "The Daily Spark (Sejal Soni)": "16deNYAwBPFU7bcXZffCt2F242_XeRvIP"
}

_thread_local = threading.local()

def get_drive_service():
    if not hasattr(_thread_local, "service"):
        creds = service_account.Credentials.from_service_account_file(
            "service_account.json",
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        _thread_local.service = build("drive", "v3", credentials=creds, cache_discovery=False)
    return _thread_local.service

def wipe_file(file_info):
    file_id = file_info['id']
    file_name = file_info['name']
    try:
        service = get_drive_service()
        media = MediaInMemoryUpload(b"", mimetype="application/octet-stream")
        service.files().update(fileId=file_id, media_body=media, supportsAllDrives=True).execute()
        return True, file_id, file_name, None
    except Exception as e:
        return False, file_id, file_name, str(e)

def list_folder_files(folder_id):
    service = get_drive_service()
    query = f"'{folder_id}' in parents and trashed = false"
    files = []
    page_token = None
    while True:
        resp = service.files().list(
            q=query,
            spaces="drive",
            fields="nextPageToken, files(id, name, size)",
            pageToken=page_token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            pageSize=100
        ).execute()
        files.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return files

def main():
    print("=" * 65, flush=True)
    print("🧹 THREAD-SAFE ZERO-BYTE DRIVE QUOTA PURGE", flush=True)
    print("=" * 65, flush=True)
    
    total_wiped = 0
    total_failed = 0
    already_zero = 0

    for name, fid in TARGET_FOLDERS.items():
        print(f"\n📂 Scanning folder: {name} ({fid})...", flush=True)
        files = list_folder_files(fid)
        to_wipe = []
        for f in files:
            sz = int(f.get('size', 0))
            if sz > 0:
                to_wipe.append(f)
            else:
                already_zero += 1

        print(f"   Found {len(files)} total files ({already_zero} already 0 bytes, {len(to_wipe)} needing wipe)...", flush=True)
        if not to_wipe:
            print("   ✅ All files in this folder are already 0 bytes!", flush=True)
            continue

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(wipe_file, f) for f in to_wipe]
            for future in as_completed(futures):
                success, fid_res, fname, err = future.result()
                if success:
                    total_wiped += 1
                    if total_wiped % 20 == 0 or total_wiped == len(to_wipe):
                        print(f"   [PROGRESS] Wiped {total_wiped} files to 0 bytes...", flush=True)
                else:
                    total_failed += 1
                    print(f"   [FAILED] {fname[:30]} ({fid_res}): {err}", flush=True)

    print("\n" + "=" * 65, flush=True)
    print(f"🎉 GOOGLE DRIVE PURGE COMPLETE!", flush=True)
    print(f"   Newly wiped: {total_wiped} files", flush=True)
    print(f"   Already zero: {already_zero} files", flush=True)
    print(f"   Total 0-byte cleaned: {total_wiped + already_zero} files", flush=True)
    print(f"   Failed: {total_failed} files", flush=True)
    print("=" * 65, flush=True)

if __name__ == "__main__":
    main()
