"""
Check Graph API Explorer for User Token
"""

import sys
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.anti_detect.device_profiles import S25_NEWYORK_PROFILE
from src.anti_detect.browser_launcher import launch_android_browser


def check_graph_explorer():
    p, ctx, page = launch_android_browser(S25_NEWYORK_PROFILE, headless=True)
    try:
        page.goto("https://developers.facebook.com/tools/explorer/?app_id=1113008228331576", wait_until="domcontentloaded", timeout=25000)
        time.sleep(5)
        print("Explorer URL:", page.url)
        print("Explorer Title:", page.title())

        # Grab token field if present
        tok = page.evaluate("""() => {
            const input = document.querySelector('input[aria-label*="Access Token"], input[placeholder*="Access Token"], input[value^="EAA"]');
            return input ? input.value : null;
        }""")
        print("Extracted Explorer Token:", tok[:30] + "..." if tok else "None found")
    finally:
        ctx.close()
        p.stop()


if __name__ == "__main__":
    check_graph_explorer()
