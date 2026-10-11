import json
import os
import glob
from datetime import datetime, timezone

def audit():
    print("=== STARTING COMPREHENSIVE FACEBOOK SUITE AUDIT ===")
    pages_path = 'docs/data/pages_data.json'
    history_path = 'docs/data/upload_history.json'
    server_path = 'docs/data/server_uploaded_videos.json'

    # 1. Check pages_data.json
    if not os.path.exists(pages_path):
        print(f"ERROR: {pages_path} missing!")
        return

    with open(pages_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    pages = data.get('pages', [])
    print(f"Total Pages: {len(pages)}")

    total_followers = sum(int(p.get('followers_count', 0) or 0) for p in pages)
    total_lifetime_views = sum(int(p.get('total_views', 0) or 0) for p in pages)
    all_videos = []
    for p in pages:
        for v in p.get('videos', []):
            all_videos.append(v)

    print(f"Total Followers across fleet: {total_followers:,}")
    print(f"Total Lifetime Views sum(total_views): {total_lifetime_views:,}")
    print(f"Total Videos in pages: {len(all_videos):,}")

    video_views_sum = sum(int(v.get('views', 0) or 0) for v in all_videos)
    print(f"Sum of views in all individual video objects: {video_views_sum:,}")

    # Inspect 0 view pages
    zero_view_pages = [p for p in pages if (p.get('total_views') or 0) == 0]
    zero_video_pages = [p for p in pages if not p.get('videos')]
    pages_with_videos_but_zero_views = [p for p in pages if p.get('videos') and (p.get('total_views') or 0) == 0]

    print(f"\n--- ZERO VIEW ANALYSIS ---")
    print(f"Pages with 0 total_views: {len(zero_view_pages)}")
    print(f"Pages with 0 videos attached: {len(zero_video_pages)}")
    print(f"Pages with videos attached but 0 total_views: {len(pages_with_videos_but_zero_views)}")

    if pages_with_videos_but_zero_views:
        for p in pages_with_videos_but_zero_views[:10]:
            v_count = len(p.get('videos', []))
            v_views = sum(int(v.get('views', 0) or 0) for v in p.get('videos', []))
            print(f"  * {p.get('name')} (ID: {p.get('id')}): {v_count} videos, sum(views)={v_views}")

    # Inspect videos with 0 views
    zero_view_videos = [v for v in all_videos if (v.get('views') or 0) == 0]
    print(f"Total videos with 0 views: {len(zero_view_videos)} / {len(all_videos)} ({len(zero_view_videos)/max(1, len(all_videos))*100:.1f}%)")

    # Inspect today's videos
    today_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    today_vids = [v for v in all_videos if (v.get('posted_at') or v.get('created_time_iso') or '')[:10] == today_utc]
    today_views = sum(int(v.get('views', 0) or 0) for v in today_vids)
    print(f"\n--- TODAY'S REELS (UTC: {today_utc}) ---")
    print(f"Count: {len(today_vids)}")
    print(f"Views: {today_views:,}")

    # 2. Check upload_history.json
    if os.path.exists(history_path):
        with open(history_path, 'r', encoding='utf-8') as f:
            hdata = json.load(f)
        h_list = hdata.get('history', [])
        print(f"\n--- UPLOAD HISTORY ---")
        print(f"Total records in history: {len(h_list)}")
        print(f"Total DB posted: {hdata.get('total_db_posted')}")
        h_today = [h for h in h_list if (h.get('posted_at') or '')[:10] == today_utc]
        print(f"Today uploads in history: {len(h_today)}")
    else:
        print(f"WARNING: {history_path} not found")

    # 3. Check server_uploaded_videos.json
    if os.path.exists(server_path):
        with open(server_path, 'r', encoding='utf-8') as f:
            s_list = json.load(f)
        print(f"\n--- SERVER UPLOADED VIDEOS ---")
        print(f"Count: {len(s_list)}")
    else:
        print(f"WARNING: {server_path} not found")

    # 4. Check web/ mirror
    print(f"\n--- WEB/ VS DOCS/ SYNCHRONIZATION ---")
    for fname in ['pages_data.json', 'upload_history.json', 'server_uploaded_videos.json', 'js/gold_app.js', 'index.html']:
        d_p = os.path.join('docs', fname)
        w_p = os.path.join('web', fname)
        if os.path.exists(d_p) and os.path.exists(w_p):
            d_sz = os.path.getsize(d_p)
            w_sz = os.path.getsize(w_p)
            match = "MATCH" if d_sz == w_sz else f"MISMATCH ({d_sz} vs {w_sz})"
            print(f"  {fname}: {match}")
        else:
            print(f"  {fname}: missing in one of docs/ or web/")

if __name__ == '__main__':
    audit()
