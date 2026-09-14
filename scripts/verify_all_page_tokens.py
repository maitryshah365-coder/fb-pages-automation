import os
import sys
import json
import yaml
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(BASE_DIR, "config.yaml")
tokens_path = os.path.join(BASE_DIR, "data", "pages_tokens.json")

with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

tokens_map = {}
if os.path.exists(tokens_path):
    with open(tokens_path, "r", encoding="utf-8") as f:
        t_data = json.load(f)
        for item in t_data:
            pid = str(item.get("id", ""))
            tok = item.get("access_token", "")
            if pid and tok:
                tokens_map[pid] = tok

print("==========================================================")
print("  VERIFYING FACEBOOK ACCESS TOKENS FOR ALL 15 PAGES")
print("==========================================================")

results = []
pages = config.get("pages", [])

for idx, page in enumerate(pages, 1):
    pid = str(page.get("page_id", ""))
    pname = page.get("name", f"page_{idx}")
    dfolder = page.get("drive_folder_id", "")
    has_drive = bool(dfolder and "REPLACE" not in dfolder)
    
    token = tokens_map.get(pid) or os.environ.get(f"FB_TOKEN_PAGE_{idx}") or os.environ.get("FB_PAGE_ACCESS_TOKEN")
    
    if not token:
        print(f"[{idx:02d}] ❌ {pname} (ID: {pid}): NO TOKEN FOUND!")
        results.append({"index": idx, "name": pname, "id": pid, "status": "NO_TOKEN", "has_drive": has_drive})
        continue

    # Query Graph API
    url = f"https://graph.facebook.com/v19.0/{pid}"
    params = {
        "fields": "id,name,followers_count,is_published,fan_count,category",
        "access_token": token
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if "error" in data:
            err_msg = data["error"].get("message", "Unknown error")
            err_code = data["error"].get("code", 0)
            print(f"[{idx:02d}] ❌ {pname} (ID: {pid}): TOKEN ERROR ({err_code}): {err_msg}")
            results.append({"index": idx, "name": pname, "id": pid, "status": "ERROR", "error": err_msg, "has_drive": has_drive})
        else:
            fb_name = data.get("name", pname)
            followers = data.get("followers_count", 0)
            published = data.get("is_published", False)
            tasks = data.get("tasks", [])
            has_create_content = any("CREATE_CONTENT" in t or "MANAGE" in t for t in tasks) or bool(tasks)
            
            drive_status = f"Drive: ✅ READY ({dfolder[:15]}...)" if has_drive else "Drive: ⏳ Pending Folder"
            print(f"[{idx:02d}] ✅ {fb_name:<22} (ID: {pid}) | Followers: {followers:<6} | Published: {published} | {drive_status}")
            results.append({
                "index": idx,
                "name": fb_name,
                "id": pid,
                "status": "VALID",
                "followers": followers,
                "published": published,
                "has_drive": has_drive,
                "tasks": tasks
            })
    except Exception as e:
        print(f"[{idx:02d}] ⚠️ {pname} (ID: {pid}): REQUEST FAILED: {e}")
        results.append({"index": idx, "name": pname, "id": pid, "status": "NETWORK_ERR", "error": str(e), "has_drive": has_drive})

valid_count = sum(1 for r in results if r["status"] == "VALID")
active_drive_count = sum(1 for r in results if r["status"] == "VALID" and r["has_drive"])

print("\n==========================================================")
print(f"RESULTS SUMMARY:")
print(f"  Total Pages: {len(pages)}")
print(f"  Valid Live Tokens: {valid_count} / {len(pages)}")
print(f"  Fully Ready For Upload (Valid Token + Active Drive): {active_drive_count} / 11 configured")
print("==========================================================")
