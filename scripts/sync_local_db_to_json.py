import json
import sqlite3
import os
from datetime import datetime, timezone, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "posted_videos.db")
SUMMARY_PATH = os.path.join(BASE_DIR, "docs", "data", "latest_run_summary.json")
HISTORY_PATH = os.path.join(BASE_DIR, "docs", "data", "upload_history.json")

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
        summary_completed_at = summary_data.get("completed_at", datetime.now(timezone.utc).isoformat())
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

# 3. Read upload_history.json and merge into db_map
if os.path.exists(HISTORY_PATH):
    with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
        h_data = json.load(f)
        for h in h_data.get("history", []):
            fbid = str(h.get("id") or h.get("video_id") or "")
            if fbid and fbid not in db_map:
                db_map[fbid] = {
                    'page_id': str(h.get("page_id", "")),
                    'filename': h.get("title", "Uploaded Reel"),
                    'facebook_video_id': fbid,
                    'posted_at': h.get("posted_at") or datetime.now(timezone.utc).isoformat()
                }

print(f"Total server posted videos after merging summary and history: {len(db_map)}")

# Determine today's date prefixes across UTC, EDT (US), BST (UK), and IST (India)
now_utc = datetime.now(timezone.utc)
now_edt = datetime.now(timezone(timedelta(hours=-4)))
now_bst = datetime.now(timezone(timedelta(hours=1)))
now_ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))

today_prefixes = {
    now_utc.strftime("%Y-%m-%d"),
    now_edt.strftime("%Y-%m-%d"),
    now_bst.strftime("%Y-%m-%d"),
    now_ist.strftime("%Y-%m-%d")
}
print(f"Operational today date prefixes: {today_prefixes}")

# Calculate today's posts per page
today_posts_by_page = {}
for fbid, r in db_map.items():
    p_at = str(r.get("posted_at", ""))
    is_today = any(p_at.startswith(pref) for pref in today_prefixes)
    if is_today:
        pid = str(r.get("page_id", ""))
        if pid:
            today_posts_by_page[pid] = today_posts_by_page.get(pid, 0) + 1

print(f"Unique pages with today uploads: {len(today_posts_by_page)}")
print(f"Total today uploads across all pages: {sum(today_posts_by_page.values())}")

# Update pages_data.json for both docs/ and web/
for rel_path in ['docs/data/pages_data.json', 'web/data/pages_data.json']:
    full_path = os.path.join(BASE_DIR, rel_path)
    if not os.path.exists(full_path):
        continue
    with open(full_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    page_map = {str(p.get("id")): p for p in data.get("pages", [])}
    cfg_name_map = {f"page_{p.get('index')}": p for p in data.get("pages", [])}

    # Ensure all DB videos exist in their page's videos array
    for fbid, sinfo in db_map.items():
        pid = sinfo['page_id']
        p = page_map.get(pid)
        if not p:
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
                disp_date = "Recent"
                disp_time = "12:00 PM"

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

    # Mark server_uploaded and sort videos per page, truncate to latest 30
    server_uploaded_videos = []
    seen = set()

    total_today_uploaded = 0
    for p in data.get('pages', []):
        pid = str(p.get('id'))
        
        # Sort page videos newest first
        p_vids = p.get('videos', [])
        p_vids.sort(key=lambda x: str(x.get('posted_at') or x.get('created_time_iso') or x.get('created_at') or ''), reverse=True)
        
        # Count today posts for this page from its videos + db
        t_count = 0
        p_seen_vids = set()
        for v in p_vids:
            vid = str(v.get('id'))
            if vid in db_map:
                v['server_uploaded'] = True
                v['source'] = 'server'
                v['page_name'] = p.get('name')
                v['page_id'] = p.get('id')
                if vid not in seen:
                    seen.add(vid)
                    server_uploaded_videos.append(v)
            
            # Check if this video is today
            v_date = str(v.get('posted_at') or v.get('created_time_iso') or '')
            if any(v_date.startswith(pref) for pref in today_prefixes):
                if vid not in p_seen_vids:
                    p_seen_vids.add(vid)
                    t_count += 1

        db_count = today_posts_by_page.get(pid, 0)
        final_today = max(t_count, db_count)
        p['today_posts'] = final_today
        total_today_uploaded += final_today

        # Keep latest 30 videos per page to ensure fast 4.4MB payload
        p['videos'] = p_vids[:30]
        p['is_configured'] = True

    active_pages_count = len(data.get('pages', [])) # 128 pages
    target_total = active_pages_count * 4           # 512 target slots

    if 'today_summary' in data:
        data['today_summary']['target_total'] = target_total
        data['today_summary']['uploaded'] = total_today_uploaded
        data['today_summary']['remaining'] = max(0, target_total - total_today_uploaded)
        data['today_summary']['active_pages_count'] = active_pages_count

    data['synced_at'] = now_utc.isoformat()

    # Update latest_run_summary in pages_data
    if os.path.exists(SUMMARY_PATH):
        with open(SUMMARY_PATH, 'r', encoding='utf-8') as f_sum:
            data['latest_run_summary'] = json.load(f_sum)

    # Strip legacy bulky root duplicates
    data.pop('server_uploaded_videos', None)
    data.pop('upload_history', None)

    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Updated {rel_path}: today uploaded {total_today_uploaded}/{target_total} across {active_pages_count} pages.")

# Sort standalone server_uploaded_videos newest first and truncate to latest 300
server_uploaded_videos.sort(key=lambda x: str(x.get('posted_at') or x.get('created_time_iso') or ''), reverse=True)
server_uploaded_videos = server_uploaded_videos[:300]

for out_rel in ["docs/data/server_uploaded_videos.json", "web/data/server_uploaded_videos.json"]:
    out_path = os.path.join(BASE_DIR, out_rel)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(server_uploaded_videos, f, indent=2, ensure_ascii=False)
    print(f"Saved {out_rel} with {len(server_uploaded_videos)} reels.")
