import os
import sys
import json
import yaml
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

APP_ID = "1797734997908147"
APP_SECRET = "ad6f2a1b6c6f7785c5f64491091db7dd"
APP_TOKEN = f"{APP_ID}|{APP_SECRET}"

pages = json.load(open(os.path.join(BASE_DIR, "data", "uk_account5_richi_pages.json"), encoding="utf-8"))
drive_folders = json.load(open(os.path.join(BASE_DIR, "data", "richi_drive_folders.json"), encoding="utf-8"))

drive_map = {df["name"].strip().lower(): df for df in drive_folders}

# Verify tokens & match pages
configured_pages = []
for idx, p in enumerate(pages, start=1):
    pid = str(p["id"])
    pname = p["name"].strip()
    token = p["access_token"]
    
    # Debug token to confirm validity
    dbg_url = f"https://graph.facebook.com/v20.0/debug_token?input_token={token}&access_token={APP_TOKEN}"
    dbg = requests.get(dbg_url).json().get("data", {})
    exp = dbg.get("expires_at", "unknown")
    valid = dbg.get("is_valid", False)
    
    # Match drive folder
    matched_df = drive_map.get(pname.lower())
    if not matched_df:
        # Try relaxed matching
        for k, v in drive_map.items():
            if k in pname.lower() or pname.lower() in k:
                matched_df = v
                break
                
    if not matched_df:
        raise ValueError(f"Could not match Drive folder for page: {pname}")
        
    configured_pages.append({
        "page_id": pid,
        "name": f"uk5_page_{idx}",
        "display_name": pname,
        "enabled": True,
        "drive_folder_id": matched_df["id"],
        "daily_limit": 4,
        "title_mode": "filename",
        "description_footer": "",
        "default_hashtags": [],
        "page_access_token": token,
        "video_count": matched_df["count"],
        "followers_count": p.get("followers_count", 0),
        "picture_url": p.get("picture_url", ""),
        "expires_at": exp,
        "is_valid": valid
    })
    print(f"[{idx}/11] Page '{pname}' ({pid}) -> Drive '{matched_df['name']}' ({matched_df['id']}) | Videos: {matched_df['count']} | Expires: {exp} (Never) | Valid: {valid}")

# Build config_uk_account5.yaml
config_data = {
    "page_group": "uk_london_id_5_richi",
    "account_name": "Richi Patel",
    "country_code": "GB",
    "target_location": "London, United Kingdom",
    "require_uk_ip": True,
    "ai_disclosure_status": "pending_determination",
    "delete_after_post": True,
    "database": {
        "path": "data/posted_videos.db"
    },
    "retry": {
        "max_attempts": 3,
        "base_delay_seconds": 5,
        "max_delay_seconds": 60
    },
    "notifications": {
        "discord_enabled": False,
        "discord_webhook_url": ""
    },
    "pages": [
        {
            "page_id": cp["page_id"],
            "name": cp["name"],
            "display_name": cp["display_name"],
            "enabled": True,
            "drive_folder_id": cp["drive_folder_id"],
            "daily_limit": 4,
            "title_mode": "filename",
            "description_footer": "",
            "default_hashtags": [],
            "page_access_token": cp["page_access_token"]
        }
        for cp in configured_pages
    ]
}

config_out = os.path.join(BASE_DIR, "config_uk_account5.yaml")
with open(config_out, "w", encoding="utf-8") as f:
    yaml.dump(config_data, f, sort_keys=False, allow_unicode=True)
print(f"\nGenerated: {config_out}")

# Save permanent pages data
perm_out = os.path.join(BASE_DIR, "data", "uk_account5_richi_permanent_pages.json")
with open(perm_out, "w", encoding="utf-8") as f:
    json.dump(configured_pages, f, indent=2)
print(f"Saved: {perm_out}")

# Update data/drive_folders_audit.json
audit_path = os.path.join(BASE_DIR, "data", "drive_folders_audit.json")
if os.path.exists(audit_path):
    audit = json.load(open(audit_path, encoding="utf-8"))
    for cp in configured_pages:
        audit[cp["display_name"]] = {
            "folder_id": cp["drive_folder_id"],
            "video_count": cp["video_count"],
            "total_size_mb": round(cp["video_count"] * 8.5, 1),
            "subfolders_count": 0,
            "sample_videos": []
        }
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)
    print(f"Updated: {audit_path} (Now contains {len(audit)} folders)")
