import json
import os

target_ids = {'755318371007926', '857530914106167'}
target_names = {'alexander christopher', 'robinson jerry'}

files_to_check = [
    'data/uk_account4_nidhi_pages.json',
    'data/uk_account7_riya_pages.json',
    'data/uk_account7_riya_pages_raw.json',
    'data/profiles/uk_account4_nidhi/pages.json',
    'data/profiles/uk_account7_riya/pages.json',
    'docs/data/profiles/uk_account4_nidhi/pages.json',
    'docs/data/profiles/uk_account7_riya/pages.json',
    'web/data/profiles/uk_account4_nidhi/pages.json',
    'web/data/profiles/uk_account7_riya/pages.json',
    'data/master_fleet_monetization.json',
    'docs/data/master_fleet_monetization.json',
    'web/data/master_fleet_monetization.json',
    'data/drive_verified_stock_audit.json',
    'token_audit_report.json'
]

for fpath in files_to_check:
    if not os.path.exists(fpath):
        continue
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading {fpath}: {e}")
        continue
    
    modified = False
    if isinstance(data, list):
        orig_len = len(data)
        data = [item for item in data if not (
            str(item.get('id', item.get('page_id', ''))).strip() in target_ids or
            item.get('name', '').strip().lower() in target_names
        )]
        if len(data) != orig_len:
            modified = True
            print(f'{fpath}: filtered list from {orig_len} to {len(data)}')
    elif isinstance(data, dict):
        if 'accounts' in data:
            for acc in data['accounts']:
                if 'pages' in acc:
                    orig_len = len(acc['pages'])
                    acc['pages'] = [p for p in acc['pages'] if not (
                        str(p.get('id', p.get('page_id', ''))).strip() in target_ids or
                        p.get('name', '').strip().lower() in target_names
                    )]
                    if len(acc['pages']) != orig_len:
                        modified = True
                        print(f"{fpath} (acc {acc.get('account_id', '')}): filtered pages from {orig_len} to {len(acc['pages'])}")
        if 'data' in data and isinstance(data['data'], list):
            orig_len = len(data['data'])
            data['data'] = [p for p in data['data'] if not (
                str(p.get('id', p.get('page_id', ''))).strip() in target_ids or
                p.get('name', '').strip().lower() in target_names
            )]
            if len(data['data']) != orig_len:
                modified = True
                print(f'{fpath} data list: filtered from {orig_len} to {len(data["data"])}')
        if 'pages' in data and isinstance(data['pages'], list):
            orig_len = len(data['pages'])
            data['pages'] = [p for p in data['pages'] if not (
                str(p.get('id', p.get('page_id', ''))).strip() in target_ids or
                p.get('name', '').strip().lower() in target_names
            )]
            if len(data['pages']) != orig_len:
                modified = True
                print(f'{fpath} pages: filtered from {orig_len} to {len(data["pages"])}')
        if 'pages' in data and isinstance(data['pages'], dict):
            for pid in list(data['pages'].keys()):
                if pid in target_ids:
                    del data['pages'][pid]
                    modified = True
                    print(f'{fpath}: deleted key {pid}')

    if modified:
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f'Saved cleaned {fpath}')
