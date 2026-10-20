import json
import os
import re
import sys
import time
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from google.oauth2 import service_account
from googleapiclient.discovery import build

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Thread-local storage for Drive API clients
thread_local = threading.local()

def get_drive_service(creds):
    if not hasattr(thread_local, "service"):
        thread_local.service = build("drive", "v3", credentials=creds, cache_discovery=False)
    return thread_local.service

def scan_single_folder(item, creds):
    fid = item["folder_id"]
    pname = item["page_name"]
    acc = item["account"]
    pid = item["page_id"]
    video_exts = (".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm")

    service = get_drive_service(creds)
    q = f"'{fid}' in parents and trashed = false"

    for attempt in range(3):
        try:
            files = []
            page_token = None
            while True:
                res = service.files().list(
                    q=q,
                    pageSize=1000,
                    fields="nextPageToken, files(id, name, mimeType, size)",
                    pageToken=page_token,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True
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

            status = "HEALTHY"
            if v_count == 0:
                status = "EMPTY"
            elif v_count <= 5:
                status = "CRITICAL"
            elif v_count <= 15:
                status = "LOW"

            return {
                "page_id": pid,
                "page_name": pname,
                "account": acc,
                "folder_id": fid,
                "video_count": v_count,
                "zero_byte_wiped": z_count,
                "total_files": len(files),
                "status": status,
                "error": None
            }
        except Exception as e:
            if attempt < 2:
                time.sleep(1 + attempt)
                continue
            return {
                "page_id": pid,
                "page_name": pname,
                "account": acc,
                "folder_id": fid,
                "video_count": 0,
                "zero_byte_wiped": 0,
                "total_files": 0,
                "status": "ERROR",
                "error": str(e)
            }

def update_gold_app_js_stock(results_by_pid):
    """Update videoCount in DRIVE_CONFIGURED_PAGES inside docs/js/gold_app.js and web/js/gold_app.js"""
    for js_path in ["docs/js/gold_app.js", "web/js/gold_app.js"]:
        if not os.path.exists(js_path):
            continue
        try:
            with open(js_path, "r", encoding="utf-8") as f:
                content = f.read()

            modified = False
            for pid, res in results_by_pid.items():
                v_count = res["video_count"]
                # Match entry for this pid: "907450442461718": { ... videoCount: 67, ... }
                pattern = re.compile(rf'("{pid}":\s*\{{[^}}]*?videoCount:\s*)(\d+)([^}}]*\}})')
                m = pattern.search(content)
                if m and int(m.group(2)) != v_count:
                    content = pattern.sub(rf'\g<1>{v_count}\g<3>', content)
                    modified = True

            if modified:
                with open(js_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Updated videoCount in {js_path}")
        except Exception as e:
            print(f"Error updating {js_path}: {e}")

def run_live_drive_audit():
    sa_path = "service_account.json"
    if not os.path.exists(sa_path):
        print(f"ERROR: {sa_path} not found!")
        return

    print("Connecting to Google Drive API v3 via Service Account...")
    creds = service_account.Credentials.from_service_account_file(
        sa_path, scopes=["https://www.googleapis.com/auth/drive"]
    )

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
                    y = yaml.safe_load(cf) or {}
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

    print(f"Starting parallel deep scan of {len(audit_queue)} Google Drive folders (8 workers)...")

    results_by_pid = {}
    results_by_fid = {}
    folder_results = {}
    empty_folders = []
    critical_folders = []
    low_folders = []
    healthy_folders = []

    total_valid_stock = 0
    total_zero_byte = 0

    start_time = time.time()
    completed_count = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(scan_single_folder, item, creds): item for item in audit_queue}
        for future in as_completed(futures):
            res = future.result()
            completed_count += 1
            pid = res["page_id"]
            fid = res["folder_id"]
            pname = res["page_name"]
            v_count = res["video_count"]
            z_count = res["zero_byte_wiped"]
            status = res["status"]

            results_by_pid[pid] = res
            results_by_fid[fid] = res
            folder_results[pname] = res

            total_valid_stock += v_count
            total_zero_byte += z_count

            if status == "EMPTY":
                empty_folders.append(res)
            elif status == "CRITICAL":
                critical_folders.append(res)
            elif status == "LOW":
                low_folders.append(res)
            else:
                healthy_folders.append(res)

            if completed_count % 30 == 0 or completed_count == len(audit_queue) or v_count <= 5:
                print(f"[{completed_count}/{len(audit_queue)}] {pname} ({res['account']}): {v_count} valid ({z_count} wiped) -> {status}")

    elapsed = time.time() - start_time
    print(f"\nAudit completed in {elapsed:.1f}s")
    print("="*65)
    print("GOOGLE DRIVE LIVE STOCK DEEP AUDIT RESULTS")
    print("="*65)
    print(f"Total Folders Scanned: {len(audit_queue)}")
    print(f"Total Valid Playable Stock: {total_valid_stock:,} videos")
    print(f"Total Wiped 0-Byte Ghost Files: {total_zero_byte:,} files")
    print(f"Empty Folders (0 valid videos): {len(empty_folders)}")
    print(f"Critical Stock Folders (1 to 5 videos): {len(critical_folders)}")
    print(f"Low Stock Folders (6 to 15 videos): {len(low_folders)}")
    print(f"Healthy Stock Folders (>15 videos): {len(healthy_folders)}")

    # Sort reports
    empty_folders.sort(key=lambda x: x["page_name"])
    critical_folders.sort(key=lambda x: x["video_count"])
    low_folders.sort(key=lambda x: x["video_count"])

    if empty_folders:
        print("\n--- 🔴 EMPTY FOLDERS (0 VIDEOS - IMMEDIATE REFILL NEEDED) ---")
        for ef in empty_folders:
            print(f"  🔴 {ef['page_name']} ({ef['account']}): 0 valid videos | {ef['zero_byte_wiped']} wiped | Folder: {ef['folder_id']}")

    if critical_folders:
        print("\n--- ⚠️ CRITICAL STOCK FOLDERS (1 TO 5 VIDEOS) ---")
        for cf in critical_folders:
            print(f"  ⚠️ {cf['page_name']} ({cf['account']}): {cf['video_count']} videos remaining | Folder: {cf['folder_id']}")

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
            "folders": folder_results,
            "by_page_id": results_by_pid
        }, out, indent=2, ensure_ascii=False)
    print("\nSaved report to data/drive_verified_stock_audit.json")

    # Update drive_folders_audit.json in data/, docs/data/, web/data/
    drive_audit_dict = {}
    for pid, info in results_by_pid.items():
        name = info["page_name"]
        drive_audit_dict[name] = {
            "page_id": pid,
            "video_count": info.get("video_count", 0),
            "zero_byte_wiped": info.get("zero_byte_wiped", 0),
            "folder_id": info.get("folder_id"),
            "folder_name": name,
            "account": info.get("account"),
            "status": info.get("status")
        }

    for target_dir in ["data", "docs/data", "web/data"]:
        tpath = os.path.join(target_dir, "drive_folders_audit.json")
        with open(tpath, "w", encoding="utf-8") as out:
            json.dump(drive_audit_dict, out, indent=2, ensure_ascii=False)
        print(f"Saved {tpath}")

    # Update pages_data.json with exact drive_videos_count
    for p in pages:
        pid = str(p.get("id"))
        fid = p.get("drive_folder_id")
        pname = p.get("name")
        matching = results_by_pid.get(pid) or results_by_fid.get(fid) or folder_results.get(pname)
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

    # Update DRIVE_CONFIGURED_PAGES in gold_app.js files
    update_gold_app_js_stock(results_by_pid)

    print("\n✅ LIVE AUDIT AND DATA SYNCHRONIZATION COMPLETE!")

if __name__ == "__main__":
    run_live_drive_audit()
