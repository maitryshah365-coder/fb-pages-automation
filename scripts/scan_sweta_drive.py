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

target_folder_id = "1juR-SabCgQnyM2VXLjNwgaYlb2HlDIHm"

# Check root folder details
folder_meta = service.files().get(fileId=target_folder_id, fields="id, name, mimeType").execute()
print(f"Parent Folder: {folder_meta.get('name')} (ID: {target_folder_id})")

# List contents
res = service.files().list(
    q=f"'{target_folder_id}' in parents and trashed = false",
    fields="files(id, name, mimeType)",
    pageSize=100
).execute()

items = res.get("files", [])
print(f"Found {len(items)} items in parent folder:")
subfolders = []
for it in items:
    is_folder = it.get("mimeType") == "application/vnd.google-apps.folder"
    print(f"  - {'[FOLDER]' if is_folder else '[FILE]'} {it.get('name')} (ID: {it.get('id')})")
    if is_folder:
        subfolders.append(it)

with open("data/sweta_drive_folders.json", "w", encoding="utf-8") as f:
    json.dump({"parent": folder_meta, "subfolders": subfolders, "all_items": items}, f, indent=2)
