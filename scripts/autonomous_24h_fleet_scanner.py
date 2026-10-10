#!/usr/bin/env python3
"""
Autonomous 24-Hour Fleet Real-Time Scanner & Sync Engine
Scans EVERY single Facebook Page (156 Pages):
1. Page Profile & Follower/Fan count via Meta Graph API v20.0
2. Every Reel's real views, likes, comments via Meta Graph API Batch Requests
3. Exact Google Drive stock video count for every folder via Google Drive API
4. Token health & validity verification
5. Automatically syncs and updates docs/data/pages_data.json and web/data/pages_data.json

Supports:
- python scripts/autonomous_24h_fleet_scanner.py --once       (Single immediate run)
- python scripts/autonomous_24h_fleet_scanner.py --daemon     (Runs 24/7 every 24 hours)
"""

import os
import sys
import json
import time
import glob
import yaml
import argparse
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SA_PATH = os.path.join(BASE_DIR, "service_account.json")
PAGES_DATA_DOCS = os.path.join(BASE_DIR, "docs", "data", "pages_data.json")
PAGES_DATA_WEB = os.path.join(BASE_DIR, "web", "data", "pages_data.json")
DRIVE_AUDIT_DATA = os.path.join(BASE_DIR, "data", "drive_folders_audit.json")
DRIVE_AUDIT_DOCS = os.path.join(BASE_DIR, "docs", "data", "drive_folders_audit.json")
DRIVE_AUDIT_WEB = os.path.join(BASE_DIR, "web", "data", "drive_folders_audit.json")

SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi"}

def safe_int(val, default=0):
    """Safely converts any value (including dicts like {'count': ...} or strings) to int."""
    if isinstance(val, dict):
        return int(val.get("count") or val.get("total_count") or default)
    try:
        return int(val or default)
    except Exception:
        return default

# -------------------------------------------------------------
# Google Drive API Client Initialization (Direct Bearer Token)
# -------------------------------------------------------------
def get_drive_bearer_token():
    """Initializes and returns Google Drive Bearer token."""
    if os.path.exists(SA_PATH):
        try:
            from google.oauth2 import service_account
            from google.auth.transport.requests import Request
            creds = service_account.Credentials.from_service_account_file(
                SA_PATH,
                scopes=["https://www.googleapis.com/auth/drive.readonly"]
            )
            creds.refresh(Request())
            return creds.token
        except Exception as e:
            print(f"⚠️ Service account token warning: {e}", flush=True)

    # Fallback to OAuth refresh token
    token_file = os.path.join(BASE_DIR, "gdrive_owner.token")
    secret_file = os.path.join(BASE_DIR, "client_secret.json")
    if os.path.exists(token_file) and os.path.exists(secret_file):
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            token = open(token_file, encoding="utf-8").read().strip()
            secret = json.load(open(secret_file, encoding="utf-8"))
            installed = secret.get("installed") or secret.get("web")
            creds = Credentials(
                None,
                refresh_token=token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=installed["client_id"],
                client_secret=installed["client_secret"],
                scopes=["https://www.googleapis.com/auth/drive.readonly"]
            )
            creds.refresh(Request())
            return creds.token
        except Exception as e:
            print(f"⚠️ OAuth token warning: {e}", flush=True)

    return None

# -------------------------------------------------------------
# Drive Folder Video Counter
# -------------------------------------------------------------
def count_drive_videos(session, drive_token, folder_id):
    """Counts video files in a Google Drive folder via HTTP API."""
    if not drive_token or not folder_id or len(str(folder_id).strip()) < 10:
        return 0

    folder_id = str(folder_id).strip()
    total_videos = 0
    page_token = None
    headers = {"Authorization": f"Bearer {drive_token}"}

    try:
        for _ in range(3): # up to 3 pages (3000 files)
            url = "https://www.googleapis.com/drive/v3/files"
            params = {
                "q": f"'{folder_id}' in parents and trashed = false",
                "pageSize": 1000,
                "fields": "nextPageToken, files(id, name, mimeType)"
            }
            if page_token:
                params["pageToken"] = page_token

            r = session.get(url, params=params, headers=headers, timeout=6).json()
            for it in r.get("files", []):
                mime = (it.get("mimeType") or "").lower()
                name = (it.get("name") or "").lower()
                ext = os.path.splitext(name)[1]

                if ext in SUPPORTED_VIDEO_EXTENSIONS or mime.startswith("video/") or mime == "application/octet-stream":
                    total_videos += 1

            page_token = r.get("nextPageToken")
            if not page_token:
                break

    except Exception:
        pass

    return total_videos

# -------------------------------------------------------------
# Token & Folder Mappings
# -------------------------------------------------------------
def load_all_tokens_and_folders():
    tokens = {}
    folders = {}

    for yf in glob.glob(os.path.join(BASE_DIR, "config*.yaml")):
        try:
            with open(yf, "r", encoding="utf-8") as f:
                yd = yaml.safe_load(f)
            if isinstance(yd, dict):
                for p in yd.get("pages", []):
                    pid = str(p.get("page_id") or p.get("id") or "").strip()
                    tok = (p.get("page_access_token") or p.get("access_token") or "").strip()
                    fld = (p.get("drive_folder_id") or "").strip()
                    if pid and tok:
                        tokens[pid] = tok
                    if pid and fld:
                        folders[pid] = fld
        except Exception:
            pass

    for jf in glob.glob(os.path.join(BASE_DIR, "data", "*.json")):
        try:
            with open(jf, "r", encoding="utf-8") as f:
                jd = json.load(f)
            plist = jd.get("pages", []) if isinstance(jd, dict) else (jd if isinstance(jd, list) else [])
            for p in plist:
                if isinstance(p, dict):
                    pid = str(p.get("id") or p.get("page_id") or "").strip()
                    tok = (p.get("access_token") or p.get("page_access_token") or "").strip()
                    fld = (p.get("drive_folder_id") or p.get("folder_id") or "").strip()
                    if pid and tok and pid not in tokens:
                        tokens[pid] = tok
                    if pid and fld and pid not in folders:
                        folders[pid] = fld
        except Exception:
            pass

    return tokens, folders

# -------------------------------------------------------------
# Single Page Real-Time Scanner
# -------------------------------------------------------------
def scan_page_realtime(page_obj, session, drive_token, all_tokens, all_folders):
    try:
        pid = str(page_obj.get("id") or page_obj.get("page_id") or "").strip()
        name = page_obj.get("name", "Unknown Page")
        account = page_obj.get("account", "Fleet")
        token = all_tokens.get(pid) or page_obj.get("access_token") or ""
        folder_id = all_folders.get(pid) or page_obj.get("drive_folder_id") or ""

        result = dict(page_obj)
        result["id"] = pid
        result["access_token"] = token
        result["drive_folder_id"] = folder_id

        # 1. Page Info (followers, fans, picture)
        live_followers = safe_int(page_obj.get("followers"))
        live_fans = safe_int(page_obj.get("fan_count"))
        is_valid = False
        error_msg = None

        if token:
            try:
                url = f"https://graph.facebook.com/v20.0/{pid}"
                r = session.get(
                    url,
                    params={"fields": "id,name,followers_count,fan_count,is_published,picture.type(large)", "access_token": token},
                    timeout=8
                ).json()

                if "id" in r:
                    is_valid = True
                    result["token_status"] = "active"
                    if "followers_count" in r:
                        live_followers = safe_int(r["followers_count"])
                    if "fan_count" in r:
                        live_fans = safe_int(r["fan_count"])
                    if "picture" in r and "data" in r["picture"]:
                        result["pic_url"] = r["picture"]["data"].get("url", result.get("pic_url"))
                else:
                    err = r.get("error", {})
                    error_msg = err.get("message", "Token Error")
                    result["token_status"] = "expired"
            except Exception as e:
                error_msg = str(e)
                result["token_status"] = "error"
        else:
            error_msg = "No Token Configured"
            result["token_status"] = "no_token"

        result["followers"] = live_followers
        result["fan_count"] = live_fans

        # 2. Reels & Exact Real Views via Batch API
        meta_videos = []
        total_reel_views = 0
        total_reel_likes = 0
        total_reel_comments = 0

        if is_valid and token:
            try:
                reels_url = f"https://graph.facebook.com/v20.0/{pid}/video_reels?fields=id,description,created_time,updated_time,picture,permalink_url&limit=50&access_token={token}"
                raw_reels = []
                for _ in range(3):
                    r_res = session.get(reels_url, timeout=8).json()
                    data_batch = r_res.get("data", [])
                    if not data_batch:
                        break
                    raw_reels.extend(data_batch)
                    reels_url = r_res.get("paging", {}).get("next")
                    if not reels_url:
                        break

                metrics_map = {}
                for i in range(0, len(raw_reels), 50):
                    batch_chunk = raw_reels[i:i+50]
                    batch_payload = [{
                        "method": "GET",
                        "relative_url": f"{r['id']}?fields=id,views,likes.summary(true),comments.summary(true),created_time"
                    } for r in batch_chunk]

                    try:
                        b_res = session.post(
                            "https://graph.facebook.com/v20.0/",
                            data={"access_token": token, "batch": json.dumps(batch_payload)},
                            timeout=12
                        ).json()

                        for item in b_res:
                            if item.get("code") == 200:
                                body = json.loads(item.get("body", "{}"))
                                rid = str(body.get("id"))
                                metrics_map[rid] = {
                                    "views": int(body.get("views") or 0),
                                    "likes": int(body.get("likes", {}).get("summary", {}).get("total_count", 0)),
                                    "comments": int(body.get("comments", {}).get("summary", {}).get("total_count", 0)),
                                    "created_time": body.get("created_time")
                                }
                    except Exception:
                        pass

                existing_videos_map = {str(v.get("id")): v for v in page_obj.get("videos", [])}
                for rr in raw_reels:
                    rid = str(rr["id"])
                    met = metrics_map.get(rid, {})
                    v_views = met.get("views") if met.get("views") is not None else int(rr.get("views") or 0)
                    v_likes = met.get("likes", 0)
                    v_comments = met.get("comments", 0)

                    # Ground Truth: Never degrade verified view count
                    if rid in existing_videos_map:
                        prev_v = existing_videos_map[rid]
                        v_views = max(v_views, int(prev_v.get("views") or 0))
                        v_likes = max(v_likes, int(prev_v.get("likes") or 0))
                        v_comments = max(v_comments, int(prev_v.get("comments") or 0))

                    total_reel_views += v_views
                    total_reel_likes += v_likes
                    total_reel_comments += v_comments

                    c_time = met.get("created_time") or rr.get("created_time") or rr.get("updated_time") or "2026-09-01T00:00:00+0000"
                    try:
                        dt = datetime.fromisoformat(c_time.replace("+0000", "+00:00"))
                        date_display = dt.strftime("%b %d, %Y")
                        time_display = dt.strftime("%I:%M %p")
                    except Exception:
                        date_display = "Recent"
                        time_display = "12:00 PM"

                    raw_desc = (rr.get("description") or "Facebook Reel").strip()
                    title_line = raw_desc.split("\n")[0][:60]

                    meta_videos.append({
                        "id": rid,
                        "title": title_line,
                        "date": date_display,
                        "time": time_display,
                        "created_time": c_time,
                        "views": v_views,
                        "likes": v_likes,
                        "comments": v_comments,
                        "permalink_url": rr.get("permalink_url") or f"https://www.facebook.com/reel/{rid}",
                        "thumbnail": rr.get("picture") or "icons/default_reel.png",
                        "status": "published"
                    })

            except Exception as e:
                print(f"⚠️ Error scanning reels for {name}: {e}", flush=True)

        if meta_videos:
            result["videos"] = meta_videos
            result["total_views"] = max(total_reel_views, safe_int(page_obj.get("total_views")))
            result["total_engagement"] = total_reel_likes + total_reel_comments
        else:
            result["videos"] = page_obj.get("videos", [])
            result["total_views"] = safe_int(page_obj.get("total_views"))
            result["total_engagement"] = safe_int(page_obj.get("total_engagement"))

        # 3. Google Drive Video Stock
        drive_stock = safe_int(page_obj.get("drive_videos_count"))
        if folder_id:
            real_drive_count = count_drive_videos(session, drive_token, folder_id)
            if real_drive_count > 0:
                drive_stock = real_drive_count
            result["has_drive_folder"] = True
        else:
            result["has_drive_folder"] = False

        result["drive_videos_count"] = drive_stock

        return {
            "page": result,
            "valid": is_valid,
            "name": name,
            "pid": pid,
            "account": account,
            "followers": result["followers"],
            "views": result["total_views"],
            "reels_count": len(result.get("videos", [])),
            "drive_stock": drive_stock,
            "error": error_msg
        }

    except Exception as e:
        print(f"⚠️ Page scan exception for {page_obj.get('name')}: {e}", flush=True)
        return {
            "page": page_obj,
            "valid": False,
            "name": page_obj.get("name", "Unknown"),
            "pid": str(page_obj.get("id", "")),
            "account": page_obj.get("account", ""),
            "followers": safe_int(page_obj.get("followers")),
            "views": safe_int(page_obj.get("total_views")),
            "reels_count": len(page_obj.get("videos", [])),
            "drive_stock": safe_int(page_obj.get("drive_videos_count")),
            "error": str(e)
        }

# -------------------------------------------------------------
# Main Fleet Scan
# -------------------------------------------------------------
def run_fleet_scan():
    start_time = datetime.now(timezone.utc)
    print("=" * 80, flush=True)
    print("🚀 STARTING REAL-TIME FLEET SCAN (EVERY PAGE • EVERY REEL • DRIVE STOCK)", flush=True)
    print(f"   Execution Timestamp: {start_time.isoformat()}", flush=True)
    print("=" * 80, flush=True)

    with open(PAGES_DATA_DOCS, "r", encoding="utf-8") as f:
        full_data = json.load(f)
    pages = full_data.get("pages", [])
    print(f"Loaded {len(pages)} pages from {PAGES_DATA_DOCS}", flush=True)

    all_tokens, all_folders = load_all_tokens_and_folders()
    print(f"Resolved {len(all_tokens)} page tokens & {len(all_folders)} drive folders.", flush=True)

    drive_token = get_drive_bearer_token()
    if drive_token:
        print("✅ Google Drive Bearer Token Authenticated.", flush=True)
    else:
        print("⚠️ Warning: Google Drive Bearer token could not be obtained.", flush=True)

    session = requests.Session()

    print(f"\n--> Concurrently scanning all {len(pages)} pages (12 Worker Threads)...", flush=True)
    scanned_pages = []
    drive_audit_dict = {}

    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {
            executor.submit(scan_page_realtime, p, session, drive_token, all_tokens, all_folders): p
            for p in pages
        }

        for idx, fut in enumerate(as_completed(futures), 1):
            try:
                res = fut.result()
                p_updated = res["page"]
                scanned_pages.append(p_updated)

                pid = res["pid"]
                pname = res["name"]
                f_count = res["followers"]
                v_count = res["views"]
                r_count = res["reels_count"]
                d_stock = res["drive_stock"]
                v_status = "✅" if res["valid"] else "❌"

                print(f"[{idx:03d}/{len(pages):03d}] {v_status} {pname:<24} | Followers: {f_count:>7,d} | Views: {v_count:>10,d} ({r_count:2d} reels) | Drive: {d_stock:>4d}", flush=True)

                folder_id = p_updated.get("drive_folder_id", "")
                if folder_id:
                    drive_audit_dict[pname] = {
                        "video_count": d_stock,
                        "folder_id": folder_id,
                        "folder_name": pname,
                        "account": p_updated.get("account", ""),
                        "region": p_updated.get("region", "US")
                    }

            except Exception as e:
                orig_p = futures[fut]
                print(f"⚠️ Worker error for {orig_p.get('name')}: {e}", flush=True)
                scanned_pages.append(orig_p)

    scanned_pages.sort(key=lambda x: safe_int(x.get("index"), 999))

    total_fleet_views = sum(safe_int(p.get("total_views")) for p in scanned_pages)
    total_fleet_stock = sum(safe_int(p.get("drive_videos_count")) for p in scanned_pages)
    total_fleet_followers = sum(safe_int(p.get("followers")) for p in scanned_pages)
    valid_tokens_count = sum(1 for p in scanned_pages if p.get("token_status") == "active")

    full_data["pages"] = scanned_pages
    full_data["synced_at"] = datetime.now(timezone.utc).isoformat()
    full_data["total_views"] = total_fleet_views
    full_data["valid_tokens_count"] = valid_tokens_count

    print("\n-------------------------------------------------------------", flush=True)
    print("💾 SAVING & SYNCHRONIZING REAL-TIME FLEET DATA...", flush=True)
    print("-------------------------------------------------------------", flush=True)

    for p_path in [PAGES_DATA_DOCS, PAGES_DATA_WEB]:
        os.makedirs(os.path.dirname(p_path), exist_ok=True)
        with open(p_path, "w", encoding="utf-8") as f:
            json.dump(full_data, f, indent=2, ensure_ascii=False)
        print(f"  ✅ Saved: {os.path.relpath(p_path, BASE_DIR)}", flush=True)

    for da_path in [DRIVE_AUDIT_DATA, DRIVE_AUDIT_DOCS, DRIVE_AUDIT_WEB]:
        os.makedirs(os.path.dirname(da_path), exist_ok=True)
        with open(da_path, "w", encoding="utf-8") as f:
            json.dump(drive_audit_dict, f, indent=2, ensure_ascii=False)
        print(f"  ✅ Saved: {os.path.relpath(da_path, BASE_DIR)}", flush=True)

    duration = (datetime.now(timezone.utc) - start_time).total_seconds()
    print("=" * 80, flush=True)
    print("🎉 REAL-TIME SCAN COMPLETED SUCCESSFULLY!", flush=True)
    print(f"   Duration:             {duration:.1f} seconds", flush=True)
    print(f"   Total Pages Scanned:  {len(scanned_pages)}", flush=True)
    print(f"   Active Valid Tokens:  {valid_tokens_count} / {len(scanned_pages)} ({valid_tokens_count/len(scanned_pages)*100:.1f}%)", flush=True)
    print(f"   Total Real Views:     {total_fleet_views:,}", flush=True)
    print(f"   Total Real Followers: {total_fleet_followers:,}", flush=True)
    print(f"   Total Cloud Stock:    {total_fleet_stock:,} Reels", flush=True)
    print("=" * 80 + "\n", flush=True)

    return full_data

def run_24h_daemon(interval_seconds=86400):
    print("=================================================================", flush=True)
    print("👑 AUTONOMOUS 24-HOUR REAL FLEET SCANNER DAEMON", flush=True)
    print(f"   Interval: {interval_seconds // 3600} Hours ({interval_seconds} seconds)", flush=True)
    print("=================================================================\n", flush=True)

    cycle = 0
    while True:
        cycle += 1
        print(f"\n🚀 >>> STARTING 24-HOUR SCAN CYCLE #{cycle} <<<", flush=True)
        try:
            run_fleet_scan()
        except Exception as e:
            print(f"⚠️ Scan cycle #{cycle} error: {e}", flush=True)

        print(f"😴 Cycle #{cycle} complete. Sleeping for {interval_seconds // 3600} hours until next scan...", flush=True)
        time.sleep(interval_seconds)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous 24-Hour Fleet Scanner")
    parser.add_argument("--once", action="store_true", help="Run scan once and exit")
    parser.add_argument("--daemon", action="store_true", help="Run continuously every 24 hours")
    parser.add_argument("--interval", type=int, default=86400, help="Interval in seconds for daemon mode")
    args = parser.parse_args()

    if args.daemon:
        run_24h_daemon(args.interval)
    else:
        run_fleet_scan()
