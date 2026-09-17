import json

with open('docs/data/pages_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('Portfolio views:', data.get('portfolio', {}).get('total_views'))
for p in data.get('pages', []):
    vids = p.get('videos', [])
    page_views = sum(v.get('views', 0) for v in vids)
    server_vids = [v for v in vids if v.get('server_uploaded')]
    print(f"{p.get('name')}: total videos={len(vids)}, server_vids={len(server_vids)}, total views={page_views}")
    if vids:
        sorted_vids = sorted(vids, key=lambda x: x.get('views', 0), reverse=True)[:3]
        for sv in sorted_vids:
            print(f"   Top vid {sv.get('id')}: views={sv.get('views')}, server_up={sv.get('server_uploaded')}, title={sv.get('title')[:30] if sv.get('title') else ''}")
