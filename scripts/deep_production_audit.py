#!/usr/bin/env python3
"""
Deep Production Pipeline & Real-Time Sync Auditor
Checks:
1. Upload Timing & Frequency across all accounts (Last post, Today's posts, Slots status)
2. App Sync Mode & Real-Time Telemetry Flow (Sync endpoints, pages_data.json freshness, live views)
3. Deep Scan of All 156 Pages (Tokens, Drive Folders, Unposted Stock, Zero-Stock Gaps)
4. Pipeline Health & Blocking Issues
"""

import os
import sys
import json
import glob
import sqlite3
import yaml
import requests
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "posted_videos.db")
PAGES_DATA_PATH = os.path.join(BASE_DIR, "docs", "data", "pages_data.json")

def load_master_data():
    with open(PAGES_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    pages = data.get("pages", [])
    
    # Load tokens from YAMLs and json token files
    cfg_tokens = {}
    cfg_folders = {}
    for yml in glob.glob(os.path.join(BASE_DIR, "*.yaml")):
        try:
            with open(yml, "r", encoding="utf-8") as f:
                yd = yaml.safe_load(f)
                if isinstance(yd, dict):
                    for p in yd.get("pages", []):
                        pid = str(p.get("page_id") or p.get("id") or "")
                        tok = p.get("page_access_token") or p.get("access_token")
                        fld = p.get("drive_folder_id")
                        if pid and tok: cfg_tokens[pid] = tok
                        if pid and fld: cfg_folders[pid] = fld
        except Exception:
            pass

    for dfile in glob.glob(os.path.join(BASE_DIR, "data", "*.json")):
        try:
            with open(dfile, "r", encoding="utf-8") as f:
                ddata = json.load(f)
                plist = ddata.get("pages", []) if isinstance(ddata, dict) else (ddata if isinstance(ddata, list) else [])
                for p in plist:
                    if isinstance(p, dict):
                        pid = str(p.get("id") or p.get("page_id") or "")
                        tok = p.get("access_token") or p.get("page_access_token")
                        fld = p.get("drive_folder_id") or p.get("folder_id")
                        if pid and tok and pid not in cfg_tokens: cfg_tokens[pid] = tok
                        if pid and fld and pid not in cfg_folders: cfg_folders[pid] = fld
        except Exception:
            pass

    return pages, cfg_tokens, cfg_folders, data

def audit_account_upload_timing():
    print("="*80)
    print("1. ACCOUNT-WISE UPLOADING TIMING & SLOT STATUS")
    print("="*80)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check latest uploads overall
    c.execute("SELECT max(posted_at), min(posted_at), count(*) FROM videos WHERE status = 'posted'")
    max_post, min_post, total_posts = c.fetchone()
    print(f"  • DB Lifetime Posts: {total_posts:,} videos")
    print(f"  • Latest Upload in DB: {max_post}")
    
    # Get last post per page from DB
    c.execute("SELECT page_id, max(posted_at), count(*) FROM videos WHERE status = 'posted' GROUP BY page_id")
    page_last_post = {str(row[0]): (row[1], row[2]) for row in c.fetchall()}
    conn.close()
    
    pages, cfg_tokens, cfg_folders, full_data = load_master_data()
    
    # Group pages by account
    accounts = {}
    for p in pages:
        acc = p.get("account", "Unknown")
        accounts.setdefault(acc, []).append(p)
        
    for acc_name, acc_pages in sorted(accounts.items()):
        total_p = len(acc_pages)
        today_up = sum(p.get("today_posts", 0) for p in acc_pages)
        target = total_p * 4
        
        # Check last upload timestamp across this account's pages
        latest_ts = None
        pages_with_posts = 0
        for p in acc_pages:
            pid = str(p.get("id"))
            if pid in page_last_post:
                ts, cnt = page_last_post[pid]
                pages_with_posts += 1
                if not latest_ts or ts > latest_ts:
                    latest_ts = ts
                    
        pct = (today_up / target * 100) if target > 0 else 0
        status_flag = "✅ ON SCHEDULE" if today_up > 0 else "⚠️ PENDING / ZERO TODAY"
        print(f"  [{status_flag:20s}] {acc_name:24s} | Slots: {today_up:2d}/{target:2d} ({pct:2.0f}%) | Last Upload: {latest_ts or 'Never'}")
        
    return page_last_post

def audit_app_sync_and_realtime_flow():
    print("\n" + "="*80)
    print("2. APP SYNC MODE & REAL-TIME DATA FLOW AUDIT")
    print("="*80)
    pages, cfg_tokens, cfg_folders, full_data = load_master_data()
    
    synced_at = full_data.get("synced_at")
    print(f"  • pages_data.json Last Synchronized: {synced_at}")
    
    # Check if synced_at exists and is valid
    if synced_at:
        try:
            sync_dt = datetime.fromisoformat(synced_at.replace("Z", "+00:00"))
            print(f"    -> Sync Timestamp Verified: {sync_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        except Exception as e:
            print(f"    ⚠️ Could not parse synced_at: {e}")
            
    # Check total views & real-time fields in pages_data.json
    total_views = sum(int(p.get("total_views") or 0) for p in pages)
    total_followers = sum(int(p.get("followers") or 0) for p in pages)
    pages_with_views = sum(1 for p in pages if int(p.get("total_views") or 0) > 0)
    pages_with_followers = sum(1 for p in pages if int(p.get("followers") or 0) > 0)
    
    print(f"  • Pages with Real-Time Views: {pages_with_views} / {len(pages)} ({pages_with_views/len(pages)*100:.1f}%)")
    print(f"  • Pages with Follower Data:   {pages_with_followers} / {len(pages)} ({pages_with_followers/len(pages)*100:.1f}%)")
    print(f"  • Total Real-Time Views Aggregated: {total_views:,}")
    print(f"  • Total Followers Aggregated:       {total_followers:,}")
    
    # Check sync_views.yml workflow
    sync_yml_path = os.path.join(BASE_DIR, ".github", "workflows", "sync_views.yml")
    if os.path.exists(sync_yml_path):
        print("  • Automated Real-Time Sync Workflow: ✅ ACTIVE (.github/workflows/sync_views.yml)")
    else:
        print("  • Automated Real-Time Sync Workflow: ❌ MISSING")

def deep_scan_all_156_pages_and_gaps():
    print("\n" + "="*80)
    print("3. DEEP SCAN OF ALL 156 PAGES & PIPELINE GAP DETECTION")
    print("="*80)
    pages, cfg_tokens, cfg_folders, full_data = load_master_data()
    
    gaps = []
    zero_stock_pages = []
    missing_folder_pages = []
    missing_token_pages = []
    invalid_token_pages = []
    
    def verify_page(p):
        pid = str(p.get("id"))
        name = p.get("name", "Unknown")
        acc = p.get("account", "Unknown")
        tok = cfg_tokens.get(pid) or p.get("access_token")
        fld = cfg_folders.get(pid) or p.get("drive_folder_id")
        stock = int(p.get("drive_videos_count") or p.get("videos_count") or 0)
        
        info = {
            "id": pid, "name": name, "account": acc, "has_token": bool(tok),
            "has_folder": bool(fld), "stock": stock, "token_valid": False, "error": None
        }
        
        if not fld:
            info["error"] = "Missing Google Drive Folder ID"
            return info
        if stock <= 0:
            info["error"] = "0 Stock in Google Drive"
            
        if not tok:
            info["error"] = (info["error"] + " + " if info["error"] else "") + "No Token Configured"
            return info
            
        # Test token against Meta Graph API
        try:
            r = requests.get(f"https://graph.facebook.com/v20.0/{pid}", params={"fields": "id,name,is_published", "access_token": tok}, timeout=5).json()
            if "id" in r:
                info["token_valid"] = True
            else:
                err = r.get("error", {})
                info["error"] = (info["error"] + " + " if info["error"] else "") + f"Meta API [{err.get('code')}]: {err.get('message', '')[:40]}"
        except Exception as e:
            info["error"] = (info["error"] + " + " if info["error"] else "") + f"Net Error: {str(e)[:30]}"
            
        return info

    print(f"--> Scanning all {len(pages)} pages across Meta Graph API and Drive linkages (16 threads)...")
    with ThreadPoolExecutor(max_workers=16) as pool:
        scan_results = list(pool.map(verify_page, pages))
        
    for r in scan_results:
        if not r["has_folder"]:
            missing_folder_pages.append(r)
        if r["stock"] <= 0:
            zero_stock_pages.append(r)
        if not r["has_token"]:
            missing_token_pages.append(r)
        elif not r["token_valid"]:
            invalid_token_pages.append(r)
            
    print(f"\n[SCAN RESULTS SUMMARY]:")
    print(f"  • Total Pages Scanned:           {len(pages)}")
    print(f"  • Valid & Ready Pages:           {sum(1 for r in scan_results if r['token_valid'] and r['stock'] > 0 and r['has_folder'])} / {len(pages)}")
    print(f"  • Pages with Missing Folder ID:  {len(missing_folder_pages)}")
    print(f"  • Pages with 0 Video Stock:      {len(zero_stock_pages)}")
    print(f"  • Pages with Missing Token:      {len(missing_token_pages)}")
    print(f"  • Pages with Invalid Meta Token: {len(invalid_token_pages)}")
    
    if missing_token_pages:
        print(f"\n⚠️ Pages Missing Tokens ({len(missing_token_pages)}):")
        for p in missing_token_pages:
            print(f"    - {p['name']} ({p['account']}) ID: {p['id']}")
            
    if invalid_token_pages:
        print(f"\n⚠️ Pages with Invalid Tokens ({len(invalid_token_pages)}):")
        for p in invalid_token_pages:
            print(f"    - {p['name']} ({p['account']}) ID: {p['id']} | Error: {p['error']}")

    if zero_stock_pages:
        print(f"\n⚠️ Pages with 0 Stock ({len(zero_stock_pages)}):")
        for p in zero_stock_pages:
            print(f"    - {p['name']} ({p['account']}) ID: {p['id']}")

    return scan_results

if __name__ == "__main__":
    audit_account_upload_timing()
    audit_app_sync_and_realtime_flow()
    deep_scan_all_156_pages_and_gaps()
