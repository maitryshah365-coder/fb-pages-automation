import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(BASE_DIR, 'docs', 'data', 'pages_data.json')
with open(data_path, 'r', encoding='utf-8') as f:
    d = json.load(f)

print(f"{'Page Name':25} | {'Account':12} | {'Followers':9} | {'Total Views':11} | {'Recent Server Reel Views'}")
print("-" * 95)

zero_view_pages = []
healthy_pages = []

for p in d.get('pages', []):
    pname = (p.get('name') or 'Page')[:24]
    acc = (p.get('account') or 'A1')[:12]
    foll = p.get('followers', 0)
    t_views = p.get('total_views', 0)
    server_vids = [v for v in p.get('videos', []) if v.get('server_uploaded')]
    recent_views = [v.get('views', 0) for v in server_vids[:5]]
    
    line = f"{pname:25} | {acc:12} | {str(foll):9} | {str(t_views):11} | {recent_views}"
    print(line)
    
    if recent_views and all(v == 0 for v in recent_views):
        zero_view_pages.append(pname)
    elif recent_views and any(v > 0 for v in recent_views):
        healthy_pages.append(pname)

print("\n=== SUMMARY OF FINDINGS ===")
print(f"Zero View Pages Count: {len(zero_view_pages)}")
print(f"Healthy View Pages Count: {len(healthy_pages)}")
