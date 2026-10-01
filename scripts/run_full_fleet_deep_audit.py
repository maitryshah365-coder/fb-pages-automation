import sys
import os
import json
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts.real_facebook_monetization_engine import audit_account_fleet, load_master_data, save_master_data

def main():
    target_account = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != "all" else None
    
    master = load_master_data()
    accounts = master.get("accounts", [])
    
    if target_account:
        accounts = [a for a in accounts if a["account_id"] == target_account]

    print("==========================================================================")
    print("👑 RAJ FB PRO • FULL FLEET CLOUD MONETIZATION REAL AUDITOR")
    print(f"Total Accounts to Audit: {len(accounts)}")
    print("==========================================================================\n")

    success_count = 0
    for idx, acc in enumerate(accounts, 1):
        acc_id = acc["account_id"]
        acc_name = acc.get("account_name", acc_id)
        print(f"\n[{idx}/{len(accounts)}] Auditing {acc_name} ({acc_id})...")
        try:
            audit_account_fleet(acc_id)
            success_count += 1
        except Exception as e:
            print(f"⚠️ Error auditing {acc_id}: {e}")

    # Final save
    save_master_data(master)
    print(f"\n==========================================================================")
    print(f"🎉 CLOUD AUDIT COMPLETE! {success_count}/{len(accounts)} accounts audited.")
    print("==========================================================================")

if __name__ == "__main__":
    main()
