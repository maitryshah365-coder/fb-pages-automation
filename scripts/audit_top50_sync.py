import json
import sqlite3
import os

with open('docs/data/pages_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

pages = data.get('pages', [])

def get_effective_views(p):
    vids = p.get('videos', [])
    vids_views = sum(int(v.get('views', 0) or 0) for v in vids)
    p_views = int(p.get('total_views', 0) or 0)
    return max(vids_views, p_views)

def get_engagement(p):
    eng = p.get('total_engagement', {})
    likes = int(eng.get('likes', 0) or 0)
    comments = int(eng.get('comments', 0) or 0)
    return likes + comments

def get_followers(p):
    return int(p.get('followers', 0) or p.get('fan_count', 0) or 0)

ranked = sorted(pages, key=lambda p: (get_effective_views(p), get_followers(p), get_engagement(p)), reverse=True)
top50 = ranked[:50]

conn = sqlite3.connect('data/posted_videos.db')
cursor = conn.cursor()
tables = [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(f"Database tables in posted_videos.db: {tables}")

# Check schema of the main table
table_name = tables[0] if tables else None
columns = []
if table_name:
    columns = [col[1] for col in cursor.execute(f"PRAGMA table_info({table_name})").fetchall()]
    print(f"Columns in {table_name}: {columns}")

issues = []
synced_top50_records = []

for idx, p in enumerate(top50, 1):
    pid = str(p.get('id', ''))
    name = p.get('name', '')
    tok = p.get('access_token', '')
    folder_id = p.get('drive_folder_id', '')
    tok_status = p.get('token_status', '')
    owner = p.get('account_owner', '')
    views = get_effective_views(p)
    flw = get_followers(p)
    stock = p.get('drive_videos_count', 0)
    reels = len(p.get('videos', []))
    last_up = p.get('last_upload', 'N/A')
    today_posts = p.get('today_posts', 0)
    
    # DB count check
    db_posts = 0
    if table_name and 'page_id' in columns:
        cursor.execute(f"SELECT count(*) FROM {table_name} WHERE page_id = ?", (pid,))
        db_posts = cursor.fetchone()[0]
    
    # Validation checks
    has_token = bool(tok and len(tok) > 15)
    has_folder = bool(folder_id and len(folder_id) > 10)
    name_ok = bool(name and not name.lower().startswith('page ') and not name.lower().startswith('page_') and not name.isdigit())
    
    if not has_token:
        issues.append(f"Rank #{idx:02d} {name} ({pid}): Missing or invalid token")
    if not has_folder:
        issues.append(f"Rank #{idx:02d} {name} ({pid}): Missing drive_folder_id")
    if not name_ok:
        issues.append(f"Rank #{idx:02d} {name} ({pid}): Suspicious page name '{name}'")
    if tok_status != 'active':
        issues.append(f"Rank #{idx:02d} {name} ({pid}): Token status is '{tok_status}'")
        
    synced_top50_records.append({
        "rank": idx,
        "name": name,
        "id": pid,
        "owner": owner,
        "views": views,
        "followers": flw,
        "reels_tracked": reels,
        "db_posts": db_posts,
        "drive_stock": stock,
        "token_status": tok_status,
        "sync_healthy": has_token and has_folder and name_ok and tok_status == 'active'
    })

conn.close()

print(f"\nAudit completed for all 50 Pages:")
print(f"  Total issues detected: {len(issues)}")
if issues:
    for iss in issues:
        print(f"    [!] {iss}")
else:
    print("  [SUCCESS] 50 / 50 Pages rank-wise have 100% HEALTHY SYNC status!")

print(f"\nTop 10 Sample:")
for r in synced_top50_records[:10]:
    print(f"  #{r['rank']:02d} | {r['name']:<22} | {r['owner']:<15} | Views: {r['views']:>10,} | Flws: {r['followers']:>6,} | Sync: {'OK' if r['sync_healthy'] else 'FAIL'}")

print(f"\nRank 41-50 Sample:")
for r in synced_top50_records[40:]:
    print(f"  #{r['rank']:02d} | {r['name']:<22} | {r['owner']:<15} | Views: {r['views']:>10,} | Flws: {r['followers']:>6,} | Sync: {'OK' if r['sync_healthy'] else 'FAIL'}")
