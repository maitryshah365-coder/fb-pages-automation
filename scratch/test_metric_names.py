import json
import requests

with open('docs/data/pages_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

p = d.get('pages', [])[0]
token = p.get('access_token', '')

# Test standard basic fields
r = requests.get(f"https://graph.facebook.com/v20.0/{p['id']}?fields=name,followers_count,fan_count,category,about,is_published&access_token={token}")
print("Basic fields:", r.json())

# Test individual metric names
common_metrics = [
    "page_impressions",
    "page_impressions_unique",
    "page_engaged_users",
    "page_post_engagements",
    "page_fans",
    "page_views_total",
    "page_video_views"
]

for m in common_metrics:
    res = requests.get(f"https://graph.facebook.com/v20.0/{p['id']}/insights/{m}?access_token={token}")
    print(f"Metric {m}: status={res.status_code}, data={res.text[:120]}")
