import json
import requests

with open('docs/data/pages_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for p in d.get('pages', []):
    pid = p['id']
    name = p['name']
    token = p.get('access_token', '')
    if not token:
        continue
    res = requests.get(f"https://graph.facebook.com/v20.0/{pid}/insights", params={
        "metric": "page_post_engagements,page_views_total,page_video_views,page_daily_follows_unique",
        "access_token": token
    })
    if res.status_code == 200:
        data = res.json().get('data', [])
        non_empty = [item['name'] for item in data if item.get('values')]
        print(f"Page {name} ({pid}): HTTP 200, non-empty metrics = {non_empty}")
    else:
        print(f"Page {name} ({pid}): HTTP {res.status_code}")
