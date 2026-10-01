import sys
import os
import time
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.anti_detect.device_profiles import PIXEL9_NEWYORK_PROFILE
from src.anti_detect.browser_launcher import launch_android_browser

def extract_ids():
    p, ctx, page = launch_android_browser(PIXEL9_NEWYORK_PROFILE, headless=True)

    try:
        page.goto("https://business.facebook.com/latest/settings/profiles?asset_id=340559612467800", wait_until="domcontentloaded", timeout=35000)
        time.sleep(8)

        # Let's inspect all clickable page rows or links inside the table
        page_map = page.evaluate("""() => {
            const results = {};
            // Look for all elements that contain page names
            const elements = Array.from(document.querySelectorAll('*'));
            for (const el of elements) {
                const text = el.innerText ? el.innerText.trim() : '';
                // If element has an aria-label or role='row' or role='button'
                const parent = el.closest('div[role="row"], div[role="button"], tr, li');
                if (parent) {
                    const html = parent.outerHTML;
                    // search for 15-16 digit numbers or asset_id or id
                    const idMatches = html.match(/(\\d{14,17})/g);
                    if (idMatches && text && text.length < 40) {
                        results[text] = idMatches;
                    }
                }
            }
            return results;
        }""")

        print("Extracted page map candidates:")
        for k, v in page_map.items():
            if any(name in k for name in ["Daily Spark", "Chill Spot", "Tag", "Stellar", "Sovereign", "Silent Grove", "Vanguard", "Frontier", "Rajat", "Mouth", "Mojo", "Fly Happy", "Flute", "Faro", "Cosmic"]):
                print(f"  {k} -> {set(v)}")

        # Also let's click on each row to inspect right panel
        rows = page.query_selector_all('div[role="row"], div:has-text("Facebook Page")')
        print(f"\nTotal div rows with Facebook Page: {len(rows)}")

        page_ids = {}
        target_names = [
            "The Daily Spark", "The Chill Spot", "Tag The", "Stellar Vibes", "Sovereign Collective",
            "Silent Grove", "Royal Vanguard", "Royal Frontier", "Rajat Gupta", "Mouth The Hang",
            "Mojo Day", "Fly Happy", "Flute Tomography Nature", "Faro Fact", "Cosmic Mirage"
        ]

        for name in target_names:
            el = page.query_selector(f'text="{name}"')
            if el:
                el.click()
                time.sleep(1.5)
                # Check URL or right panel text
                pane_text = page.evaluate("""() => {
                    const match = document.body.innerText.match(/ID[:\\s]+(\\d{14,17})/i) || document.body.innerText.match(/(\\d{14,17})/);
                    return match ? match[1] : null;
                }""")
                print(f"Clicked '{name}' -> Detected ID: {pane_text}")
                if pane_text:
                    page_ids[name] = pane_text

        print("\nFinal Mapped IDs:", page_ids)

    finally:
        ctx.close()
        p.stop()

if __name__ == "__main__":
    extract_ids()
