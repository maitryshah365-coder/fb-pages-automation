import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from src.drive_client import DriveClient

def main():
    target_id = "1IL8OAUOfOZpisnHiGV0cKeO6x7O_UYRS"
    client = DriveClient("service_account.json")
    try:
        meta = client.service.files().get(fileId=target_id, fields="id, name, mimeType", supportsAllDrives=True).execute()
        print("Folder Name:", meta.get("name"))
        print("Folder ID:", meta.get("id"))

        query = f"'{target_id}' in parents and trashed = false"
        results = client.service.files().list(
            q=query,
            fields="files(id, name, mimeType, size)",
            pageSize=100,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        files = results.get("files", [])
        print(f"Total items inside: {len(files)}")
        for f in files:
            mtype = "DIR" if f.get("mimeType") == "application/vnd.google-apps.folder" else "FILE"
            print(f"  [{mtype}] {f.get('name')} | ID: {f.get('id')}")
            
            # If it's a directory, let's also peek inside to see how many files it has
            if mtype == "DIR":
                sub_q = f"'{f.get('id')}' in parents and trashed = false"
                sub_res = client.service.files().list(
                    q=sub_q,
                    fields="files(id, name, mimeType)",
                    pageSize=10,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True
                ).execute()
                sub_files = sub_res.get("files", [])
                print(f"       -> Contains {len(sub_files)} items (showing max 3):")
                for sf in sub_files[:3]:
                    print(f"          * {sf.get('name')}")
    except Exception as e:
        print("Error accessing Google Drive:", e)

if __name__ == "__main__":
    main()
