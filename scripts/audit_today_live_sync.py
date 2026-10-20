import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = r"E:\Anty Working\Google_Drive_to_Facebook_Automation_Master_Spec"
today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

print("=" * 80)
print(f"👑 FB PAGES APP & FLEET SYNC MASTER AUDIT ({today_str} UTC)")
print("=" * 80)

# 1. Database Audit
db_path = os.path.join(BASE_DIR, "data", "posted_videos.db")
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT count(*) FROM videos WHERE status = 'posted'")
    total_posted = cur.fetchone()[0]

    cur.execute("SELECT count(*) FROM videos WHERE status = 'posted' AND date(posted_at) = ?", (today_str,))
    today_posted = cur.fetchone()[0]

    cur.execute("""
        SELECT substr(posted_at, 1, 10) as pdate, count(*) 
        FROM videos 
        WHERE status = 'posted' AND posted_at IS NOT NULL
        GROUP BY pdate 
        ORDER BY pdate DESC 
        LIMIT 7
    """)
    recent_days = cur.fetchall()

    cur.execute("""
        SELECT count(*) FROM runs 
        WHERE date(started_at) = ? AND status NOT IN ('success', 'completed', 'no_content')
    """, (today_str,))
    today_errors = cur.fetchone()[0]

    cur.execute("""
        SELECT count(*) FROM runs 
        WHERE date(started_at) = ? AND status = 'no_content'
    """, (today_str,))
    today_no_content = cur.fetchone()[0]

    print("\n[1] 📊 DATABASE POSTING AUDIT (SQLite)")
    print(f"    - Grand Total Videos Posted:  {total_posted:,}")
    print(f"    - Videos Posted Today ({today_str}): {today_posted}")
    print(f"    - Failed/Error Runs Today:    {today_errors}")
    print(f"    - No Content (Empty Stock):   {today_no_content}")
    print("    - Last 7 Days Posting Activity:")
    for d, c in recent_days:
        print(f"        * {d}: {c} videos posted")
    conn.close()
else:
    print(f"[1] ⚠️ Database missing at {db_path}")

# 2. Pages Data & Portfolio Fleet Status
pages_path = os.path.join(BASE_DIR, "docs", "data", "pages_data.json")
if os.path.exists(pages_path):
    with open(pages_path, "r", encoding="utf-8") as f:
        pdata = json.load(f)
    pages = pdata.get("pages", [])
    portfolio = pdata.get("portfolio", {})
    
    total_views = sum(int(p.get("total_views") or 0) for p in pages)
    total_followers = sum(int(p.get("followers") or p.get("fan_count") or 0) for p in pages)
    total_stock = sum(int(p.get("drive_videos_count") or 0) for p in pages)
    zero_stock_pages = [p["name"] for p in pages if (p.get("drive_videos_count") or 0) == 0]
    
    print("\n[2] 🌐 FLEET & PORTFOLIO METRICS")
    print(f"    - Total Pages in Fleet:      {len(pages)}")
    print(f"    - Total Fleet Followers:     {total_followers:,}")
    print(f"    - Total Fleet Lifetime Views: {total_views:,}")
    print(f"    - Total Drive Stock Videos:  {total_stock:,}")
    print(f"    - Pages with 0 Stock:        {len(zero_stock_pages)}")

# 3. Token Audit Status
tok_path = os.path.join(BASE_DIR, "docs", "data", "token_audit_report.json")
if os.path.exists(tok_path):
    with open(tok_path, "r", encoding="utf-8") as f:
        tdata = json.load(f)
    print("\n[3] 🔑 META GRAPH API TOKEN HEALTH")
    print(f"    - Total Pages Audited: {tdata.get('total_pages')}")
    print(f"    - Active Valid Tokens: {tdata.get('valid_tokens_count')} ({tdata.get('valid_percentage')}%)")
    print(f"    - Invalid Tokens:      {tdata.get('invalid_tokens_count')}")

# 4. Sync Status & Latest Pipeline Run
sync_path = os.path.join(BASE_DIR, "docs", "data", "auto_sync_status.json")
if os.path.exists(sync_path):
    with open(sync_path, "r", encoding="utf-8") as f:
        sdata = json.load(f)
    print("\n[4] 🔄 SYNC DAEMON & RADAR STATUS")
    print(f"    - Daemon Status:       {sdata.get('daemon_status')}")
    print(f"    - Last Updated At:     {sdata.get('updated_at')}")
    print(f"    - Current Account:     {sdata.get('current_account')}")

run_path = os.path.join(BASE_DIR, "docs", "data", "latest_run_summary.json")
if os.path.exists(run_path):
    with open(run_path, "r", encoding="utf-8") as f:
        rdata = json.load(f)
    print("\n[5] 🚀 LATEST UPLOAD RUN TELEMETRY")
    print(f"    - Run ID:              {rdata.get('run_id')}")
    print(f"    - Completed At:        {rdata.get('completed_at')}")
    print(f"    - Successful Uploads:  {rdata.get('successful_uploads')} / {rdata.get('total_pages')}")
    runner = rdata.get("runner_telemetry", {})
    if runner:
        print(f"    - Runner IP & City:    {runner.get('ip')} ({runner.get('city')}, {runner.get('country')})")

print("\n" + "=" * 80)
print("AUDIT SUMMARY COMPLETE!")
print("=" * 80)
