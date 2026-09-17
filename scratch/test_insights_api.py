import json
import requests

with open('docs/data/pages_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for p in d.get('pages', [])[:5]:
    pid = p['id']
    name = p.get('name')
    token = p.get('access_token', '')
    print(f"\n=== Testing Page: {name} ({pid}) ===")
    if not token:
        print("No token")
        continue

    # 1. Page Details
    r1 = requests.get(f"https://graph.facebook.com/v20.0/{pid}?fields=name,followers_count,fan_count,verification_status,tasks&access_token={token}")
    print("Page info:", r1.json())

    # 2. Insights test metrics
    metrics = [
        "page_impressions_by_country_unique",
        "page_fans_country",
        "page_fans_gender_age",
        "page_views_total",
        "page_video_views",
        "page_post_engagements",
        "page_daily_follows_unique",
        "page_daily_unfollows_unique"
    ]
    r2 = requests.get(f"https://graph.facebook.com/v20.0/{pid}/insights", params={
        "metric": ",".join(metrics),
        "period": "day",
        "access_token": token
    })
    print("Insights Day status:", r2.status_code)
    if r2.status_code == 200:
        data = r2.json().get('data', [])
        print(f"Returned {len(data)} insight metrics: {[item['name'] for item in data]}")
        for item in data:
            values = item.get('values', [])
            latest = values[-1] if values else {}
            print(f"  - {item['name']}: {latest}")
    else:
        print("Insights error:", r2.text)
