import json, requests, sys

with open('docs/data/pages_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for p in data.get('pages', [])[:5]:
    pid = str(p['id'])
    pname = p.get('name')
    tok = p.get('access_token')
    print(f"\n--- Checking Page: {pname} ({pid}) ---")
    if not tok:
        print("No token!")
        continue
    # Query video_reels
    r = requests.get(f"https://graph.facebook.com/v20.0/{pid}/video_reels", params={
        "fields": "id,description,views,created_time",
        "limit": 5,
        "access_token": tok
    }).json()
    reels = r.get("data", [])
    print(f"video_reels count: {len(reels)}")
    for reel in reels[:3]:
        print(f"  Reel {reel.get('id')}: views={reel.get('views')} created={reel.get('created_time')} desc={reel.get('description', '')[:30]}")

    # Query /videos
    v = requests.get(f"https://graph.facebook.com/v20.0/{pid}/videos", params={
        "fields": "id,title,description,views,created_time",
        "limit": 5,
        "access_token": tok
    }).json()
    vids = v.get("data", [])
    print(f"videos count: {len(vids)}")
    for vid in vids[:3]:
        print(f"  Video {vid.get('id')}: views={vid.get('views')} created={vid.get('created_time')} title={vid.get('title', '')[:30]}")
