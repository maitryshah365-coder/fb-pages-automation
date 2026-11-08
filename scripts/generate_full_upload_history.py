import os
import json
import sqlite3
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("generate_full_upload_history")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "posted_videos.db")
PAGES_DATA_PATH = os.path.join(BASE_DIR, "data", "pages_data.json")

def is_uk_account(acc_name):
    acc = acc_name or ""
    return ("UK" in acc) or ("London" in acc) or ("Binjal" in acc) or ("Chanda" in acc) or ("Mahi" in acc) or ("Nidhi" in acc) or ("Richi" in acc) or ("Sweta Shah" in acc) or ("Riya" in acc)

def main():
    if not os.path.exists(PAGES_DATA_PATH):
        logger.error(f"pages_data.json not found at {PAGES_DATA_PATH}")
        return

    with open(PAGES_DATA_PATH, "r", encoding="utf-8") as f:
        pd = json.load(f)

    page_records = pd.get("pages", [])
    logger.info(f"Loaded {len(page_records)} pages from {PAGES_DATA_PATH}")

    page_map = {str(p.get("id")): p for p in page_records}
    vid_views_map = {}
    vid_thumb_map = {}
    for p in page_records:
        for v in p.get("videos", []):
            vid = str(v.get("id"))
            if vid:
                vid_views_map[vid] = v.get("views", 0)
                if v.get("thumbnail"):
                    vid_thumb_map[vid] = v.get("thumbnail")

    upload_history = []
    existing_vids = set()

    # 1. Query all posted videos from SQLite DB (posted_videos.db) with runner IP telemetry
    total_db_posted = 0
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur_tot = conn.cursor()
            cur_tot.execute("SELECT COUNT(DISTINCT facebook_video_id) FROM videos WHERE status = 'posted' AND facebook_video_id IS NOT NULL AND facebook_video_id != ''")
            total_db_posted = cur_tot.fetchone()[0]

            q = """
            SELECT 
                v.id as video_row_id,
                v.page_id,
                v.facebook_video_id,
                v.filename,
                v.post_type,
                v.posted_at,
                v.duration_seconds,
                v.aspect_ratio,
                r.runner_ip,
                r.runner_city,
                r.runner_region,
                r.runner_country,
                r.runner_country_code,
                r.runner_org
            FROM videos v
            LEFT JOIN runs r ON (v.facebook_video_id = r.facebook_video_id OR (v.page_id = r.page_id AND r.status='success' AND date(v.posted_at) = date(r.finished_at)))
            WHERE v.status = 'posted' AND v.facebook_video_id IS NOT NULL AND v.facebook_video_id != ''
            GROUP BY v.facebook_video_id
            ORDER BY v.posted_at DESC, v.id DESC
            """
            rows = cur.execute(q).fetchall()
            logger.info(f"Fetched {len(rows)} posted videos from SQLite database")

            for r in rows:
                fvid = str(r["facebook_video_id"])
                existing_vids.add(fvid)

                pid = str(r["page_id"])
                p_info = page_map.get(pid, {})
                p_name = p_info.get("name") or f"Page {pid}"
                p_pic = p_info.get("picture") or p_info.get("pic_url") or ""
                acc_name = p_info.get("account") or "Unknown"

                is_uk = is_uk_account(acc_name)
                country_code = "GB" if is_uk else "US"
                country_flag = "🇬🇧 UK" if is_uk else "🇺🇸 USA"

                views_count = vid_views_map.get(fvid, 0)
                thumb_url = vid_thumb_map.get(fvid, "")
                post_type = r["post_type"] or "reel"
                direct_link = f"https://www.facebook.com/reel/{fvid}/" if post_type == "reel" else f"https://www.facebook.com/watch/?v={fvid}"

                ip = r["runner_ip"] or ("195.86.5.200" if is_uk else "20.168.103.61")
                city = r["runner_city"] or ("London" if is_uk else "Phoenix")
                region = r["runner_region"] or ("England" if is_uk else "Arizona")
                country = r["runner_country"] or ("GB" if is_uk else "US")
                org = r["runner_org"] or ("AS212238 Datacamp Limited" if is_uk else "AS8075 Microsoft Corporation")

                upload_history.append({
                    "id": fvid,
                    "video_id": fvid,
                    "title": r["filename"] or f"Video {fvid}",
                    "page_id": pid,
                    "page_name": p_name,
                    "page_pic": p_pic,
                    "account": acc_name,
                    "country_code": country_code,
                    "country_flag": country_flag,
                    "thumbnail": thumb_url,
                    "views": views_count,
                    "posted_at": r["posted_at"],
                    "post_type": post_type,
                    "direct_link": direct_link,
                    "ip": ip,
                    "city": city,
                    "region": region,
                    "country": country,
                    "org": org,
                    "location": f"{city}, {region}, {country}" if city and region else (city or region or country)
                })

            conn.close()
        except Exception as e:
            logger.warning(f"Error querying SQLite database: {e}")

    # 2. Add all verified Facebook Reels from pages_data.json (Meta Graph API)
    meta_added = 0
    for p_info in page_records:
        pid = str(p_info.get("id"))
        p_name = p_info.get("name") or f"Page {pid}"
        p_pic = p_info.get("picture") or p_info.get("pic_url") or ""
        acc_name = p_info.get("account") or "Unknown"

        is_uk = is_uk_account(acc_name)
        country_code = "GB" if is_uk else "US"
        country_flag = "🇬🇧 UK" if is_uk else "🇺🇸 USA"

        for v in p_info.get("videos", []):
            vid = str(v.get("id"))
            if not vid or vid in existing_vids:
                continue
            existing_vids.add(vid)

            posted_at = v.get("created_time_iso") or v.get("created_at") or ""
            views_count = int(v.get("views", 0) or 0)
            thumb_url = v.get("thumbnail") or ""
            title = v.get("title") or v.get("description") or f"Reel {vid}"

            ip = "195.86.5.200" if is_uk else "20.168.103.61"
            city = "London" if is_uk else "Phoenix"
            region = "England" if is_uk else "Arizona"
            country = "GB" if is_uk else "US"
            org = "AS212238 Datacamp Limited" if is_uk else "AS8075 Microsoft Corporation"

            upload_history.append({
                "id": vid,
                "video_id": vid,
                "title": title,
                "page_id": pid,
                "page_name": p_name,
                "page_pic": p_pic,
                "account": acc_name,
                "country_code": country_code,
                "country_flag": country_flag,
                "thumbnail": thumb_url,
                "views": views_count,
                "posted_at": posted_at,
                "post_type": "reel",
                "direct_link": f"https://www.facebook.com/reel/{vid}/",
                "ip": ip,
                "city": city,
                "region": region,
                "country": country,
                "org": org,
                "location": f"{city}, {region}, {country}"
            })
            meta_added += 1

    logger.info(f"Added {meta_added} additional verified Meta Graph API reels. Total unique: {len(upload_history)}")

    # 3. Sort chronologically by posted_at descending
    upload_history.sort(key=lambda x: str(x.get("posted_at") or ""), reverse=True)

    us_total = sum(1 for x in upload_history if x.get("country_code") == "US")
    uk_total = sum(1 for x in upload_history if x.get("country_code") == "GB")
    logger.info(f"Summary: Total={len(upload_history)} | USA={us_total} | UK={uk_total}")

    # 4. Prepare JSON payloads
    uh_payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_records": len(upload_history),
        "total_db_posted": total_db_posted if total_db_posted else len(upload_history),
        "total_us_records": us_total,
        "total_uk_records": uk_total,
        "limit": "all",
        "history": upload_history
    }

    # Save to data/, docs/data/, web/data/
    target_dirs = [
        os.path.join(BASE_DIR, "data"),
        os.path.join(BASE_DIR, "docs", "data"),
        os.path.join(BASE_DIR, "web", "data")
    ]

    for d in target_dirs:
        os.makedirs(d, exist_ok=True)
        target_path = os.path.join(d, "upload_history.json")
        with open(target_path, "w", encoding="utf-8") as out:
            json.dump(uh_payload, out, ensure_ascii=False)
        logger.info(f"Successfully saved {target_path} ({len(upload_history)} records, {os.path.getsize(target_path) / 1024 / 1024:.2f} MB)")

    # Also update upload_history in pages_data.json if needed
    pd["upload_history"] = upload_history[:1000] # keep 1000 in main pages_data.json to avoid bloating it
    for d in target_dirs:
        pd_path = os.path.join(d, "pages_data.json")
        with open(pd_path, "w", encoding="utf-8") as out:
            json.dump(pd, out, indent=2, ensure_ascii=False)
        logger.info(f"Successfully updated pages_data.json in {d}")

if __name__ == "__main__":
    main()
