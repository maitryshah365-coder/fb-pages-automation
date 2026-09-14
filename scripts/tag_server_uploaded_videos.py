import json
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "posted_videos.db")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT page_id, filename, facebook_video_id, posted_at, status FROM videos WHERE status = 'posted' ORDER BY posted_at DESC")
db_rows = c.fetchall()
conn.close()

db_map = {str(r[2]): {'page_id': str(r[0]), 'filename': r[1], 'facebook_video_id': str(r[2]), 'posted_at': r[3]} for r in db_rows}

print(f"Total server posted videos in DB: {len(db_map)}")

for rel_path in ['docs/data/pages_data.json', 'web/data/pages_data.json']:
    full_path = os.path.join(BASE_DIR, rel_path)
    if not os.path.exists(full_path):
        continue
    with open(full_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    server_uploaded_videos = []
    seen = set()

    for p in data.get('pages', []):
        for v in p.get('videos', []):
            vid = str(v.get('id'))
            if vid in db_map:
                v['server_uploaded'] = True
                v['page_name'] = p.get('name')
                v['page_id'] = p.get('id')
                v['filename'] = db_map[vid]['filename']
                v['posted_at'] = db_map[vid]['posted_at']
                if vid not in seen:
                    seen.add(vid)
                    server_uploaded_videos.append(v)
            else:
                v['server_uploaded'] = False

    # Sort server uploaded videos by posted_at or created_time_iso descending (newest first)
    server_uploaded_videos.sort(key=lambda x: x.get('posted_at') or x.get('created_time_iso') or '', reverse=True)
    data['server_uploaded_videos'] = server_uploaded_videos

    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Updated {rel_path}: tagged {len(server_uploaded_videos)} server uploaded videos.")

# Also save standalone docs/data/server_uploaded_videos.json for instant fetch/debug
standalone_path = os.path.join(BASE_DIR, "docs", "data", "server_uploaded_videos.json")
with open(standalone_path, 'w', encoding='utf-8') as f:
    json.dump(server_uploaded_videos, f, indent=2, ensure_ascii=False)

web_standalone = os.path.join(BASE_DIR, "web", "data", "server_uploaded_videos.json")
with open(web_standalone, 'w', encoding='utf-8') as f:
    json.dump(server_uploaded_videos, f, indent=2, ensure_ascii=False)

print("Saved standalone server_uploaded_videos.json")
