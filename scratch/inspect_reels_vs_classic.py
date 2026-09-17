import sqlite3, json, requests, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('data/posted_videos.db')
c = conn.cursor()

c.execute("SELECT id, page_id, facebook_video_id, filename, post_type, duration_seconds, aspect_ratio, posted_at FROM videos WHERE post_type = 'reel'")
reels = c.fetchall()
print(f"Total 'reel' posts: {len(reels)}")
for r in reels:
    print(r)

c.execute("SELECT id, page_id, facebook_video_id, filename, post_type, duration_seconds, aspect_ratio, posted_at FROM videos WHERE post_type = 'classic_video' LIMIT 10")
classic = c.fetchall()
print(f"\nSample 'classic_video' posts:")
for r in classic:
    print(r)
