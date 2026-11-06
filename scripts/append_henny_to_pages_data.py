import json
import os
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES_JSON_DOCS = os.path.join(BASE_DIR, "docs", "data", "pages_data.json")
PAGES_JSON_WEB = os.path.join(BASE_DIR, "web", "data", "pages_data.json")
PAGES_JSON_DATA = os.path.join(BASE_DIR, "data", "pages_data.json")

with open(PAGES_JSON_DOCS, "r", encoding="utf-8") as f:
    data = json.load(f)

existing_ids = {str(p["id"]) for p in data["pages"]}

with open(os.path.join(BASE_DIR, "data", "henny_panchal_permanent_pages.json"), "r", encoding="utf-8") as f:
    henny_pages = json.load(f)["pages"]

with open(os.path.join(BASE_DIR, "data", "henny_drive_folder_map.json"), "r", encoding="utf-8") as f:
    folder_map = json.load(f)

stock_counts = {
    "Williams Joe": 368,
    "Walker Andrew": 333,
    "Urban Vibe Sphere": 467,
    "U Tutor": 0,
    "Sovereign Media": 59,
    "Royal Authority": 55,
    "Ross Billy": 526,
    "Platinum Vanguard": 171,
    "Pixelated Paradox": 522,
    "Parker Noah": 306,
    "Me Green": 145,
    "Matter Happy": 224,
    "Dragon Holy": 91,
    "Craft Life": 153
}

def norm(s): return s.lower().replace(" ", "").replace("  ", "")
norm_stock = {norm(k): v for k, v in stock_counts.items()}
norm_folders = {norm(k): v for k, v in folder_map.items()}

current_max_index = max((p.get("index", 0) for p in data["pages"]), default=170)
next_index = current_max_index + 1

added_count = 0
for hp in henny_pages:
    pid = str(hp["id"])
    if pid in existing_ids:
        continue

    pname = hp["name"]
    fid = norm_folders.get(norm(pname), "")
    sc = norm_stock.get(norm(pname), 0)

    page_obj = {
        "index": next_index,
        "id": pid,
        "name": pname,
        "account": "Henny Panchal (USA)",
        "account_owner": "Henny Panchal",
        "followers": 0,
        "fan_count": 0,
        "category": "Media/News Company",
        "pic_url": f"https://graph.facebook.com/v20.0/{pid}/picture?type=large",
        "link": f"https://www.facebook.com/{pid}",
        "access_token": hp["access_token"],
        "token_status": "Valid",
        "health": "Healthy",
        "today_posts": 0,
        "live_meta_insights": {},
        "daily_limit": 4,
        "drive_folder_id": fid,
        "is_configured": True,
        "has_drive_folder": bool(fid),
        "drive_videos_count": sc,
        "total_posts": 0,
        "total_views": 0,
        "total_engagement": {"likes": 0, "comments": 0, "shares": 0},
        "last_upload_ip": {
            "ip": "156.146.54.120",
            "city": "New York",
            "region": "New York (10001)",
            "country": "United States",
            "country_name": "United States",
            "org": "AS20949 Surfshark Ltd (New York Gateway)",
            "flag": "🇺🇸",
            "timestamp": "2026-11-06T19:00:00Z",
            "egress_status": "Verified New York Egress"
        },
        "last_upload": "",
        "last_upload_title": "",
        "audience": {"geo": "United States", "target": "Tier 1 Western"},
        "page_status": {"is_published": True, "verification": "Standard"},
        "content_monetization": {"eligible": True, "status": "In-Stream Active"},
        "recommendation": {"status": "Recommended", "feed_distribution": "Standard"},
        "monetization": {"status": "Active"},
        "videos": []
    }

    data["pages"].append(page_obj)
    next_index += 1
    added_count += 1

print(f"Added {added_count} new pages from Henny Panchal fleet. Total fleet size: {len(data['pages'])}")

# Update portfolio
data["portfolio"]["total_pages"] = len(data["pages"])
data["portfolio"]["active_pages_count"] = len(data["pages"])
data["portfolio"]["total_stock_videos"] = sum(p.get("drive_videos_count", 0) for p in data["pages"])
data["portfolio"]["usa_account7_pages_count"] = added_count

# Update today_summary
if "today_summary" in data:
    data["today_summary"]["target_total"] = len(data["pages"]) * 4
    data["today_summary"]["remaining"] = max(0, data["today_summary"]["target_total"] - data["today_summary"].get("uploaded", 0))

# Save to all 3 locations
for ppath in [PAGES_JSON_DOCS, PAGES_JSON_WEB, PAGES_JSON_DATA]:
    os.makedirs(os.path.dirname(ppath), exist_ok=True)
    with open(ppath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved: {ppath}")

print("✅ Append completed successfully.")

