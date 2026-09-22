import os
import re
import sqlite3
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "posted_videos.db")
LOG_PATH = os.path.join(BASE_DIR, "temp_logs_usa", "facebook-logs-35761682791", "run_20260922_173606.log")

def recover():
    if not os.path.exists(LOG_PATH):
        print(f"Log path not found: {LOG_PATH}")
        return

    with open(LOG_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    posts = []
    curr = {}

    for line in lines:
        m_page = re.search(r'Processing Page: (page_\d+) \(ID: (\d+)', line)
        if m_page:
            curr['page_label'] = m_page.group(1)
            curr['page_id'] = m_page.group(2)
        m_file = re.search(r'Selected unposted file: \'(.*?)\' \(ID: (.*?)\)', line)
        if m_file:
            curr['filename'] = m_file.group(1)
            curr['drive_file_id'] = m_file.group(2)
        m_insp = re.search(r'Video inspection: Duration=([\d\.]+)s, Dimensions=(\d+x\d+), Chosen Route: (.*)', line)
        if m_insp:
            curr['duration'] = float(m_insp.group(1))
            curr['aspect_ratio'] = m_insp.group(2)
            curr['route'] = m_insp.group(3)
        m_pub = re.search(r'\[(.*?)\] \[INFO\] \[(\d+)\] (Reel|Classic Video) successfully published! Video ID: (\d+)', line)
        if m_pub:
            dt_str = m_pub.group(1) # e.g. 2026-09-22 17:36:52
            # convert to ISO format with UTC timezone
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            curr['posted_at'] = dt.isoformat()
            curr['post_type'] = 'reel' if 'Reel' in m_pub.group(3) else 'video'
            curr['facebook_video_id'] = m_pub.group(4)
            posts.append(dict(curr))
            curr = {}

    print(f"Found {len(posts)} published posts in USA run log.")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    inserted_videos = 0
    inserted_runs = 0

    for p in posts:
        pid = p['page_id']
        fvid = p['facebook_video_id']
        dfid = p['drive_file_id']
        fn = p['filename']
        dur = p.get('duration', 60.0)
        ar = p.get('aspect_ratio', '720x1280')
        ptype = p.get('post_type', 'reel')
        pat = p['posted_at']

        # Check existing in videos
        cur.execute("SELECT id FROM videos WHERE facebook_video_id = ? OR (page_id = ? AND drive_file_id = ?)", (fvid, pid, dfid))
        exists_v = cur.fetchone()
        if not exists_v:
            cur.execute("""
                INSERT INTO videos (
                    page_id, drive_file_id, filename, mime_type, post_type, status,
                    facebook_video_id, duration_seconds, aspect_ratio, first_seen_at,
                    selected_at, posted_at, last_attempt_at, retry_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pid, dfid, fn, 'video/mp4', ptype, 'posted',
                fvid, dur, ar, pat, pat, pat, pat, 0
            ))
            inserted_videos += 1

        # Check existing in runs
        cur.execute("SELECT id FROM runs WHERE facebook_video_id = ? OR (page_id = ? AND run_id = '35761682791')", (fvid, pid))
        exists_r = cur.fetchone()
        if not exists_r:
            cur.execute("""
                INSERT INTO runs (
                    page_id, run_id, started_at, finished_at, status, drive_files_seen,
                    selected_drive_file_id, facebook_video_id, runner_ip, runner_city,
                    runner_region, runner_country, runner_country_code, runner_org
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pid, '35761682791', pat, pat, 'success', 1,
                dfid, fvid, '52.161.75.162', 'Cheyenne', 'Wyoming', 'United States', 'US', 'AS8075 Microsoft Corporation'
            ))
            inserted_runs += 1

    conn.commit()
    conn.close()

    print(f"Successfully inserted {inserted_videos} videos and {inserted_runs} runs into {DB_PATH}")

if __name__ == "__main__":
    recover()
