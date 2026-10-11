import os
import sys
import json
import sqlite3
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = r"E:\Anty Working\Google_Drive_to_Facebook_Automation_Master_Spec"
PAGES_JSON_DOCS = os.path.join(BASE_DIR, "docs", "data", "pages_data.json")
PAGES_JSON_WEB = os.path.join(BASE_DIR, "web", "data", "pages_data.json")
DB_PATH = os.path.join(BASE_DIR, "data", "posted_videos.db")
HISTORY_JSON = os.path.join(BASE_DIR, "docs", "data", "upload_history.json")

print("=" * 80)
print("     REAL-TIME FACEBOOK FLEET AUDIT & 0-VIEW SYNC ENGINE")
print("=" * 80)

# 1. Load pages_data.json
with open(PAGES_JSON_DOCS, "r", encoding="utf-8") as f:
    master_data = json.load(f)

pages = master_data.get("pages", [])
print(f"Loaded {len(pages)} Facebook Pages from pages_data.json")

# 2. Function to process one page's 0-view & server-uploaded reels
def sync_page_views(page):
    pid = str(page.get("id"))
    pname = page.get("name", "Page")
    tok = page.get("access_token")
    if not tok:
        return {"page_id": pid, "page_name": pname, "checked": 0, "updated": 0, "gain": 0}

    videos = page.get("videos", [])
    if not videos:
        return {"page_id": pid, "page_name": pname, "checked": 0, "updated": 0, "gain": 0}

    # Focus on 0-view videos or server uploaded videos
    target_vids = [v for v in videos if (v.get("views", 0) == 0 or v.get("server_uploaded")) and v.get("id")]
    if not target_vids:
        return {"page_id": pid, "page_name": pname, "checked": 0, "updated": 0, "gain": 0}

    vid_map = {str(v["id"]): v for v in target_vids}
    checked_count = len(target_vids)
    updated_count = 0
    views_gain = 0

    # Batch query in chunks of 50
    chunks = [list(vid_map.keys())[i:i+50] for i in range(0, len(vid_map), 50)]
    for chunk in chunks:
        batch = [
            {"method": "GET", "relative_url": f"{vid_id}?fields=id,views,likes.summary(true),comments.summary(true)"}
            for vid_id in chunk
        ]
        try:
            res = requests.post(
                "https://graph.facebook.com/v20.0/",
                data={"access_token": tok, "batch": json.dumps(batch)},
                timeout=20
            ).json()

            for item in res:
                if item.get("code") == 200:
                    body = json.loads(item.get("body", "{}"))
                    rid = str(body.get("id"))
                    if rid in vid_map:
                        live_v = body.get("views", 0)
                        live_likes = body.get("likes", {}).get("summary", {}).get("total_count", 0)
                        live_comm = body.get("comments", {}).get("summary", {}).get("total_count", 0)

                        target_obj = vid_map[rid]
                        prev_v = target_obj.get("views", 0)

                        if live_v > prev_v or live_likes > target_obj.get("likes", 0):
                            views_gain += (live_v - prev_v)
                            target_obj["views"] = live_v
                            target_obj["likes"] = live_likes
                            target_obj["comments"] = live_comm
                            if live_v > 100:
                                target_obj["subscribers_gain"] = f"+{max(0, int(live_v * 0.003))}"
                            updated_count += 1
        except Exception:
            pass

    return {
        "page_id": pid,
        "page_name": pname,
        "checked": checked_count,
        "updated": updated_count,
        "gain": views_gain
    }

print("\n--> Starting High-Speed Multi-Threaded Sync across all pages...")
total_checked_reels = 0
total_updated_reels = 0
total_views_gained = 0
pages_with_updates = []

with ThreadPoolExecutor(max_workers=16) as executor:
    futures = [executor.submit(sync_page_views, p) for p in pages]
    for fut in as_completed(futures):
        res = fut.result()
        total_checked_reels += res["checked"]
        total_updated_reels += res["updated"]
        total_views_gained += res["gain"]
        if res["updated"] > 0:
            pages_with_updates.append(res)
            print(f"  [+] [{res['page_name']}] Synced {res['updated']} reels! (+{res['gain']:,} views)")

print("\n" + "-" * 80)
print(f"SYNC RESULTS: Checked {total_checked_reels} reels | Synced {total_updated_reels} reels | Gained +{total_views_gained:,} new views!")
print("-" * 80)

# 3. Recalculate Page & Portfolio Lifetime Stats
total_portfolio_views = 0
total_portfolio_followers = 0
total_portfolio_videos = 0

for p in pages:
    p_vids = p.get("videos", [])
    # Recalculate page sum of views
    p_views_sum = sum(v.get("views", 0) for v in p_vids)
    # Ensure total_views reflects at least the sum of tracked videos
    p["total_views"] = max(p.get("total_views", 0), p_views_sum)
    p_foll = int(p.get("followers") or 0)

    total_portfolio_views += p["total_views"]
    total_portfolio_followers += p_foll
    total_portfolio_videos += len(p_vids)

if "portfolio" in master_data:
    master_data["portfolio"]["total_views"] = total_portfolio_views
    master_data["portfolio"]["total_followers"] = total_portfolio_followers
    master_data["portfolio"]["total_videos"] = total_portfolio_videos

master_data["synced_at"] = datetime.now(timezone.utc).isoformat()

# 4. Save to docs/data/pages_data.json and web/data/pages_data.json
for out_path in [PAGES_JSON_DOCS, PAGES_JSON_WEB]:
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(master_data, f, indent=2, ensure_ascii=False)
    print(f"  ✅ Saved updated pages data to: {out_path}")

# 5. Sync missing videos from posted_videos.db into upload_history.json
if os.path.exists(DB_PATH) and os.path.exists(HISTORY_JSON):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT page_id, filename, facebook_video_id, posted_at, status FROM videos WHERE status = 'posted' ORDER BY posted_at DESC")
    db_rows = c.fetchall()
    conn.close()

    with open(HISTORY_JSON, "r", encoding="utf-8") as f:
        hist_data = json.load(f)

    existing_history = hist_data.get("history", []) if isinstance(hist_data, dict) else (hist_data if isinstance(hist_data, list) else [])
    existing_vids = {str(h.get("id") or h.get("video_id") or ""): h for h in existing_history}

    page_name_lookup = {str(p.get("id")): p.get("name") for p in pages}

    added_to_history = 0
    for r in db_rows:
        fbid = str(r[2])
        if fbid and fbid not in existing_vids:
            pid = str(r[0])
            pname = page_name_lookup.get(pid, f"Page {pid}")
            iso = r[3]
            try:
                c_dt = datetime.fromisoformat(iso.replace("+0000", "+00:00"))
                disp_date = c_dt.strftime("%b %d, %Y")
                disp_time = c_dt.strftime("%I:%M %p")
            except Exception:
                disp_date = "Recent"
                disp_time = "12:00 PM"

            item = {
                "id": fbid,
                "video_id": fbid,
                "page_id": pid,
                "page_name": pname,
                "title": r[1].rsplit(".", 1)[0][:60],
                "filename": r[1],
                "posted_at": iso,
                "date": disp_date,
                "time": disp_time,
                "status": "success",
                "post_type": "reel"
            }
            existing_history.append(item)
            existing_vids[fbid] = item
            added_to_history += 1

    # Sort newest first
    existing_history.sort(key=lambda x: str(x.get("posted_at") or ""), reverse=True)
    if isinstance(hist_data, dict):
        hist_data["history"] = existing_history
        hist_data["total_count"] = len(existing_history)
        hist_data["last_synced_at"] = datetime.now(timezone.utc).isoformat()
        out_hist = hist_data
    else:
        out_hist = existing_history

    with open(HISTORY_JSON, "w", encoding="utf-8") as f:
        json.dump(out_hist, f, indent=2, ensure_ascii=False)
    print(f"  ✅ Synced {added_to_history} previously missing videos into upload_history.json! (Total: {len(existing_history)})")

print("\n" + "=" * 80)
print(f"AUDIT & LIVE SYNC COMPLETE! Total Fleet Views: {total_portfolio_views:,}")
print("=" * 80)
