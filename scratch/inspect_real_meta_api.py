import json
import requests

with open("docs/data/pages_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Test with first 3 pages
for p in data["pages"][:3]:
    pid = p["id"]
    token = p["access_token"]
    pname = p["name"]
    print(f"\n==================== {pname} ({pid}) ====================")
    
    # 1. Page basic fields
    res = requests.get(f"https://graph.facebook.com/v20.0/{pid}", params={
        "fields": "id,name,followers_count,fan_count,verification_status,is_eligible_for_branded_content",
        "access_token": token
    }).json()
    print("Page details:", res)

    # 2. Page video_reels with real fields
    reels_res = requests.get(f"https://graph.facebook.com/v20.0/{pid}/video_reels", params={
        "fields": "id,description,created_time,updated_time,picture,permalink_url",
        "limit": 5,
        "access_token": token
    }).json()
    reels = reels_res.get("data", [])
    print(f"Reels count sample: {len(reels)}")
    if reels:
        first_reel_id = reels[0]["id"]
        # Check reel details and video insights
        v_res = requests.get(f"https://graph.facebook.com/v20.0/{first_reel_id}", params={
            "fields": "id,views,created_time,description,likes.summary(true),comments.summary(true)",
            "access_token": token
        }).json()
        print("First reel fields:", v_res)

        # Check video insights if available
        ins_res = requests.get(f"https://graph.facebook.com/v20.0/{first_reel_id}/video_insights", params={
            "access_token": token
        }).json()
        print("First reel video_insights:", ins_res)
