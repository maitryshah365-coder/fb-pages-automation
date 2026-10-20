import sqlite3
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

db_path = "data/posted_videos.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

pages_file = "docs/data/pages_data.json"
pages_map = {}
if os.path.exists(pages_file):
    with open(pages_file, "r", encoding="utf-8") as f:
        pdata = json.load(f)
        for p in pdata.get("pages", []):
            pages_map[str(p["id"])] = p

print("=" * 80)
print("FLEET RUN SCHEDULE & EXECUTION COMPARISON (OCT 10 vs OCT 11)")
print("=" * 80)

# Check run counts by account owner for Oct 10 and Oct 11
for target_date in ["2026-10-10", "2026-10-11"]:
    print(f"\n--- DATE: {target_date} ---")
    cur.execute("""
        SELECT page_id, COUNT(*) as cnt, MAX(started_at) as last_run, status
        FROM runs
        WHERE date(started_at) = ?
        GROUP BY page_id, status
    """, (target_date,))
    rows = cur.fetchall()
    
    fleet_summary = {}
    for r in rows:
        pid = str(r["page_id"])
        p_info = pages_map.get(pid, {})
        owner = p_info.get("account_owner", "Unknown")
        status = r["status"]
        if owner not in fleet_summary:
            fleet_summary[owner] = {"success": 0, "no_content": 0, "failed": 0, "last_time": ""}
        fleet_summary[owner][status] = fleet_summary[owner].get(status, 0) + r["cnt"]
        if r["last_run"] > fleet_summary[owner]["last_time"]:
            fleet_summary[owner]["last_time"] = r["last_run"]
            
    for owner, st in sorted(fleet_summary.items()):
        print(f"  {owner:20s} | Success: {st.get('success',0):2d} | No Content: {st.get('no_content',0):2d} | Failed: {st.get('failed',0):2d} | Last Run: {st['last_time']}")

# Let's check why certain fleets didn't run on Oct 11 in SQLite
print("\n" + "=" * 80)
print("WHY SOME FLEETS DIDN'T LOG IN SQLITE TODAY")
print("=" * 80)
# Check git log for github-actions commits today
import subprocess
try:
    git_log = subprocess.check_output(
        ["git", "log", "--since=2026-10-11T00:00:00", "--oneline"],
        cwd=".",
        text=True,
        encoding="utf-8"
    )
    print("Git commits pushed today:")
    print(git_log if git_log.strip() else "  No commits logged today yet.")
except Exception as e:
    print("Git log error:", e)

conn.close()
