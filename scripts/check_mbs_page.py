"""
Extract Page Name and Assets from Meta Business Suite
"""

import sys
import os
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.anti_detect.device_profiles import S25_NEWYORK_PROFILE
from src.anti_detect.browser_launcher import launch_android_browser
from src.anti_detect.session_manager import ProfileSessionManager


def extract_mbs_details():
    profile = S25_NEWYORK_PROFILE
    session_mgr = ProfileSessionManager(profile.profile_id)

    playwright, context, page = launch_android_browser(
        profile=profile,
        headless=True,
        initial_url="https://business.facebook.com/latest/home?asset_id=497577420112654"
    )

    try:
        page.wait_for_load_state("networkidle", timeout=20000)
        time.sleep(5)

        # Extract title and any page name from header or selector
        data = page.evaluate("""() => {
            const pageNameEl = document.querySelector('div[role="banner"] span, h1, div[data-testid="page_name"]');
            const spans = Array.from(document.querySelectorAll('span, div, h2, h3'));
            let possibleNames = [];
            spans.forEach(s => {
                const t = s.innerText ? s.innerText.trim() : '';
                if (t && t.length > 2 && t.length < 40 && !t.includes('Meta') && !t.includes('Business') && !t.includes('Home') && !t.includes('Notifications') && !t.includes('Inbox') && !t.includes('Posts') && !t.includes('Reels') && !t.includes('Insights') && !t.includes('Settings')) {
                    possibleNames.push(t);
                }
            });

            // Get all buttons or links that might show page name
            const assetButtons = Array.from(document.querySelectorAll('div[role="button"]'));
            const buttonTexts = assetButtons.map(b => b.innerText.trim()).filter(t => t.length > 0 && t.length < 50);

            return {
                title: document.title,
                url: window.location.href,
                possibleNames: possibleNames.slice(0, 15),
                buttonTexts: buttonTexts.slice(0, 15)
            };
        }""")

        print(f"MBS Title: {data['title']}")
        print(f"Current URL: {data['url']}")
        print(f"Button Texts: {data['buttonTexts']}")
        print(f"Possible Names: {data['possibleNames']}")

        # Also let's query Graph API directly with the cookies to see if we can get the page name for 497577420112654
        cookies = context.cookies()
        c_user = next((c['value'] for c in cookies if c['name'] == 'c_user'), None)
        xs = next((c['value'] for c in cookies if c['name'] == 'xs'), None)
        print(f"c_user: {c_user}, xs present: {bool(xs)}")

    finally:
        context.close()
        playwright.stop()


if __name__ == "__main__":
    extract_mbs_details()
