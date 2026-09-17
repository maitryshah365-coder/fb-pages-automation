import json, requests, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('docs/data/pages_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for p in data.get('pages', []):
    pid = str(p['id'])
    pname = p.get('name')
    tok = p.get('access_token')
    if not tok:
        continue
    r = requests.get(f"https://graph.facebook.com/v20.0/{pid}", params={
        "fields": "id,name,is_published,verification_status,can_post,followers_count",
        "access_token": tok
    }).json()
    print(f"Page {p.get('index')}: {pname} (ID: {pid}) -> Published: {r.get('is_published')}, CanPost: {r.get('can_post')}, Followers: {r.get('followers_count')}")
