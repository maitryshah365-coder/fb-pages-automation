import sys
import os
import json
import time
import subprocess
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts.real_facebook_monetization_engine import audit_account_fleet, load_master_data

STATUS_PATHS = [
    os.path.join(BASE_DIR, "data", "auto_sync_status.json"),
    os.path.join(BASE_DIR, "docs", "data", "auto_sync_status.json"),
    os.path.join(BASE_DIR, "web", "data", "auto_sync_status.json")
]

def update_daemon_status(status_obj):
    status_obj["updated_at"] = datetime.now(timezone.utc).isoformat()
    for sp in STATUS_PATHS:
        try:
            os.makedirs(os.path.dirname(sp), exist_ok=True)
            with open(sp, "w", encoding="utf-8") as f:
                json.dump(status_obj, f, indent=2)
        except Exception:
            pass

def push_to_github(commit_msg):
    try:
        print(f"\n[GIT] Committing and pushing verified live data to GitHub...")
        subprocess.run(["git", "add", "data/", "docs/data/", "web/data/"], cwd=BASE_DIR, check=False)
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, check=False)
        res = subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, capture_output=True, text=True, check=False)
        if res.returncode == 0:
            print("  ✅ Successfully pushed live Facebook data to GitHub!")
        else:
            print(f"  ⚠️ Git push output: {res.stderr.strip()[:100]}")
    except Exception as e:
        print(f"  ⚠️ Git push error: {e}")

def run_continuous_sync(loop_delay_seconds=3600):
    print("=================================================================")
    print("👑 RAJ FB PRO • 24/7 ALL-TIME AUTONOMOUS LIVE FACEBOOK AUDITOR")
    print(f"Base Directory: {BASE_DIR}")
    print(f"Cycle Delay: {loop_delay_seconds // 60} minutes")
    print("=================================================================\n")

    cycle_count = 0

    while True:
        cycle_count += 1
        print(f"\n🚀 >>> STARTING FLEET AUDIT CYCLE #{cycle_count} <<<")
        
        master = load_master_data()
        accounts = master.get("accounts", [])
        total_accounts = len(accounts)

        status_obj = {
            "daemon_status": "RUNNING",
            "cycle": cycle_count,
            "total_accounts": total_accounts,
            "current_account_index": 0,
            "current_account": None,
            "current_page": None,
            "cycle_started_at": datetime.now(timezone.utc).isoformat(),
            "last_successful_cycle_at": None
        }
        update_daemon_status(status_obj)

        for idx, acc in enumerate(accounts, 1):
            acc_id = acc["account_id"]
            acc_name = acc.get("account_name", acc_id)
            print(f"\n[{idx}/{total_accounts}] Auditing Account: {acc_name} ({acc_id})...")

            status_obj["current_account_index"] = idx
            status_obj["current_account"] = acc_name
            update_daemon_status(status_obj)

            def on_progress(p_idx, p_total, pname, pid):
                status_obj["current_page"] = f"{pname} ({p_idx}/{p_total})"
                update_daemon_status(status_obj)

            try:
                audit_account_fleet(acc_id, progress_callback=on_progress)
            except Exception as e:
                print(f"⚠️ Error auditing {acc_id}: {e}")

            # Push after each account completes so phone/GitHub Pages updates immediately!
            push_to_github(f"Auto-Sync: Live Facebook audit updated for {acc_name}")
            time.sleep(5)

        status_obj["daemon_status"] = "SLEEPING_UNTIL_NEXT_CYCLE"
        status_obj["current_page"] = "Cycle Complete"
        status_obj["last_successful_cycle_at"] = datetime.now(timezone.utc).isoformat()
        update_daemon_status(status_obj)

        print(f"\n🎉 FLEET AUDIT CYCLE #{cycle_count} COMPLETE across all {total_accounts} accounts!")
        print(f"💤 Sleeping for {loop_delay_seconds // 60} minutes before next automatic check...\n")
        time.sleep(loop_delay_seconds)

if __name__ == "__main__":
    delay = int(sys.argv[1]) if len(sys.argv) > 1 else 3600
    run_continuous_sync(delay)
