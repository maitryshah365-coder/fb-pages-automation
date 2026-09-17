import json

with open('docs/data/pages_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Today summary:", data.get("today_summary"))
for p in data.get('pages', []):
    print(f"Page {p.get('index', '?')} ({p.get('name')}): today_posts={p.get('today_posts')}, total_videos={len(p.get('videos', []))}")
