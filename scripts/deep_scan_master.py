import os
import sys
import json
import sqlite3
import yaml
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 80)
    print("👑 MASTER DEEP SCAN: FB PAGES, TOKENS, UPLOADS, SCHEDULE & DATA")
    print("=" * 80)

    # 1. Inspect pages_data.json
    pages_json_path = os.path.join(BASE_DIR, "docs", "data", "pages_data.json")
    if os.path.exists(pages_json_path):
        with open(pages_json_path, "r", encoding="utf-8") as f:
            pdata = json.load(f)
        pages = pdata.get("pages", [])
        print(f"\n[1] docs/data/pages_data.json:")
        print(f"    Total pages in JSON: {len(pages)}")
        print(f"    File size: {os.path.getsize(pages_json_path) / (1024*1024):.2f} MB")
        
        # Check accounts breakdown
        acc_counts = {}
        tokens_present = 0
        drive_configured = 0
        total_videos = 0
        total_views = 0
        total_followers = 0
        today_posts = 0

        for p in pages:
            acc = p.get("account", "Unknown")
            acc_counts[acc] = acc_counts.get(acc, 0) + 1
            if p.get("access_token"):
                tokens_present += 1
            if p.get("drive_folder_id") or p.get("drive_folder"):
                drive_configured += 1
            vids = p.get("videos", [])
            total_videos += len(vids)
            total_followers += int(p.get("followers") or p.get("fan_count") or 0)
            today_posts += int(p.get("today_posts") or 0)
            for v in vids:
                total_views += int(v.get("views") or 0)

        print(f"    Tokens present: {tokens_present}/{len(pages)}")
        print(f"    Drive folders configured: {drive_configured}/{len(pages)}")
        print(f"    Total video records: {total_videos}")
        print(f"    Total recorded views: {total_views:,}")
        print(f"    Total followers: {total_followers:,}")
        print(f"    Today posts count in JSON: {today_posts}")
        print(f"    Breakdown by Account:")
        for acc, count in sorted(acc_counts.items()):
            print(f"      - {acc}: {count} pages")

    # 2. Inspect SQLite DB posted_videos.db
    db_path = os.path.join(BASE_DIR, "data", "posted_videos.db")
    if os.path.exists(db_path):
        print(f"\n[2] data/posted_videos.db:")
        print(f"    File size: {os.path.getsize(db_path) / (1024*1024):.2f} MB")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        print(f"    Tables: {tables}")

        if "posted_videos" in tables:
            cur.execute("SELECT COUNT(*) FROM posted_videos")
            print(f"    Total in posted_videos: {cur.fetchone()[0]}")
            cur.execute("SELECT MAX(posted_at) FROM posted_videos")
            print(f"    Latest posted_at: {cur.fetchone()[0]}")

        if "runs" in tables:
            cur.execute("SELECT COUNT(*) FROM runs")
            print(f"    Total runs: {cur.fetchone()[0]}")
            cur.execute("SELECT date(started_at) as d, COUNT(*), SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) FROM runs GROUP BY d ORDER BY d DESC LIMIT 7")
            print(f"    Recent daily run stats (Date | Total | Success):")
            for r in cur.fetchall():
                print(f"      {r[0]}: Total {r[1]} runs | Success: {r[2]}")

        conn.close()

    # 3. Inspect latest_run_summary.json
    sum_path = os.path.join(BASE_DIR, "docs", "data", "latest_run_summary.json")
    if os.path.exists(sum_path):
        with open(sum_path, "r", encoding="utf-8") as f:
            sdata = json.load(f)
        print(f"\n[3] docs/data/latest_run_summary.json:")
        print(f"    Run ID: {sdata.get('run_id')}")
        print(f"    Account: {sdata.get('account')}")
        print(f"    Started at: {sdata.get('started_at')}")
        print(f"    Completed at: {sdata.get('completed_at')}")
        print(f"    Total pages in run: {sdata.get('total_pages')}")
        print(f"    Successful uploads: {sdata.get('successful_uploads')}")
        print(f"    Failed uploads: {sdata.get('failed_uploads')}")

    # 4. Inspect upload_history.json
    hist_path = os.path.join(BASE_DIR, "docs", "data", "upload_history.json")
    if os.path.exists(hist_path):
        with open(hist_path, "r", encoding="utf-8") as f:
            hdata = json.load(f)
        history = hdata.get("history", []) if isinstance(hdata, dict) else hdata
        print(f"\n[4] docs/data/upload_history.json:")
        print(f"    Total history items: {len(history)}")
        if history:
            print(f"    Latest item: Page: {history[0].get('page_name')}, Date: {history[0].get('uploaded_at') or history[0].get('date')}, Status: {history[0].get('status')}")

    # 5. Inspect auto_sync_status.json
    sync_path = os.path.join(BASE_DIR, "docs", "data", "auto_sync_status.json")
    if os.path.exists(sync_path):
        with open(sync_path, "r", encoding="utf-8") as f:
            syndata = json.load(f)
        print(f"\n[5] docs/data/auto_sync_status.json:")
        print(f"    Status: {syndata.get('daemon_status')}")
        print(f"    Updated at: {syndata.get('updated_at')}")

if __name__ == "__main__":
    main()
