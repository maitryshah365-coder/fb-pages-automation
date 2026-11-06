import os
import sys
import json
import sqlite3
import subprocess
from datetime import datetime, timezone, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "posted_videos.db")
PAGES_PATH = os.path.join(BASE_DIR, "docs", "data", "pages_data.json")

print("=" * 80)
print("🛡️ AUTONOMOUS 4-SLOT GUARANTEE WATCHDOG ENGINE")
print("=" * 80)

now_utc = datetime.now(timezone.utc)
current_hour = now_utc.hour
current_date_str = now_utc.strftime("%Y-%m-%d")

print(f"Current UTC Time: {now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
print(f"Current UTC Hour: {current_hour}")

# Load active accounts
with open(PAGES_PATH, "r", encoding="utf-8") as f:
    pages_data = json.load(f)

pages = pages_data.get("pages", [])

# Map of accounts to dispatch flags and workflows
# Target slots for USA:
# Slot 1: 02:00 - 05:00 UTC
# Slot 2: 11:00 - 14:00 UTC
# Slot 3: 16:00 - 19:00 UTC
# Slot 4: 21:00 - 00:00 UTC

# Target slots for UK:
# Slot 1: 07:00 - 10:00 UTC
# Slot 2: 12:00 - 15:00 UTC
# Slot 3: 17:00 - 20:00 UTC
# Slot 4: 21:00 - 00:00 UTC

# Group pages by account
account_pages = {}
for p in pages:
    acc = p.get("account", "Unknown")
    account_pages.setdefault(acc, []).append(str(p.get("id")))

# Check recent uploads in the last 4 hours
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cutoff_4h = (now_utc - timedelta(hours=4)).isoformat()
cutoff_today = f"{current_date_str}T00:00:00"

print(f"\nEvaluating recent uploads (Cutoff: {cutoff_4h})...\n")

dispatches = []

# USA Accounts mapping
usa_accounts = [
    {"name": "Meghal Chauhan (USA)", "flag": "usa1", "workflow": "post.yml"},
    {"name": "Mia Shah (USA)", "flag": "usa2", "workflow": "post.yml"},
    {"name": "Radika Patel (USA)", "flag": "usa3", "workflow": "post.yml"},
    {"name": "Rohini Dutt (USA)", "flag": "usa4", "workflow": "post.yml"},
    {"name": "Sejal Soni (USA)", "flag": "usa5", "workflow": "post.yml"},
    {"name": "Kalpesh Shah (USA)", "flag": "usa6", "workflow": "post.yml"},
    {"name": "Henny Panchal (USA)", "flag": "usa7", "workflow": "post.yml"},
]

# UK Accounts mapping
uk_accounts = [
    {"name": "Binjal Mehra (UK)", "flag": "uk_account_1", "workflow": "uk_london_post.yml"},
    {"name": "Chanda Nai (UK)", "flag": "uk_account_2", "workflow": "uk_london_post.yml"},
    {"name": "Mahi Patel (UK)", "flag": "uk_account_3", "workflow": "uk_london_post.yml"},
    {"name": "Nidhi Desai (UK)", "flag": "uk_account_4", "workflow": "uk_london_post.yml"},
    {"name": "Richi Patel (UK)", "flag": "uk_account_5", "workflow": "uk_london_post.yml"},
    {"name": "Sweta Shah (UK)", "flag": "uk_account_6", "workflow": "uk_london_post.yml"},
    {"name": "Riya Gaur (UK)", "flag": "uk_account_7", "workflow": "uk_london_post.yml"},
]

def check_account_status(acc_info, is_usa):
    name = acc_info["name"]
    pids = account_pages.get(name, [])
    if not pids:
        # Match by partial string
        for k in account_pages:
            if acc_info["flag"].lower() in k.lower() or name.split()[0].lower() in k.lower():
                pids = account_pages[k]
                break
                
    if not pids:
        print(f"⚠️ Account {name}: No registered pages found in blueprint.")
        return

    placeholders = ",".join(["?"] * len(pids))
    # Count posts in last 4 hours
    cursor.execute(f"""
        SELECT COUNT(*) FROM videos 
        WHERE status='posted' AND page_id IN ({placeholders}) AND posted_at >= ?
    """, (*pids, cutoff_4h))
    posts_4h = cursor.fetchone()[0]

    # Count posts today
    cursor.execute(f"""
        SELECT COUNT(*) FROM videos 
        WHERE status='posted' AND page_id IN ({placeholders}) AND posted_at >= ?
    """, (*pids, cutoff_today))
    posts_today = cursor.fetchone()[0]

    # Max slots possible per run is len(pids)
    print(f"[{name}] {len(pids)} Pages | Today: {posts_today} uploads | Last 4h: {posts_4h} uploads")

    # If within an active window and 0 posts in last 4h, and today is less than 4 per page
    max_daily = len(pids) * 4
    if posts_today < max_daily and posts_4h == 0:
        # Check if current hour should have had an upload
        should_run = False
        if is_usa:
            # USA slots windows: [2,3,4], [11,12,13], [16,17,18], [21,22,23]
            if current_hour in [3, 4, 5, 12, 13, 14, 17, 18, 19, 22, 23, 0]:
                should_run = True
        else:
            # UK slots windows: [7,8,9], [12,13,14], [17,18,19], [21,22,23]
            if current_hour in [8, 9, 10, 13, 14, 15, 18, 19, 20, 22, 23, 0]:
                should_run = True

        if should_run:
            print(f"  🚨 MISSED SLOT DETECTED for {name}! (0 uploads in active window)")
            dispatches.append((acc_info["workflow"], acc_info["flag"], name))
        else:
            print(f"  ⏳ Outside target slot window. Normal idle.")
    else:
        print(f"  ✅ Healthy cadence. (Uploaded recently or daily target met)")

print("\n--- CHECKING USA FLEET ---")
for acc in usa_accounts:
    check_account_status(acc, is_usa=True)

print("\n--- CHECKING UK FLEET ---")
for acc in uk_accounts:
    check_account_status(acc, is_usa=False)

print("\n" + "=" * 80)
if dispatches:
    print(f"🚨 FOUND {len(dispatches)} MISSED SLOTS. TRIGGERING FAIL-SAFE DISPATCHES:")
    gh_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    gh_repo = os.environ.get("GITHUB_REPOSITORY")
    
    for wf, flag, acc_name in dispatches:
        print(f"  🚀 Dispatching: {wf} (Account: {acc_name}, Flag: {flag})")
        dispatched = False
        
        # Method 1: Direct GitHub REST API Call
        if gh_repo and gh_token:
            try:
                import urllib.request
                import urllib.error
                api_url = f"https://api.github.com/repos/{gh_repo}/actions/workflows/{wf}/dispatches"
                headers = {
                    "Authorization": f"Bearer {gh_token}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "Slot-Watchdog-Bot"
                }
                body = json.dumps({"ref": "main", "inputs": {"page": flag}}).encode("utf-8")
                req = urllib.request.Request(api_url, data=body, headers=headers, method="POST")
                with urllib.request.urlopen(req) as resp:
                    if resp.status in (200, 204):
                        print(f"    ✅ Dispatched successfully via GitHub Actions REST API!")
                        dispatched = True
            except Exception as e:
                print(f"    ⚠️ REST API dispatch note: {e}")

        # Method 2: gh CLI fallback
        if not dispatched:
            try:
                env = dict(os.environ)
                if gh_token:
                    env["GH_TOKEN"] = gh_token
                cmd = ["gh", "workflow", "run", wf, "-f", f"page={flag}"]
                res = subprocess.run(cmd, capture_output=True, text=True, env=env)
                if res.returncode == 0:
                    print(f"    ✅ Triggered successfully via gh CLI!")
                    dispatched = True
                else:
                    print(f"    ℹ️ gh CLI response: {res.stderr.strip()}")
            except Exception as e:
                print(f"    ⚠️ Could not run gh command: {e}")
else:
    print("🎉 ALL ACCOUNTS ARE RUNNING ON PERFECT SCHEDULE! ZERO MISSED SLOTS.")
print("=" * 80)
