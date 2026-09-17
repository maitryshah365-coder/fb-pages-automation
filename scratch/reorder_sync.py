with open('scripts/sync_dashboard_data.py', 'r', encoding='utf-8') as f:
    code = f.read()

marker_fetch = 'def fetch_single_page_record(p, idx, curr_telemetry, posted_by_page, runs_by_page):'
marker_concurrent = '    print(f"Syncing live Meta Graph API data for {len(pages)} pages concurrently...")'

idx_fetch = code.index(marker_fetch)
idx_concurrent = code.index(marker_concurrent)

top_part = code[:code.index('def sync_data():')]
sync_top = code[code.index('def sync_data():'):idx_fetch]
fetch_body = code[idx_fetch:idx_concurrent]
sync_bottom = code[idx_concurrent:]

sync_top = sync_top.replace('    page_records = []\n    total_portfolio_followers = 0\n    total_portfolio_likes = 0\n    total_today_posted = 0\n', '')
sync_top = sync_top.replace('from concurrent.futures import ThreadPoolExecutor\n', '')

final_code = top_part + 'from concurrent.futures import ThreadPoolExecutor\n\n' + fetch_body + '\n' + sync_top + sync_bottom

with open('scripts/sync_dashboard_data.py', 'w', encoding='utf-8') as f:
    f.write(final_code)

print('Restructured cleanly!')
