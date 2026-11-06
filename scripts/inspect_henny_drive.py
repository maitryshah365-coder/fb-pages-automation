import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import json
from src.drive_client import DriveClient

client = DriveClient('service_account.json')
folder_id = '12dNCaP3UDIAn9wysWEbaw6hDRyiKc1fc'

query = f"'{folder_id}' in parents and trashed = false"
results = client.service.files().list(q=query, fields='files(id, name, mimeType)', pageSize=100).execute()
files = results.get('files', [])

print(f"Total items in folder {folder_id}: {len(files)}")
subfolders = []
for f in files:
    is_folder = f['mimeType'] == 'application/vnd.google-apps.folder'
    if is_folder:
        subfolders.append(f)

print(f"\nSubfolders count: {len(subfolders)}\n")
print(f"{'Folder / Page Name':25} | {'Folder ID':35} | {'Videos'}")
print("-" * 75)

total_videos = 0
folder_map = {}
for sf in subfolders:
    vids = client.list_folder_videos(sf['id'])
    v_count = len(vids)
    total_videos += v_count
    folder_map[sf['name'].strip()] = sf['id']
    print(f"{sf['name']:25} | {sf['id']:35} | {v_count} videos")

print("-" * 75)
print(f"TOTAL STOCK ACROSS HENNY FLEET: {total_videos} videos\n")

# Save folder map for future config generation
with open('data/henny_drive_folder_map.json', 'w', encoding='utf-8') as fp:
    json.dump(folder_map, fp, indent=2)
print("Folder map saved to data/henny_drive_folder_map.json")
