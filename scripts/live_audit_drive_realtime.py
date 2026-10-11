import json
import os
import sys
import time
import yaml
from google.oauth2 import service_account
from googleapiclient.discovery import build

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_live_drive_audit():
    sa_path = "service_account.json"
    if not os.path.exists(sa_path):
        print(f"ERROR: {sa_path} not found!")
        return

    print("Connecting to Google Drive API v3 via Service Account...")
    creds = service_account.Credentials.from_service_account_file(
        sa_path, scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build("drive", "v3", credentials=creds, cache_discovery=False)

    # 1. Load all pages from docs/data/pages_data.json as master reference
    pages_file = "docs/data/pages_data.json"
    with open(pages_file, "r", encoding="utf-8") as f:
        pdata = json.load(f)
    pages = pdata.get("pages", [])

    print(f"Loaded {len(pages)} pages from pages_data.json")

    # 2. Also map folder IDs from all config*.yaml files
    folder_map = {}
    for conf in sorted(os.listdir(".")):
        if conf.startswith("config") and conf.endswith(".yaml"):
            try:
                with open(conf, "r", encoding="utf-8") as cf:
                    y = yaml.safe_load(cf)
                    for cp in y.get("pages", []):
                        pid = str(cp.get("page_id"))
                        fid = cp.get("drive_folder_id")
                        if fid and not fid.startswith("REPLACE_WITH"):
                            folder_map[pid] = fid
            except Exception as e:
                print(f"Error reading {conf}: {e}")

    # Build unique list of folders to audit
    audit_queue = []
    seen_fids = set()

    for p in pages:
        pid = str(p.get("id"))
        fid = p.get("drive_folder_id") or folder_map.get(pid)
        if fid and fid not in seen_fids:
            seen_fids.add(fid)
            audit_queue.append({
                "page_id": pid,
                "page_name": p.get("name"),
                "account": p.get("account"),
                "folder_id": fid
            })

    print(f"Unique Google Drive folders to audit: {len(audit_queue)}")

    total_valid_stock = 0
    total_zero_byte = 0
    folder_results = {}
    empty_folders = []
    critical_folders = []
    low_folders = []
    healthy_folders = []

    video_exts = (".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm")

    start_time = time.time()
    for idx, item in enumerate(audit_queue, 1):
        fid = item["folder_id"]
        pname = item["page_name"]
        acc = item["account"]
        pid = item["page_id"]

        try:
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
                f.get("name", "").lower().endswith(video_exts) or
                f.get("mimeType", "").startswith("video/")
            )]

            v_count = len(valid_files)
            z_count = len(zero_files)
            total_valid_stock += v_count
            total_zero_byte += z_count

            status = "HEALTHY"
            if v_count == 0:
                status = "EMPTY"
                empty_folders.append({**item, "valid": v_count, "wiped": z_count, "total": len(files)})
            elif v_count <= 5:
                status = "CRITICAL"
                critical_folders.append({**item, "valid": v_count, "wiped": z_count, "total": len(files)})
            elif v_count <= 15:
                status = "LOW"
                low_folders.append({**item, "valid": v_count, "wiped": z_count, "total": len(files)})
            else:
                healthy_folders.append({**item, "valid": v_count, "wiped": z_count, "total": len(files)})

            folder_results[pname] = {
                "page_id": pid,
                "page_name": pname,
                "account": acc,
                "folder_id": fid,
                "video_count": v_count,
                "zero_byte_wiped": z_count,
                "total_files": len(files),
                "status": status
            }

            if idx % 25 == 0 or idx == len(audit_queue) or v_count <= 5:
                print(f"[{idx}/{len(audit_queue)}] {pname} ({acc}): {v_count} valid videos ({z_count} wiped) -> {status}")

        except Exception as e:
            print(f"[{idx}/{len(audit_queue)}] ERROR on {pname} ({fid}): {e}")
            folder_results[pname] = {
                "page_id": pid,
                "page_name": pname,
                "account": acc,
                "folder_id": fid,
                "video_count": 0,
                "error": str(e),
                "status": "ERROR"
            }
            empty_folders.append({**item, "valid": 0, "wiped": 0, "total": 0, "error": str(e)})

    elapsed = time.time() - start_time
    print(f"\nAudit completed in {elapsed:.1f}s")
    print("="*60)
    print("GOOGLE DRIVE LIVE STOCK AUDIT RESULTS")
    print("="*60)
    print(f"Total Folders Scanned: {len(audit_queue)}")
    print(f"Total Valid Unposted Playable Stock: {total_valid_stock:,} videos")
    print(f"Total Wiped 0-Byte Ghost Files: {total_zero_byte:,} files")
    print(f"Empty Folders (0 valid videos): {len(empty_folders)}")
    print(f"Critical Stock Folders (1 to 5 videos): {len(critical_folders)}")
    print(f"Low Stock Folders (6 to 15 videos): {len(low_folders)}")
    print(f"Healthy Stock Folders (>15 videos): {len(healthy_folders)}")

    print("\n--- 🔴 EMPTY FOLDERS (0 VIDEOS - IMMEDIATE REFILL NEEDED) ---")
    for ef in empty_folders:
        print(f"  🔴 {ef['page_name']} ({ef['account']}): 0 valid videos | {ef.get('wiped', 0)} wiped | Folder ID: {ef['folder_id']}")

    print("\n--- ⚠️ CRITICAL STOCK FOLDERS (1 TO 5 VIDEOS) ---")
    for cf in critical_folders:
        print(f"  ⚠️ {cf['page_name']} ({cf['account']}): {cf['valid']} videos remaining | Folder ID: {cf['folder_id']}")

    print("\n--- 🟡 LOW STOCK FOLDERS (6 TO 15 VIDEOS) ---")
    for lf in low_folders:
        print(f"  🟡 {lf['page_name']} ({lf['account']}): {lf['valid']} videos remaining | Folder ID: {lf['folder_id']}")

    # Save to data/drive_verified_stock_audit.json
    with open("data/drive_verified_stock_audit.json", "w", encoding="utf-8") as out:
        json.dump({
            "updated_at": time.time(),
            "total_folders": len(audit_queue),
            "total_valid_stock": total_valid_stock,
            "total_zero_byte": total_zero_byte,
            "empty_count": len(empty_folders),
            "critical_count": len(critical_folders),
            "low_count": len(low_folders),
            "healthy_count": len(healthy_folders),
            "empty_folders": empty_folders,
            "critical_folders": critical_folders,
            "low_folders": low_folders,
            "folders": folder_results
        }, out, indent=2, ensure_ascii=False)
    print("\nSaved report to data/drive_verified_stock_audit.json")

    # Update docs/data/drive_folders_audit.json and web/data/drive_folders_audit.json
    drive_audit_dict = {}
    for name, info in folder_results.items():
        drive_audit_dict[name] = {
            "video_count": info.get("video_count", 0),
            "zero_byte_wiped": info.get("zero_byte_wiped", 0),
            "folder_id": info.get("folder_id"),
            "folder_name": name,
            "account": info.get("account"),
            "status": info.get("status")
        }

    for target_dir in ["docs/data", "web/data"]:
        tpath = os.path.join(target_dir, "drive_folders_audit.json")
        with open(tpath, "w", encoding="utf-8") as out:
            json.dump(drive_audit_dict, out, indent=2, ensure_ascii=False)
        print(f"Saved {tpath}")

    # Update pages_data.json with exact drive_videos_count
    for p in pages:
        pname = p.get("name")
        pid = str(p.get("id"))
        matching = folder_results.get(pname)
        if not matching:
            # try finding by page_id
            for r in folder_results.values():
                if str(r.get("page_id")) == pid:
                    matching = r
                    break
        if matching:
            p["drive_videos_count"] = matching.get("video_count", 0)
            p["drive_zero_wiped"] = matching.get("zero_byte_wiped", 0)
            p["drive_stock_status"] = matching.get("status", "HEALTHY")

    pdata["pages"] = pages
    pdata["portfolio"]["total_stock_videos"] = total_valid_stock

    for target_dir in ["docs/data", "web/data"]:
        tpath = os.path.join(target_dir, "pages_data.json")
        with open(tpath, "w", encoding="utf-8") as out:
            json.dump(pdata, out, indent=2, ensure_ascii=False)
        print(f"Saved {tpath}")

    print("\n✅ LIVE AUDIT AND DATA SYNCHRONIZATION COMPLETE!")

if __name__ == "__main__":
    run_live_drive_audit()
