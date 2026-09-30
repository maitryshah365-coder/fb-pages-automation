"""
Check existing Meta Developer Apps on developers.facebook.com
"""

import sys
import os
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


def check_meta_apps():
    p, ctx, page = launch_android_browser(S25_NEWYORK_PROFILE, headless=True)
    try:
        page.goto("https://developers.facebook.com/apps/", wait_until="domcontentloaded", timeout=25000)
        time.sleep(5)
        print("Developers URL:", page.url)
        print("Developers Title:", page.title())

        # Grab app cards or text on developers page
        res = page.evaluate("""() => {
            const cards = Array.from(document.querySelectorAll('a[href*="/apps/"], div[role="button"], span'));
            const appLinks = cards.map(c => ({ text: c.innerText.trim(), href: c.href || '' })).filter(c => c.text.length > 2 && c.text.length < 50);
            return appLinks.slice(0, 20);
        }""")
        print("Developers page elements:", res)
    finally:
        ctx.close()
        p.stop()


if __name__ == "__main__":
    check_meta_apps()
