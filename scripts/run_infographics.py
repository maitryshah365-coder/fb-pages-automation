import os
import sys
import json
import argparse
import logging
import requests
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.infographic_db import InfographicDB
from src.infographic_engine import InfographicEngine, AUTHENTIC_VERTICAL_DATA
from src.infographic_scheduler import InfographicScheduler

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("infographic_runner")

BLUEPRINT_PATH = os.path.join(BASE_DIR, "data", "fleet_vertical_blueprint.json")
PAGES_DATA_PATH = os.path.join(BASE_DIR, "docs", "data", "pages_data.json")

def load_fleet_data():
    with open(BLUEPRINT_PATH, "r", encoding="utf-8") as f:
        blueprint = json.load(f)["fleet"]
    
    with open(PAGES_DATA_PATH, "r", encoding="utf-8") as f:
        pages = {str(p["id"]): p for p in json.load(f)["pages"]}
        
    return blueprint, pages

def post_photo_to_facebook(page_id: str, access_token: str, image_path: str, caption: str) -> str:
    """Publishes photo to Facebook Page via Graph API v20.0."""
    url = f"https://graph.facebook.com/v20.0/{page_id}/photos"
    payload = {
        "caption": caption,
        "access_token": access_token
    }
    with open(image_path, "rb") as fh:
        files = {"source": fh}
        res = requests.post(url, data=payload, files=files, timeout=45)
        
    if not res.ok:
        raise RuntimeError(f"Facebook Graph API Error {res.status_code}: {res.text}")
    
    data = res.json()
    photo_id = data.get("id") or data.get("post_id")
    if not photo_id:
        raise RuntimeError(f"Incomplete photo publish response: {res.text}")
    return photo_id

def run_pipeline(
    dry_run: bool = True,
    target_page: str = None,
    target_slot: int = None,
    limit: int = None
):
    blueprint, pages_meta = load_fleet_data()
    db = InfographicDB(os.path.join(BASE_DIR, "data", "posted_videos.db"))
    engine = InfographicEngine()

    current_slot = target_slot if target_slot is not None else InfographicScheduler.get_current_slot_index()
    logger.info(f"=== STARTING INFOGRAPHIC RUNNER (Slot: {current_slot}/5, Dry-Run: {dry_run}) ===")

    filtered_fleet = blueprint
    if target_page:
        filtered_fleet = [p for p in blueprint if target_page.lower() in p["page_name"].lower() or target_page == p["page_id"]]

    if limit:
        filtered_fleet = filtered_fleet[:limit]

    logger.info(f"Total Pages Queued in Run: {len(filtered_fleet)}")

    success_count = 0
    fail_count = 0

    for idx, p in enumerate(filtered_fleet):
        pid = p["page_id"]
        name = p["page_name"]
        vertical_key = p["assigned_vertical_key"]
        p_meta = pages_meta.get(pid, {})
        access_token = p_meta.get("access_token")

        slot_timing = InfographicScheduler.calculate_page_slot_time(idx, current_slot)

        # 1. Select unposted topic strictly from this vertical's authentic bank
        v_data = AUTHENTIC_VERTICAL_DATA.get(vertical_key, AUTHENTIC_VERTICAL_DATA["miniature_diorama_disaster"])
        topic_pool = v_data.get("topics", [])

        selected_topic = None
        for t in topic_pool:
            if not db.is_topic_angle_posted(pid, t["slug"], "v1"):
                selected_topic = t
                break

        # If all cycled, dynamic wrap around
        if not selected_topic:
            selected_topic = topic_pool[idx % len(topic_pool)]

        # 2. Render Full HD Graphic
        out_image_name = f"info_{pid}_{selected_topic['slug']}.png"
        out_image_path = os.path.join(BASE_DIR, "temp", "infographics", out_image_name)

        logger.info(f"[{idx+1}/{len(filtered_fleet)}] Page: {name} (ID: {pid}) | Slot Timing: {slot_timing['scheduled_time_utc']}")
        logger.info(f"  -> Vertical: {p['assigned_vertical_label']}")
        logger.info(f"  -> Selected Topic: {selected_topic['title']}")

        try:
            render_res = engine.render_infographic(
                page_name=name,
                vertical_key=vertical_key,
                topic=selected_topic,
                output_path=out_image_path
            )

            fb_id = None
            if dry_run:
                logger.info(f"  -> DRY RUN SUCCESS: Graphic rendered at {out_image_path}")
                status = "dry_run"
            else:
                if not access_token:
                    raise ValueError(f"Missing page access token for {name} ({pid})")
                fb_id = post_photo_to_facebook(
                    page_id=pid,
                    access_token=access_token,
                    image_path=out_image_path,
                    caption=render_res["caption"]
                )
                logger.info(f"  -> 🟢 PUBLISHED TO FACEBOOK! Photo ID: {fb_id}")
                status = "posted"

            db.record_upload(
                page_id=pid,
                vertical_key=vertical_key,
                topic_slug=selected_topic["slug"],
                angle_mode="v1",
                title=render_res["title"],
                hashtags=p["infographic_specs"]["target_hashtags"][0] if p["infographic_specs"]["target_hashtags"] else "#reels",
                image_path=out_image_path,
                fb_photo_id=fb_id,
                status=status,
                slot_index=current_slot
            )
            success_count += 1

        except Exception as e:
            logger.error(f"  -> ❌ FAILED for {name}: {e}")
            db.record_upload(
                page_id=pid,
                vertical_key=vertical_key,
                topic_slug=selected_topic["slug"] if selected_topic else "unknown",
                angle_mode="v1",
                title=selected_topic["title"] if selected_topic else "unknown",
                hashtags="#error",
                image_path=None,
                fb_photo_id=None,
                status="failed",
                slot_index=current_slot,
                error_message=str(e)
            )
            fail_count += 1

    logger.info("==================================================")
    logger.info(f"RUN COMPLETE: {success_count} Succeeded, {fail_count} Failed")
    logger.info("==================================================")
    return {"success": success_count, "failed": fail_count}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Infographic Pipeline Runner")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Simulate run without live Facebook POST")
    parser.add_argument("--live", action="store_true", help="Execute actual Facebook live POST")
    parser.add_argument("--page", type=str, default=None, help="Target page name or ID")
    parser.add_argument("--slot", type=int, default=None, help="Target slot index (0 to 5)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of pages")
    args = parser.parse_args()

    is_dry = not args.live
    run_pipeline(dry_run=is_dry, target_page=args.page, target_slot=args.slot, limit=args.limit)
