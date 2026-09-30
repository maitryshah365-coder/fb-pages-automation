import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

with open('docs/data/pages_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print('Total Pages in Dashboard Data:', len(d['pages']))
ts = d.get('today_summary', {})
print(f"Target Total Slots: {ts.get('target_total')}")
print(f"Active Pages Count: {ts.get('active_pages_count')}")

rohini_pages = [p for p in d['pages'] if 'Rohini' in p.get('account', '') or 'Rohini' in p.get('account_owner', '')]
print(f"\nDiscovered {len(rohini_pages)} Rohini Dutt Pages in Dashboard:")
total_stock = 0
for rp in rohini_pages:
    stock = rp.get('drive_videos_count', 0)
    total_stock += stock
    print(f"  #{rp['index']:03d} {rp['name']:22s} | Stock: {stock:3d} reels | Folder: {rp.get('drive_folder_id')}")

print(f"\n🎉 Total Rohini Dutt Stock Synced: {total_stock:,} Videos across {len(rohini_pages)} Pages!")
