import json
import os
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
import yaml

sa_path = "service_account.json"
creds = service_account.Credentials.from_service_account_file(
    sa_path, scopes=["https://www.googleapis.com/auth/drive"]
)
service = build("drive", "v3", credentials=creds, cache_discovery=False)

# Collect all pages and folders across all config files
all_pages = []

# Load from all config*.yaml files
for conf in sorted(os.listdir(".")):
    if conf.startswith("config") and conf.endswith(".yaml"):
        try:
            with open(conf, "r", encoding="utf-8") as f:
                cdata = yaml.safe_load(f)
                account_name = cdata.get("account_name", conf)
                for p in cdata.get("pages", []):
                    all_pages.append({
                        "source": conf,
                        "account": account_name,
                        "page_id": str(p.get("page_id")),
                        "name": p.get("name"),
                        "drive_folder_id": p.get("drive_folder_id"),
                        "token": p.get("page_access_token")
                    })
        except Exception as e:
            print(f"Error reading {conf}: {e}")

# Also load USA Account 5 (Sejal Soni) from data/usa_account5_sejal_permanent_pages.json
sejal_path = "data/usa_account5_sejal_permanent_pages.json"
if os.path.exists(sejal_path):
    with open(sejal_path, "r", encoding="utf-8") as f:
        sdata = json.load(f)
        for p in sdata.get("pages", []):
            all_pages.append({
                "source": "usa_account5",
                "account": "USA Account 5 (Sejal Soni)",
                "page_id": str(p.get("page_id")),
                "name": p.get("name"),
                "drive_folder_id": p.get("drive_folder_id"),
                "token": ""
            })

print(f"Total collected pages for deep scan: {len(all_pages)}")

results = {}
total_valid_all = 0
total_zero_all = 0

for idx, p in enumerate(all_pages):
    fid = p.get("drive_folder_id")
    pname = p.get("name")
    pid = p.get("page_id")
    if not fid:
        print(f"[{idx+1}/{len(all_pages)}] {pname} (No folder ID)")
        continue
    
    try:
        # Fetch all files in folder
        files = []
        page_token = None
        q = f"'{fid}' in parents and trashed = false"
        while True:
            res = service.files().list(
                q=q,
                pageSize=1000,
                fields="nextPageToken, files(id, name, mimeType, size)",
                pageToken=page_token
            ).execute()
            files.extend(res.get("files", []))
            page_token = res.get("nextPageToken")
            if not page_token:
                break
        
        zero_files = [f for f in files if int(f.get("size") or 0) == 0]
        valid_files = [f for f in files if int(f.get("size") or 0) > 0 and (
            f.get("name", "").lower().endswith((".mp4", ".mov", ".m4v", ".avi", ".mkv")) or
            f.get("mimeType", "").startswith("video/")
        )]
        
        total_valid_all += len(valid_files)
        total_zero_all += len(zero_files)
        
        results[pid] = {
            "page_id": pid,
            "name": pname,
            "account": p.get("account"),
            "folder_id": fid,
            "total_files": len(files),
            "zero_byte_wiped": len(zero_files),
            "valid_videos_stock": len(valid_files),
            "status": "OK" if len(valid_files) > 0 else "EMPTY_STOCK"
        }
        
        if (idx + 1) % 15 == 0 or len(valid_files) == 0 or len(zero_files) > 0:
            print(f"[{idx+1}/{len(all_pages)}] {p['account']} | {pname}: {len(valid_files)} valid videos ({len(zero_files)} wiped 0-byte)")
            
    except Exception as e:
        print(f"[{idx+1}/{len(all_pages)}] ERROR {pname} ({fid}): {e}")
        results[pid] = {
            "page_id": pid,
            "name": pname,
            "account": p.get("account"),
            "folder_id": fid,
            "error": str(e)
        }

print("\n" + "="*60)
print(f"FINAL AUDIT SUMMARY ACROSS ALL {len(all_pages)} PAGES:")
print(f"Total Valid Unposted Playable Stock: {total_valid_all}")
print(f"Total Wiped 0-Byte Ghost Files: {total_zero_all}")
print("="*60)

with open("data/drive_verified_stock_audit.json", "w", encoding="utf-8") as out:
    json.dump({
        "timestamp": time.time(),
        "total_pages": len(all_pages),
        "total_valid_videos": total_valid_all,
        "total_zero_byte_wiped": total_zero_all,
        "pages": results
    }, out, indent=2)

print("Saved audit to data/drive_verified_stock_audit.json")
