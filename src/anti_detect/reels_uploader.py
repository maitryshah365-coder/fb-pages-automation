"""
Anti-Detect Mobile Reels Publishing Engine (Samsung Galaxy S25 New York)
Automates publishing Reels directly to Meta Business Suite without tokens or Graph API.
Uses humanized delays, natural typing jitter, and anti-bot evasions.
"""

import os
import sys
import time
import random
import sqlite3
from datetime import datetime, timezone
from typing import Optional, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.anti_detect.device_profiles import S25_NEWYORK_PROFILE
from src.anti_detect.browser_launcher import launch_android_browser
from src.anti_detect.session_manager import ProfileSessionManager

DB_PATH = os.path.join(BASE_DIR, "data", "posted_videos.db")


def human_type(element, text: str, min_delay_ms: int = 50, max_delay_ms: int = 120):
    """Types text with natural human keystroke speed variance."""
    for char in text:
        element.type(char, delay=random.randint(min_delay_ms, max_delay_ms))
        if char in (" ", "\n", ".", "#") and random.random() < 0.25:
            time.sleep(random.uniform(0.15, 0.45))


class AntiDetectReelsUploader:
    """Manages autonomous publishing of Facebook Reels via Meta Business Suite."""

    def __init__(self, profile=S25_NEWYORK_PROFILE, asset_id: str = "497577420112654"):
        self.profile = profile
        self.asset_id = str(asset_id) if asset_id else "497577420112654"
        self.session_mgr = ProfileSessionManager(profile.profile_id)
        if self.asset_id and self.asset_id.isdigit():
            self.composer_url = f"https://business.facebook.com/latest/reels_composer?asset_id={self.asset_id}"
        else:
            self.composer_url = "https://business.facebook.com/latest/reels_composer"

    def upload_reel(
        self,
        video_path: str,
        caption: str,
        page_name: str = "Apex House",
        asset_id: Optional[str] = None,
        headless: bool = True,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Publishes a single Reel video via the Samsung S25 New York browser profile.
        """
        if not os.path.exists(video_path):
            return {"status": "error", "message": f"Video file not found: {video_path}"}

        target_asset = str(asset_id) if asset_id else self.asset_id
        composer_url = f"https://business.facebook.com/latest/reels_composer?asset_id={target_asset}" if (target_asset and target_asset.isdigit()) else "https://business.facebook.com/latest/reels_composer"

        print(f"\n=======================================================")
        print(f"🎬 UPLOADING REEL VIA SAMSUNG GALAXY S25 (NEW YORK)")
        print(f"   Video:    {os.path.basename(video_path)}")
        print(f"   Page:     {page_name} (Asset ID: {target_asset})")
        print(f"   Caption:  {caption[:60]}...")
        print(f"   Dry Run:  {dry_run}")
        print(f"=======================================================")

        start_time = time.time()
        playwright, context, page = launch_android_browser(
            profile=self.profile,
            headless=headless,
            initial_url=composer_url
        )

        try:
            print("⏳ Loading Meta Business Suite Reels Composer...")
            page.wait_for_load_state("domcontentloaded", timeout=30000)
            time.sleep(random.uniform(4.0, 6.0))

            # 1. Attach Video File
            print("--> Locating file upload input...")
            # Look for file input or trigger Add Video
            file_input = page.query_selector('input[type="file"]')
            if not file_input:
                add_video_btn = page.query_selector('div[role="button"]:has-text("Add Video"), button:has-text("Add Video")')
                if add_video_btn:
                    print("--> Clicking 'Add Video' button...")
                    with page.expect_file_chooser() as fc_info:
                        add_video_btn.click()
                    file_chooser = fc_info.value
                    file_chooser.set_files(video_path)
                else:
                    return {"status": "error", "message": "Could not find 'Add Video' button on composer."}
            else:
                file_input.set_input_files(video_path)

            print("✅ Video file attached! Waiting for processing & thumbnail preview...")
            time.sleep(random.uniform(6.0, 9.0))

            # 2. Enter Caption / Description
            print("--> Adding caption with humanized keystrokes...")
            caption_box = page.query_selector('div[role="textbox"], textarea[placeholder*="Describe"], div[contenteditable="true"]')
            if caption_box:
                caption_box.click()
                time.sleep(random.uniform(0.5, 1.2))
                human_type(caption_box, caption)
                print("✅ Caption inserted successfully.")
            else:
                print("⚠️ Warning: Caption box not found; proceeding with video upload.")

            time.sleep(random.uniform(2.0, 3.5))

            # 3. Publish or Dry Run
            if dry_run:
                print("🔍 [DRY RUN] Video loaded and caption entered. Skipping final publish click.")
                return {"status": "success", "mode": "dry_run", "elapsed_s": round(time.time() - start_time, 2)}

            # Click Next / Share buttons
            print("--> Navigating through composer steps...")
            for step in range(2):
                next_btn = page.query_selector('div[role="button"]:has-text("Next"), button:has-text("Next")')
                if next_btn:
                    next_btn.click()
                    time.sleep(random.uniform(2.0, 3.5))

            # Click Publish / Share
            share_btn = page.query_selector('div[role="button"]:has-text("Publish"), button:has-text("Publish"), div[role="button"]:has-text("Share"), button:has-text("Share")')
            if share_btn:
                print(f"🚀 Clicking 'Publish' button for {page_name}...")
                share_btn.click()
                time.sleep(random.uniform(8.0, 12.0))
                print(f"🎉 REEL SUCCESSFULLY PUBLISHED TO {page_name.upper()}!")
                
                # Log into database
                self._record_in_db(video_path, page_name, "success")
                return {
                    "status": "success",
                    "page": page_name,
                    "video": os.path.basename(video_path),
                    "elapsed_s": round(time.time() - start_time, 2)
                }
            else:
                return {"status": "error", "message": "Could not locate 'Publish' or 'Share' button."}

        except Exception as e:
            print(f"❌ Error during upload: {e}")
            return {"status": "error", "message": str(e)}

        finally:
            context.close()
            playwright.stop()

    def _record_in_db(self, video_path: str, page_name: str, status: str):
        """Records upload in SQLite database."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            cur.execute("""
                INSERT INTO runs (page_id, run_id, started_at, finished_at, status, runner_ip, runner_city, runner_country)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (self.asset_id, f"s25_{int(time.time())}", now, now, status, "103.250.137.189", "New York (Spoofed)", "USA"))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"DB log warning: {e}")
