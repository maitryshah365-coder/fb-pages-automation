import json
import re

d = json.load(open('docs/data/pages_data.json', encoding='utf-8'))
pages = d.get('pages', [])

with open('docs/js/gold_app.js', 'r', encoding='utf-8') as f:
    js_text = f.read()

drive_map = dict(re.findall(r'"(\d{14,17})":\s*\{\s*pageName:\s*"[^"]+",\s*displayName:\s*"([^"]+)"', js_text))

mismatches = []
for p in pages:
    idx = p.get('index')
    pid = str(p.get('id'))
    name = (p.get('name') or '').strip()
    dname = (p.get('display_name') or '').strip()
    mapped_name = drive_map.get(pid, '').strip()
    # Normalize double spaces
    name_norm = ' '.join(name.split())
    mapped_norm = ' '.join(mapped_name.split())
    if name_norm != mapped_norm:
        mismatches.append((idx, pid, name, dname, mapped_name))

print(f"Total name mismatches / number names: {len(mismatches)} / {len(pages)}")
for idx, pid, name, dname, mapped in mismatches:
    print(f"#{idx:3d} (ID: {pid}) | json_name='{name}' | mapped='{mapped}'")

