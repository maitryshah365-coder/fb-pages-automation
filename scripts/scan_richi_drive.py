import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src.drive_client import DriveClient

client = DriveClient(os.path.join(BASE_DIR, 'service_account.json'))
parent_id = '1wOPsQkTcLI-YFuGSdbf-jkp1U8txnuAf'

query = f"'{parent_id}' in parents and trashed = false"
res = client.service.files().list(q=query, fields='files(id, name, mimeType)').execute()
items = res.get('files', [])
print(f'Total items in parent folder: {len(items)}')

subfolders = [x for x in items if x.get('mimeType') == 'application/vnd.google-apps.folder']
print(f'Total subfolders: {len(subfolders)}')

folder_stats = []
total_vids = 0
for sf in sorted(subfolders, key=lambda x: x['name']):
    sf_id = sf['id']
    sf_name = sf['name']
    vids = client.list_folder_videos(sf_id)
    total_vids += len(vids)
    folder_stats.append({
        'name': sf_name,
        'id': sf_id,
        'count': len(vids)
    })
    print(f'Folder: {sf_name} | ID: {sf_id} | Videos: {len(vids)}')

print(f'Total Videos across all subfolders: {total_vids}')
os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
with open(os.path.join(BASE_DIR, 'data', 'richi_drive_folders.json'), 'w', encoding='utf-8') as f:
    json.dump(folder_stats, f, indent=2)
