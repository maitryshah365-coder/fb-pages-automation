import sys
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.anti_detect.device_profiles import S25_NEWYORK_PROFILE
from src.anti_detect.browser_launcher import launch_android_browser

p, ctx, page = launch_android_browser(S25_NEWYORK_PROFILE, headless=True)
try:
    page.goto('https://business.facebook.com/latest/reels_composer?asset_id=497577420112654', wait_until='domcontentloaded', timeout=30000)
    time.sleep(5)

    # Let's inspect the page name displayed next to the profile picture
    names = page.evaluate("""() => {
        const els = Array.from(document.querySelectorAll('span, div, h2, h3'));
        const matches = [];
        els.forEach(el => {
            const t = el.innerText ? el.innerText.trim() : '';
            if (t && t.length > 2 && t.length < 35) {
                // If it looks like a page name
                if (!['OPEN', 'Create', 'Edit', 'Share', 'Add Video', 'Add Photos', 'Meta Business Suite', 'Facebook', 'Home'].includes(t)) {
                    matches.push(t);
                }
            }
        });
        return Array.from(new Set(matches)).slice(0, 15);
    }""")
    print("Found potential Page/Profile names:", names)
finally:
    ctx.close()
    p.stop()
