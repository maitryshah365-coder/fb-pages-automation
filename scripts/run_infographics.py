import os
import sys
import json
import time
import argparse
import logging
import requests
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.infographic_db import InfographicDB
from src.infographic_engine import InfographicEngine, AUTHENTIC_VERTICAL_DATA, TEMPLATE_STYLES, PALETTE_THEMES, ART_STYLE_KEYS
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

        # 2. Dynamic Rotation Plan (Rotates Layout Template, Color Theme & Art Style on every single run)
        plan = db.get_next_rotation_plan(
            page_id=pid,
            topic_pool=topic_pool,
            template_pool=TEMPLATE_STYLES,
            theme_pool=list(PALETTE_THEMES.keys()),
            art_style_pool=ART_STYLE_KEYS
        )
        selected_topic = plan["topic"]
        selected_template = plan["template"]
        selected_theme = plan["theme"]
        selected_art = plan.get("art_style", "pixar_3d")
        angle_mode = plan["angle_mode"]

        # 3. Render Full HD Graphic
        out_image_name = f"info_{pid}_{selected_topic['slug']}_{selected_template}_{selected_art}.png"
        out_image_path = os.path.join(BASE_DIR, "temp", "infographics", out_image_name)

        logger.info(f"[{idx+1}/{len(filtered_fleet)}] Page: {name} (ID: {pid}) | Slot Timing: {slot_timing['scheduled_time_utc']}")
        logger.info(f"  -> Vertical: {p['assigned_vertical_label']}")
        logger.info(f"  -> Template: [{selected_template}] | Theme: [{selected_theme}] | Art: [{selected_art}]")
        logger.info(f"  -> Selected Topic: {selected_topic['title']}")

        try:
            render_res = engine.render_infographic(
                page_name=name,
                vertical_key=vertical_key,
                topic=selected_topic,
                output_path=out_image_path,
                template_name=selected_template,
                theme_name=selected_theme,
                art_style_name=selected_art,
                target_hashtags=p.get("infographic_specs", {}).get("target_hashtags", [])
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
                angle_mode=angle_mode,
                title=render_res["title"],
                hashtags=render_res.get("hashtags", ""),
                image_path=out_image_path,
                fb_photo_id=fb_id,
                status=status,
                slot_index=current_slot
            )
            success_count += 1
            if not dry_run:
                time.sleep(2.0)

        except Exception as e:
            logger.error(f"  -> 🔴 FAILED for {name}: {e}")
            db.record_upload(
                page_id=pid,
                vertical_key=vertical_key,
                topic_slug=selected_topic["slug"],
                angle_mode=angle_mode,
                title=selected_topic["title"],
                hashtags="",
                image_path=None,
                fb_photo_id=None,
                status="failed",
                slot_index=current_slot,
                error_message=str(e)
            )
            fail_count += 1

    logger.info(f"=== INFOGRAPHIC PIPELINE COMPLETE: {success_count} Succeeded, {fail_count} Failed ===")
    return {"success": success_count, "failed": fail_count}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Facebook Infographics Pipeline Runner")
    parser.add_argument("--live", action="store_true", help="Publish directly to Facebook Graph API")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Render images only, do not publish to Facebook")
    parser.add_argument("--page", type=str, default=None, help="Specific page name or ID to run")
    parser.add_argument("--slot", type=int, default=None, help="Target slot index (0 to 5)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of pages to process")

    args = parser.parse_args()
    is_dry_run = not args.live or args.dry_run

    run_pipeline(
        dry_run=is_dry_run,
        target_page=args.page,
        target_slot=args.slot,
        limit=args.limit
    )
