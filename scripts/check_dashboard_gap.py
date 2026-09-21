import os
import sys
import json
import sqlite3
import requests
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("="*65)
    print("      DEEP AUDIT: DASHBOARD DATA SYNC & VIEW METRICS GAP")
    print("="*65)
    
    # 1. Compare SQLite DB with upload_history.json
    db_path = os.path.join(BASE_DIR, "data", "posted_videos.db")
    hist_path = os.path.join(BASE_DIR, "docs", "data", "upload_history.json")
    pages_path = os.path.join(BASE_DIR, "docs", "data", "pages_data.json")
    latest_run_path = os.path.join(BASE_DIR, "docs", "data", "latest_run_summary.json")
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM videos WHERE status = 'posted'")
    db_posted_count = cur.fetchone()[0]
    
    cur.execute("SELECT facebook_video_id, page_id, filename, posted_at FROM videos WHERE status = 'posted' ORDER BY posted_at DESC")
    db_all_posted = cur.fetchall()
    
    with open(hist_path, "r", encoding="utf-8") as f:
        hist_raw = json.load(f)
    hist_items = hist_raw if isinstance(hist_raw, list) else hist_raw.get("history", [])
    hist_count = len(hist_items)
    
    print(f"\n[1] UPLOAD HISTORY GAP ANALYSIS:")
    print(f"  - Total Posted in SQLite DB:       {db_posted_count}")
    print(f"  - Total in docs/upload_history.json: {hist_count}")
    
    db_ids = set(r[0] for r in db_all_posted if r[0])
    hist_ids = set(str(h.get("id") or h.get("video_id") or "") for h in hist_items)
    
    missing_in_hist = db_ids - hist_ids
    print(f"  - Videos in DB but Missing in upload_history.json: {len(missing_in_hist)}")
    if missing_in_hist:
        print("    Sample missing IDs:", list(missing_in_hist)[:5])
        
    # 2. Check latest upload timestamps
    print(f"\n[2] LATEST UPLOADS RECENCY CHECK:")
    if db_all_posted:
        print(f"  - Latest SQLite Upload: {db_all_posted[0][3]}")
        print(f"    Page ID: {db_all_posted[0][1]} | Video ID: {db_all_posted[0][0]}")
        print(f"    File: {db_all_posted[0][2][:60]}")
    if hist_items:
        first_h = hist_items[0]
        print(f"  - Latest in upload_history.json: {first_h.get('posted_at') or first_h.get('date') or first_h.get('time')}")
        print(f"    Page: {first_h.get('page_name')} | Video ID: {first_h.get('id')}")
        print(f"    Title: {str(first_h.get('title'))[:60]}")

    # 3. Check pages_data.json view counts and freshness
    with open(pages_path, "r", encoding="utf-8") as f:
        pages_raw = json.load(f)
    pages = pages_raw.get("pages", [])
    print(f"\n[3] PAGES DATA & VIEW METRICS AUDIT:")
    print(f"  - Total Pages in pages_data.json: {len(pages)}")
    
    total_views_in_json = sum(p.get("total_views", 0) for p in pages)
    print(f"  - Total Lifetime Views in pages_data.json: {total_views_in_json:,}")
    
    # Check how many pages have videos array and server_uploaded videos
    pages_with_server_vids = 0
    total_server_vids_in_pages = 0
    zero_view_server_vids = 0
    positive_view_server_vids = 0
    
    for p in pages:
        vids = p.get("videos", [])
        s_vids = [v for v in vids if v.get("server_uploaded")]
        if s_vids:
            pages_with_server_vids += 1
            total_server_vids_in_pages += len(s_vids)
            for sv in s_vids:
                views = sv.get("views", 0)
                if views == 0:
                    zero_view_server_vids += 1
                else:
                    positive_view_server_vids += 1
                    
    print(f"  - Pages with server_uploaded videos: {pages_with_server_vids} / {len(pages)}")
    print(f"  - Total server_uploaded videos in pages_data: {total_server_vids_in_pages}")
    print(f"  - Server videos with >0 views: {positive_view_server_vids}")
    print(f"  - Server videos with 0 views (or stale): {zero_view_server_vids}")

    # 4. Live Graph API Sample Check on 5 recent videos to see if views are growing but dashboard is stale
    print(f"\n[4] LIVE META GRAPH API VIEW VERIFICATION (Sample of 5 Videos):")
    # Find tokens
    tokens = {}
    for p in pages:
        pid = str(p.get("id") or "")
        tok = p.get("access_token")
        if pid and tok:
            tokens[pid] = tok
            
    # Also load from configs if needed
    import glob, yaml
    for cfile in glob.glob(os.path.join(BASE_DIR, "config*.yaml")):
        try:
            with open(cfile, "r", encoding="utf-8") as f:
                cdata = yaml.safe_load(f)
            for p in cdata.get("pages", []):
                pid = str(p.get("page_id", ""))
                tok = p.get("page_access_token", "")
                if pid and tok:
                    tokens[pid] = tok
        except Exception:
            pass

    checked_count = 0
    for r in db_all_posted[:8]:
        vid = r[0]
        pid = str(r[1])
        tok = tokens.get(pid)
        if not tok or not vid:
            continue
            
        url = f"https://graph.facebook.com/v20.0/{vid}"
        try:
            res = requests.get(url, params={"fields": "id,views,created_time", "access_token": tok}, timeout=8).json()
            # Also check video_insights
            ins_res = requests.get(f"https://graph.facebook.com/v20.0/{vid}/video_insights", params={"metric": "total_video_views", "access_token": tok}, timeout=8).json()
            
            live_views = res.get("views")
            ins_data = ins_res.get("data", [])
            ins_views = None
            if ins_data and "values" in ins_data[0]:
                ins_views = ins_data[0]["values"][0].get("value")
                
            # Find what dashboard has for this video
            dash_views = "N/A"
            for p in pages:
                if str(p.get("id")) == pid:
                    for v in p.get("videos", []):
                        if str(v.get("id")) == str(vid):
                            dash_views = v.get("views")
                            break
                    break
                    
            print(f"  - Video {vid} (Page {pid}):")
            print(f"      Dashboard recorded views: {dash_views}")
            print(f"      Graph API .views field:   {live_views}")
            print(f"      Graph API insights views: {ins_views}")
            checked_count += 1
            if checked_count >= 5:
                break
        except Exception as e:
            print(f"  - Video {vid} error: {e}")

    # 5. Check if web/ directory matches docs/
    print(f"\n[5] PARITY CHECK: docs/ vs web/ DIRECTORIES:")
    web_pages_path = os.path.join(BASE_DIR, "web", "data", "pages_data.json")
    if os.path.exists(web_pages_path):
        web_size = os.path.getsize(web_pages_path)
        docs_size = os.path.getsize(pages_path)
        print(f"  - docs/data/pages_data.json size: {docs_size:,} bytes")
        print(f"  - web/data/pages_data.json size:  {web_size:,} bytes")
        if web_size != docs_size:
            print(f"  ⚠️ DESYNC DETECTED between docs/ and web/ data files!")
        else:
            print(f"  ✅ docs/ and web/ are identical in size.")
    else:
        print(f"  ℹ️ web/data/pages_data.json does not exist (app serves from docs/).")

if __name__ == "__main__":
    main()
