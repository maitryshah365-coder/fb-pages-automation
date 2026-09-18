import os
import sys
import json
import yaml
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_all_tokens():
    tokens = {}
    
    # 1. Primary config YAML files
    configs = [
        "config.yaml",
        "config_uk_account1.yaml",
        "config_uk_account2.yaml",
        "config_uk_account3.yaml"
    ]
    for cfile in configs:
        cpath = os.path.join(BASE_DIR, cfile)
        if os.path.exists(cpath):
            with open(cpath, "r", encoding="utf-8") as f:
                cdata = yaml.safe_load(f)
                for p in cdata.get("pages", []):
                    pid = str(p.get("page_id", ""))
                    tok = p.get("page_access_token", "")
                    if pid and tok:
                        tokens[pid] = tok

    # 2. Permanent data files
    data_files = [
        "data/pages_tokens.json",
        "data/account2_verified_pages.json",
        "data/uk_account1_binjal_permanent_pages.json",
        "data/uk_account2_chanda_permanent_pages.json",
        "data/uk_account3_mahi_pages.json",
        "data/uk_account3_mahi_permanent_pages.json"
    ]
    for dfile in data_files:
        dpath = os.path.join(BASE_DIR, dfile)
        if os.path.exists(dpath):
            try:
                with open(dpath, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    plist = raw.get("pages", []) if isinstance(raw, dict) else raw
                    for p in plist:
                        pid = str(p.get("id") or p.get("page_id") or "")
                        tok = p.get("access_token") or p.get("page_access_token") or ""
                        if pid and tok and pid not in tokens:
                            tokens[pid] = tok
            except Exception:
                pass

    return tokens

def main():
    print("=================================================================")
    print("  VERIFYING FACEBOOK ACCESS TOKENS & GRAPH API FOR ALL 66 PAGES")
    print("=================================================================")

    tokens_map = load_all_tokens()
    pages_json = os.path.join(BASE_DIR, "docs", "data", "pages_data.json")
    
    if not os.path.exists(pages_json):
        print(f"ERROR: {pages_json} not found!")
        sys.exit(1)

    with open(pages_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    pages = data.get("pages", [])
    total_pages = len(pages)
    valid_count = 0
    with_drive_count = 0

    current_account = None

    for idx, p in enumerate(pages, 1):
        pid = str(p.get("id", ""))
        name = p.get("name", f"page_{idx}")
        account = p.get("account", "Unknown")
        drive_folder = p.get("drive_folder_id", "")
        has_drive = bool(drive_folder and len(drive_folder) > 10)

        if account != current_account:
            current_account = account
            print(f"\n--- {account.upper()} ---")

        token = tokens_map.get(pid) or p.get("access_token")
        if not token:
            print(f"[{idx:02d}] ❌ {name:<22} (ID: {pid}): NO TOKEN FOUND")
            continue

        # Test Graph API call
        url = f"https://graph.facebook.com/v20.0/{pid}"
        params = {
            "fields": "id,name,followers_count,is_published,fan_count,category",
            "access_token": token
        }
        try:
            r = requests.get(url, params=params, timeout=10)
            res = r.json()
            if "error" in res:
                err = res["error"]
                print(f"[{idx:02d}] ❌ {name:<22} (ID: {pid}): ERROR ({err.get('code')}): {err.get('message')}")
            else:
                valid_count += 1
                if has_drive:
                    with_drive_count += 1
                fol = res.get("followers_count") or res.get("fan_count") or 0
                print(f"[{idx:02d}] ✅ {res.get('name', name):<22} (ID: {pid}) | Followers: {fol:<6} | Drive: {'✅ Ready' if has_drive else '⏳ Pending'}")
        except Exception as e:
            print(f"[{idx:02d}] ⚠️ {name:<22} (ID: {pid}): NETWORK ERROR: {e}")

    print("\n=================================================================")
    print(f"AUDIT SUMMARY:")
    print(f"  Total Pages Audited: {total_pages}")
    print(f"  Valid Live Tokens: {valid_count} / {total_pages}")
    print(f"  Ready for Automated Reels Upload: {with_drive_count} / {total_pages}")
    print("=================================================================")

if __name__ == "__main__":
    main()
