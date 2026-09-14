"""
cleanup_orphaned.py
Permanently deletes ONLY:
1. Videos recorded as 'posted' in data/posted_videos.db
2. 0-byte ghost/orphaned video files dumped in root 'My Drive'

STRICT RULE: Never touches any unposted video inside page folders!
"""
import os
import sys
import json
import sqlite3
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
token_path = os.path.join(BASE_DIR, "gdrive_owner.token")
secret_path = os.path.join(BASE_DIR, "client_secret.json")
db_path = os.path.join(BASE_DIR, "data", "posted_videos.db")

if not os.path.exists(token_path):
    token = os.environ.get("GDRIVE_OWNER_REFRESH_TOKEN")
    if not token:
        print(f"❌ gdrive_owner.token not found at {token_path}")
        sys.exit(1)
else:
    token = open(token_path, "r", encoding="utf-8").read().strip()

if not os.path.exists(secret_path):
    secret_env = os.environ.get("GDRIVE_CLIENT_SECRET_JSON")
    if not secret_env:
        print(f"❌ client_secret.json not found at {secret_path}")
        sys.exit(1)
    secret_data = json.loads(secret_env)
else:
    secret_data = json.load(open(secret_path, "r", encoding="utf-8"))

installed = secret_data.get("installed") or secret_data.get("web", secret_data)

creds = Credentials(
    None,
    refresh_token=token,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=installed["client_id"],
    client_secret=installed["client_secret"],
    scopes=["https://www.googleapis.com/auth/drive"]
)

service = build("drive", "v3", credentials=creds)

posted_file_ids = set()
posted_filenames = set()

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT drive_file_id, filename FROM videos WHERE status = 'posted'")
    for fid, fname in c.fetchall():
        if fid:
            posted_file_ids.add(fid)
        if fname:
            posted_filenames.add(fname)
    conn.close()

PROTECTED_FOLDER_IDS = {
    "1D3y9fSqvz8Be1ted5Wic7egRJzBn--gB", # Page 2 - Charmy Owen
    "1ohpJm22Koo_ouVSQZCwiHE0pwAyAyxDg", # Page 5 - Bright Flare Hub
    "1rjGrEIrCk9TlEJBABjo0K-8MKAaBxZy9", # Page 8 - Crown Empire
    "1qMwQtRtvJXbmV8iEYW1GS0IQ8VDLWA6s", # Page 9 - Crafty Champions
    "1Kir7IF-zX_XN8FoaasVJTPT_TRQ1J0Xg", # Page 11 - Dominion Authority
    "1UDZx4XRzdn-5r7O9WRfUOSui2nCWuR5R", # Page 12 - Family Fancy
    "1g_Z4BtdfNqT2jF3hL9tExTr9W3Ly1YrZ", # Page 14 - Bot Mask
}

page_token = None
all_files = []

while True:
    res = service.files().list(
        q="mimeType contains 'video/' and trashed = false",
        fields="nextPageToken, files(id, name, size, parents)",
        pageSize=100,
        pageToken=page_token
    ).execute()
    all_files.extend(res.get("files", []))
    page_token = res.get("nextPageToken")
    if not page_token:
        break

deleted_count = 0
skipped_count = 0

for f in all_files:
    fid = f["id"]
    fname = f.get("name", "")
    size = int(f.get("size", 0) or 0)
    parents = f.get("parents", [])

    is_in_active_folder = any(p in PROTECTED_FOLDER_IDS for p in parents)
    if is_in_active_folder and fid not in posted_file_ids:
        skipped_count += 1
        continue

    is_posted = (fid in posted_file_ids) or (fname in posted_filenames)
    is_root_ghost = (size == 0) and (not parents or any(p == "root" for p in parents))

    if is_posted or is_root_ghost:
        try:
            service.files().delete(fileId=fid).execute()
            deleted_count += 1
        except Exception as e:
            print(f"Error deleting {fname} ({fid}): {e}")
    else:
        skipped_count += 1

print(f"Cleanup complete. Deleted: {deleted_count}, Preserved: {skipped_count}")
