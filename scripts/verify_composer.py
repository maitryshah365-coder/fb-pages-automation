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
    print("Navigating to Meta Business Suite Reels Composer...")
    page.goto('https://business.facebook.com/latest/reels_composer', wait_until='domcontentloaded', timeout=30000)
    time.sleep(5)
    print("Reels Composer URL:", page.url)
    print("Reels Composer Title:", page.title())

    # Look for file upload button or add video input
    file_input = page.query_selector('input[type="file"]')
    print("File Upload Input Present:", file_input is not None)

    # Grab visible texts on the composer screen
    texts = page.evaluate("""() => {
        const buttons = Array.from(document.querySelectorAll('button, div[role="button"]'));
        return buttons.map(b => b.innerText.trim()).filter(t => t.length > 0 && t.length < 40).slice(0, 10);
    }""")
    print("Composer Actions/Buttons:", texts)
finally:
    ctx.close()
    p.stop()
