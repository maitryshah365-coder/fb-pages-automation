import json
import requests
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tokens_path = os.path.join(BASE_DIR, 'data', 'uk_account1_binjal_permanent_pages.json')
with open(tokens_path, 'r', encoding='utf-8') as f:
    uk_data = json.load(f)

pages = uk_data if isinstance(uk_data, list) else uk_data.get('pages', [])
summary_path = os.path.join(BASE_DIR, 'data', 'latest_run_summary.json')
with open(summary_path, 'r', encoding='utf-8') as f:
    summary = json.load(f)

print("=== CHECKING UK PUBLISHED REELS STATUS & VIEWS ===")
for r in summary.get('results', []):
    vid = r.get('facebook_video_id')
    pid = str(r.get('page_id'))
    p_name = r.get('display_name')
    token = None
    for p in pages:
        if str(p.get('id') or p.get('page_id')) == pid:
            token = p.get('access_token') or p.get('page_access_token')
            break
    
    if not token or not vid:
        continue

    url = f'https://graph.facebook.com/v20.0/{vid}'
    params = {
        'fields': 'id,status,published,privacy,views,created_time,permalink_url,video_insights',
        'access_token': token
    }
    resp = requests.get(url, params=params).json()
    print(f"\nPage: {p_name} ({pid}) | Video: {vid}")
    print(f"  Published: {resp.get('published')}")
    print(f"  Privacy: {resp.get('privacy')}")
    print(f"  Status: {resp.get('status')}")
    print(f"  Views field: {resp.get('views')}")
    print(f"  Permalink: {resp.get('permalink_url')}")
    if 'error' in resp:
        print(f"  ERROR: {resp['error']}")
    
    # Also check video_insights
    insights_url = f"https://graph.facebook.com/v20.0/{vid}/video_insights"
    i_resp = requests.get(insights_url, params={'metric': 'total_video_views,total_video_impressions', 'access_token': token}).json()
    print(f"  Insights: {i_resp}")
