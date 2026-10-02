import sqlite3
import json

conn = sqlite3.connect("data/posted_videos.db")
c = conn.cursor()

print("="*60)
print("1. DAILY POST SUMMARY (LAST 14 DAYS)")
print("="*60)
c.execute("""
    SELECT substr(posted_at, 1, 10) as post_date, count(*) as cnt 
    FROM videos 
    WHERE status = 'posted' AND posted_at IS NOT NULL
    GROUP BY post_date 
    ORDER BY post_date DESC 
    LIMIT 14
""")
for row in c.fetchall():
    print(f"  [DATE] {row[0]}: {row[1]} videos posted successfully")

print("\n" + "="*60)
print("2. POSTS PER PAGE TODAY (2026-10-02)")
print("="*60)
c.execute("""
    SELECT page_id, count(*) as cnt, max(posted_at) as latest_post
    FROM videos
    WHERE status = 'posted' AND posted_at LIKE '2026-10-02%'
    GROUP BY page_id
    ORDER BY cnt DESC
""")
today_posts = c.fetchall()
print(f"Total pages that posted today: {len(today_posts)}")
for p in today_posts:
    print(f"  [PAGE] Page ID {p[0]}: {p[1]} posts (Latest: {p[2]})")

print("\n" + "="*60)
print("3. RECENT RUN FAILURES OR ANOMALIES (LAST 25 RUNS)")
print("="*60)
c.execute("""
    SELECT id, page_id, started_at, status, error_message 
    FROM runs 
    WHERE status != 'success' AND status != 'completed'
    ORDER BY id DESC 
    LIMIT 25
""")
failed_runs = c.fetchall()
if not failed_runs:
    print("  [SUCCESS] No failed runs recorded recently!")
else:
    for r in failed_runs:
        print(f"  [ANOMALY] Run #{r[0]} | Page: {r[1]} | {r[2]} | Status: '{r[3]}' | Error: {r[4]}")

print("\n" + "="*60)
print("4. TOTAL VIDEOS EVER POSTED ACROSS ALL PAGES")
print("="*60)
c.execute("SELECT count(*) FROM videos WHERE status = 'posted'")
total_posts = c.fetchone()[0]
print(f"  [TOTAL] Grand Total Posted Videos in DB: {total_posts}")

print("\n" + "="*60)
print("5. FAILED VIDEOS AWAITING RETRY OR PERMANENTLY FAILED")
print("="*60)
c.execute("""
    SELECT status, count(*) 
    FROM videos 
    WHERE status != 'posted' 
    GROUP BY status
""")
for s in c.fetchall():
    print(f"  Status: {s[0]} -> {s[1]} videos")
