import json
import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "posted_videos.db")
SUMMARY_PATH = os.path.join(BASE_DIR, "docs", "data", "latest_run_summary.json")

# 1. Read SQLite DB
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT page_id, filename, facebook_video_id, posted_at, status FROM videos WHERE status = 'posted' ORDER BY posted_at DESC")
db_rows = c.fetchall()
conn.close()

db_map = {}
for r in db_rows:
    fbid = str(r[2])
    db_map[fbid] = {
        'page_id': str(r[0]),
        'filename': r[1],
        'facebook_video_id': fbid,
        'posted_at': r[3]
    }
print(f"Total server posted videos in DB: {len(db_map)}")

# 2. Read latest run summary
latest_results = []
if os.path.exists(SUMMARY_PATH):
    with open(SUMMARY_PATH, 'r', encoding='utf-8') as f:
        summary_data = json.load(f)
        latest_results = summary_data.get("results", [])
        summary_completed_at = summary_data.get("completed_at", "2026-09-17T19:29:50+00:00")
        for r in latest_results:
            if r.get("status") == "success" and r.get("facebook_video_id"):
                fbid = str(r.get("facebook_video_id"))
                if fbid not in db_map:
                    db_map[fbid] = {
                        'page_id': str(r.get("page_id", "")),
                        'filename': r.get("filename", "Reel.mp4"),
                        'facebook_video_id': fbid,
                        'posted_at': r.get("uploaded_at") or summary_completed_at
                    }

print(f"Total server posted videos after merging latest summary: {len(db_map)}")

# Update pages_data.json for both docs/ and web/
for rel_path in ['docs/data/pages_data.json', 'web/data/pages_data.json']:
    full_path = os.path.join(BASE_DIR, rel_path)
    if not os.path.exists(full_path):
        continue
    with open(full_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Map pages by ID and by config name (page_1, page_2, etc.)
    page_map = {str(p.get("id")): p for p in data.get("pages", [])}
    cfg_name_map = {f"page_{p.get('index')}": p for p in data.get("pages", [])}

    # Ensure all DB videos exist in their page's videos array
    for fbid, sinfo in db_map.items():
        pid = sinfo['page_id']
        p = page_map.get(pid)
        if not p:
            # try finding page from latest_results
            for r in latest_results:
                if str(r.get("facebook_video_id")) == fbid:
                    p = cfg_name_map.get(r.get("page")) or page_map.get(str(r.get("page_id")))
                    break
        if not p:
            continue

        exists = any(str(v.get("id")) == fbid for v in p.get("videos", []))
        if not exists:
            iso = sinfo["posted_at"]
            try:
                clean_iso = iso.replace("+0000", "+00:00")
                c_dt = datetime.fromisoformat(clean_iso)
                disp_date = c_dt.strftime("%b %d, %Y")
                disp_time = c_dt.strftime("%I:%M %p")
            except Exception:
                disp_date = "Sep 17, 2026"
                disp_time = "07:29 PM"

            clean_title = sinfo["filename"].rsplit(".", 1)[0][:55]
            new_v = {
                "id": fbid,
                "title": clean_title,
                "description": sinfo["filename"],
                "created_at": disp_date,
                "created_time": disp_time,
                "created_time_iso": iso,
                "posted_at": iso,
                "views": 0,
                "likes": 0,
                "comments": 0,
                "subscribers_gain": "+0",
                "visibility": "Public",
                "restrictions": "None",
                "page_name": p.get("name"),
                "page_id": str(p.get("id")),
                "thumbnail": f"https://graph.facebook.com/v20.0/{fbid}/picture",
                "permalink": f"/reel/{fbid}/",
                "server_uploaded": True,
                "source": "server"
            }
            p.setdefault("videos", []).insert(0, new_v)

    # Now mark server_uploaded and source correctly on all videos
    server_uploaded_videos = []
    seen = set()

    for p in data.get('pages', []):
        for v in p.get('videos', []):
            vid = str(v.get('id'))
            if vid in db_map:
                v['server_uploaded'] = True
                v['source'] = 'server'
                v['page_name'] = p.get('name')
                v['page_id'] = p.get('id')
                v['filename'] = db_map[vid]['filename']
                v['posted_at'] = db_map[vid]['posted_at']
                
                iso = v.get('posted_at') or v.get('created_time_iso')
                if iso:
                    try:
                        clean_iso = iso.replace("+0000", "+00:00")
                        c_dt = datetime.fromisoformat(clean_iso)
                        v['created_at'] = c_dt.strftime("%b %d, %Y")
                        v['created_time'] = c_dt.strftime("%I:%M %p")
                    except Exception:
                        pass
                
                if vid not in seen:
                    seen.add(vid)
                    server_uploaded_videos.append(v)
            else:
                # Meta Graph discovered or existing reel
                if v.get('server_uploaded') is None:
                    v['server_uploaded'] = False

    # Sort server uploaded videos newest first
    server_uploaded_videos.sort(key=lambda x: x.get('posted_at') or x.get('created_time_iso') or '', reverse=True)
    data['server_uploaded_videos'] = server_uploaded_videos

    # Recalculate today's posts per page strictly for today's date
    today_prefix = datetime.utcnow().strftime("%Y-%m-%d")
    today_posts_by_page = {}
    for r in db_map.values():
        if r['posted_at'].startswith(today_prefix):
            pid = str(r['page_id'])
            today_posts_by_page[pid] = today_posts_by_page.get(pid, 0) + 1

    total_today_uploaded = 0
    for p in data.get('pages', []):
        pid = str(p.get('id'))
        p['today_posts'] = today_posts_by_page.get(pid, 0)
        total_today_uploaded += p['today_posts']
        p['is_configured'] = True

    active_pages_count = len(data.get('pages', [])) # 30 active pages
    target_total = active_pages_count * 4           # 120 target slots

    if 'today_summary' in data:
        data['today_summary']['target_total'] = target_total
        data['today_summary']['uploaded'] = total_today_uploaded
        data['today_summary']['remaining'] = max(0, target_total - total_today_uploaded)
        data['today_summary']['active_pages_count'] = active_pages_count

    # Update latest_run_summary in pages_data
    if os.path.exists(SUMMARY_PATH):
        with open(SUMMARY_PATH, 'r', encoding='utf-8') as f_sum:
            data['latest_run_summary'] = json.load(f_sum)

    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Updated {rel_path}: {len(server_uploaded_videos)} server uploaded reels, today uploaded: {total_today_uploaded}/{target_total}.")

# Save standalone server_uploaded_videos.json
for out_rel in ["docs/data/server_uploaded_videos.json", "web/data/server_uploaded_videos.json"]:
    out_path = os.path.join(BASE_DIR, out_rel)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(server_uploaded_videos, f, indent=2, ensure_ascii=False)
    print(f"Saved {out_rel} with {len(server_uploaded_videos)} reels.")
