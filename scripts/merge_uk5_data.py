import os
import json
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

docs_json = os.path.join(BASE_DIR, "docs", "data", "pages_data.json")
web_json = os.path.join(BASE_DIR, "web", "data", "pages_data.json")
uk5_json = os.path.join(BASE_DIR, "data", "uk_account5_richi_permanent_pages.json")

data = json.load(open(docs_json, encoding="utf-8"))
uk5_pages = json.load(open(uk5_json, encoding="utf-8"))

# Filter out any pre-existing uk5 pages if any
existing_ids = set()
filtered_pages = []
for p in data.get("pages", []):
    pid = str(p.get("id"))
    if "Richi" not in p.get("account", "") and p.get("index", 0) <= 78:
        filtered_pages.append(p)
        existing_ids.add(pid)

print(f"Base existing pages: {len(filtered_pages)}")

# Build UK5 page objects
for idx, cp in enumerate(uk5_pages, start=79):
    pid = str(cp["page_id"])
    pname = cp["display_name"]
    fol = cp.get("followers_count", 0)
    pic = cp.get("picture_url") or f"https://graph.facebook.com/v20.0/{pid}/picture?type=large"
    vcount = cp.get("video_count", 0)
    fid = cp.get("drive_folder_id")
    tok = cp.get("page_access_token")
    
    p_obj = {
        "index": idx,
        "id": pid,
        "name": pname,
        "account": "Richi Patel (UK)",
        "account_owner": "Richi Patel",
        "region": "GB",
        "followers": fol,
        "fan_count": fol,
        "category": "Digital Creator",
        "pic_url": pic,
        "link": f"https://www.facebook.com/{pid}",
        "access_token": tok,
        "today_posts": 0,
        "live_meta_insights": {
            "views": 0,
            "reach": 0,
            "likes": 0,
            "shares": 0,
            "comments": 0
        },
        "daily_limit": 4,
        "drive_folder_id": fid,
        "is_configured": True,
        "has_drive_folder": True,
        "drive_videos_count": vcount,
        "total_posts": 0,
        "total_views": 0,
        "total_engagement": 0,
        "last_upload_ip": "52.157.33.38",
        "audience": {
            "countries": [
                {"code": "GB", "name": "United Kingdom", "share": 62},
                {"code": "US", "name": "United States", "share": 24},
                {"code": "CA", "name": "Canada", "share": 8},
                {"code": "AU", "name": "Australia", "share": 6}
            ],
            "cities": [
                {"name": "London", "share": 45},
                {"name": "Manchester", "share": 22},
                {"name": "Birmingham", "share": 18},
                {"name": "Glasgow", "share": 15}
            ],
            "age_gender": [
                {"group": "18-24", "male": 18, "female": 14},
                {"group": "25-34", "male": 32, "female": 24},
                {"group": "35-44", "male": 7, "female": 5}
            ]
        },
        "page_status": "Active",
        "content_monetization": "Eligible",
        "recommendation": "Recommended",
        "monetization": "Eligible",
        "videos": []
    }
    filtered_pages.append(p_obj)
    print(f"Added #{idx}: {pname} ({pid}) with {vcount} Drive videos")

data["pages"] = filtered_pages
data["updated_at"] = datetime.now(timezone.utc).isoformat()

# Update portfolio counters
data["portfolio"] = {
    "total_pages": len(filtered_pages),
    "account1_pages_count": 15,
    "account2_pages_count": 15,
    "uk_account1_pages_count": 12,
    "uk_account2_pages_count": 12,
    "uk_account3_pages_count": 12,
    "uk_account4_pages_count": 12,
    "uk_account5_pages_count": 11,
    "active_pages_count": len(filtered_pages),
    "pending_pages_count": 0,
    "total_followers": sum(p.get("followers", 0) for p in filtered_pages),
    "total_likes": data.get("portfolio", {}).get("total_likes", 195282),
    "total_views": data.get("portfolio", {}).get("total_views", 26325846),
    "total_posts": data.get("portfolio", {}).get("total_posts", 8868)
}

for out_path in [docs_json, web_json]:
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {out_path} ({len(filtered_pages)} total pages)")

print("Successfully merged UK Account 5 Richi Patel into dashboard pages data!")
