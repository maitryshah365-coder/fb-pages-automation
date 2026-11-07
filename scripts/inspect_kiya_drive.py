import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import json
from src.drive_client import DriveClient

client = DriveClient('service_account.json')
folder_id = '1t2N2PBsplOxf8NsZxE24H1Mtrh_Mwum6'

print(f"Connecting to Google Drive folder: {folder_id}...")
try:
    folder_meta = client.service.files().get(
        fileId=folder_id,
        fields='id, name, mimeType, webViewLink, owners'
    ).execute()
    print("Found Folder:", folder_meta.get('name'), f"({folder_meta.get('id')})")
    print("Owners:", [o.get('emailAddress') for o in folder_meta.get('owners', [])])
except Exception as e:
    print(f"Error reading root folder: {e}")
    sys.exit(1)

def deep_scan(current_folder_id, current_path=""):
    items = []
    page_token = None
    query = f"'{current_folder_id}' in parents and trashed = false"
    while True:
        resp = client.service.files().list(
            q=query,
            fields='nextPageToken, files(id, name, mimeType, size, createdTime)',
            pageSize=100,
            pageToken=page_token
        ).execute()
        items.extend(resp.get('files', []))
        page_token = resp.get('nextPageToken')
        if not page_token:
            break
    
    subfolders = []
    files = []
    for item in items:
        if item.get('mimeType') == 'application/vnd.google-apps.folder':
            subfolders.append(item)
        else:
            files.append(item)
            
    print(f"\n[Folder: {current_path or folder_meta.get('name')}] (ID: {current_folder_id})")
    print(f"  Subfolders: {len(subfolders)}, Files: {len(files)}")
    
    structure = {
        "folder_id": current_folder_id,
        "name": current_path or folder_meta.get('name'),
        "files_count": len(files),
        "files": files,
        "subfolders": []
    }
    
    for sf in subfolders:
        sub_path = f"{current_path}/{sf['name']}" if current_path else sf['name']
        sf_res = deep_scan(sf['id'], sub_path)
        structure["subfolders"].append(sf_res)
        
    return structure

print("\nStarting Deep Scan of Drive folder...")
result = deep_scan(folder_id)

with open('data/kiya_taily_drive_scan.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)

print("\nScan completed! Saved details to data/kiya_taily_drive_scan.json")
