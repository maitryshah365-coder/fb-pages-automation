import sqlite3
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

db_path = "data/posted_videos.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=" * 80)
print("DEEP AUDIT: TODAY'S UPLOADS, SCHEDULE GAPS & APP SYNC")
print("=" * 80)

# Load pages_data.json to map page_id to page_name, account, etc.
pages_file = "docs/data/pages_data.json"
pages_map = {}
if os.path.exists(pages_file):
    with open(pages_file, "r", encoding="utf-8") as f:
        pdata = json.load(f)
        for p in pdata.get("pages", []):
            pages_map[str(p["id"])] = p

# 1. Total uploads today
cur.execute("""
    SELECT page_id, COUNT(*) as cnt
    FROM videos
    WHERE status='posted' AND date(posted_at) = '2026-10-11'
    GROUP BY page_id
""")
today_posts_by_page = {str(r["page_id"]): r["cnt"] for r in cur.fetchall()}

# 2. Total runs today by page
cur.execute("""
    SELECT page_id, status, COUNT(*) as cnt
    FROM runs
    WHERE date(started_at) = '2026-10-11'
    GROUP BY page_id, status
""")
today_runs_by_page = {}
for r in cur.fetchall():
    pid = str(r["page_id"])
    if pid not in today_runs_by_page:
        today_runs_by_page[pid] = {}
    today_runs_by_page[pid][r["status"]] = r["cnt"]

# 3. Time distribution of today's uploads (Hours in UTC and IST)
cur.execute("""
    SELECT strftime('%H', posted_at) as hour_utc, COUNT(*) as cnt
    FROM videos
    WHERE status='posted' AND date(posted_at) = '2026-10-11'
    GROUP BY hour_utc
    ORDER BY hour_utc
""")
hourly_dist = cur.fetchall()

print("\n--- HOURLY UPLOAD DISTRIBUTION TODAY (2026-10-11 UTC) ---")
for h in hourly_dist:
    h_utc = int(h["hour_utc"])
    h_ist = (h_utc + 5.5) % 24
    ist_h = int(h_ist)
    ist_m = 30 if (h_ist % 1 != 0) else 0
    print(f"  UTC {h['hour_utc']}:00 (IST {ist_h:02d}:{ist_m:02d}) -> {h['cnt']} videos uploaded")

# 4. Check coverage by Fleets (Account 1, 2, 3, 4, 5, UK 1..7)
print("\n--- FLEET BREAKDOWN (TODAY'S POSTS) ---")
fleet_counts = {}
for pid, p in pages_map.items():
    acc = p.get("account_owner") or p.get("account", "Other")
    if acc not in fleet_counts:
        fleet_counts[acc] = {"total_pages": 0, "pages_posted": 0, "total_posts": 0, "empty_pages": 0}
    fleet_counts[acc]["total_pages"] += 1
    cnt = today_posts_by_page.get(pid, 0)
    if cnt > 0:
        fleet_counts[acc]["pages_posted"] += 1
        fleet_counts[acc]["total_posts"] += cnt
    if p.get("drive_videos_count") == 0:
        fleet_counts[acc]["empty_pages"] += 1

for acc, stats in sorted(fleet_counts.items()):
    print(f"  {acc:20s}: {stats['pages_posted']:2d}/{stats['total_pages']:2d} pages posted ({stats['total_posts']:2d} posts today) | Empty Folders: {stats['empty_pages']}")

# 5. Check all 'no_content' runs today
print("\n--- 'NO_CONTENT' RUNS TODAY (ATTEMPTED BUT DRIVE EMPTY) ---")
cur.execute("""
    SELECT page_id, started_at, runner_ip, runner_city 
    FROM runs 
    WHERE date(started_at) = '2026-10-11' AND status = 'no_content'
    ORDER BY started_at
""")
no_content_runs = cur.fetchall()
for nc in no_content_runs:
    p_info = pages_map.get(str(nc["page_id"]), {})
    pname = p_info.get("name", "Unknown")
    owner = p_info.get("account_owner", "Unknown")
    stock = p_info.get("drive_videos_count", "N/A")
    print(f"  At {nc['started_at'][11:19]} UTC | Page: {pname:22s} ({owner}) | Drive Stock: {stock} | IP: {nc['runner_ip']} ({nc['runner_city']})")

# 6. Check if any errors or failed runs today
print("\n--- ERROR / FAILED RUNS TODAY ---")
cur.execute("""
    SELECT page_id, started_at, status, error_message, runner_ip
    FROM runs
    WHERE date(started_at) = '2026-10-11' AND status NOT IN ('success', 'no_content')
    ORDER BY started_at
""")
err_runs = cur.fetchall()
if not err_runs:
    print("  [✓] ZERO failed or error runs today! All runs either succeeded or cleanly logged no_content.")
else:
    for er in err_runs:
        p_info = pages_map.get(str(er["page_id"]), {})
        pname = p_info.get("name", "Unknown")
        print(f"  At {er['started_at']} | Page: {pname} | Status: {er['status']} | Error: {er['error_message']}")

# 7. Check App Sync Verification
print("\n--- APP & DASHBOARD SYNC VERIFICATION ---")
uh_file = "docs/data/upload_history.json"
if os.path.exists(uh_file):
    with open(uh_file, "r", encoding="utf-8") as f:
        uh_data = json.load(f)
        uh_count = len(uh_data.get("history", []))
        uh_updated = uh_data.get("updated_at")
        print(f"  docs/data/upload_history.json: {uh_count} records (Last updated: {uh_updated})")
        db_today_sum = sum(today_posts_by_page.values())
        print(f"  DB Posted Videos Today: {db_today_sum}")
        # Check how many today posts in upload_history.json
        uh_today = sum(1 for v in uh_data.get("history", []) if (v.get("posted_at") or "").startswith("2026-10-11"))
        print(f"  upload_history.json Today Uploads: {uh_today} vs DB: {db_today_sum}")

# Check pages_data.json today posts sum
if os.path.exists(pages_file):
    with open(pages_file, "r", encoding="utf-8") as f:
        p_data = json.load(f)
        total_today_posts_json = sum(p.get("today_posts", 0) for p in p_data.get("pages", []))
        print(f"  docs/data/pages_data.json 'today_posts' sum (Meta Graph + DB): {total_today_posts_json}")

# Check web/ folder parity
web_pages_file = "web/data/pages_data.json"
if os.path.exists(web_pages_file):
    with open(web_pages_file, "r", encoding="utf-8") as f:
        wp_data = json.load(f)
        w_total_today = sum(p.get("today_posts", 0) for p in wp_data.get("pages", []))
        print(f"  web/data/pages_data.json 'today_posts' sum: {w_total_today}")

conn.close()
