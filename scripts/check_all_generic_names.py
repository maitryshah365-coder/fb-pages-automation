import glob
import yaml
import json

d = json.load(open('docs/data/pages_data.json', encoding='utf-8'))
for p in d['pages']:
    name = str(p.get('name', ''))
    if 'page' in name.lower() or name.isdigit():
        print(f"pages_data.json: #{p.get('index')} ({p.get('id')}): '{name}' ({p.get('account')})")

for yf in sorted(glob.glob('*.yaml')):
    yd = yaml.safe_load(open(yf, encoding='utf-8'))
    if not isinstance(yd, dict):
        continue
    for p in yd.get('pages', []):
        name = str(p.get('name', ''))
        dname = str(p.get('display_name', ''))
        if ('page' in name.lower() or not name) and not dname:
            print(f"{yf}: {p.get('page_id')}: name='{name}', display_name='{dname}'")
