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
    page.goto('https://www.facebook.com/497577420112654', wait_until='domcontentloaded', timeout=25000)
    time.sleep(4)
    print('Page Title:', page.title())
    print('Final URL:', page.url)
    h1 = page.evaluate('() => document.querySelector("h1") ? document.querySelector("h1").innerText : "N/A"')
    print('Page Name (h1):', h1)

    # Let's also check all assets available in MBS by clicking the business asset dropdown or inspecting it
    page.goto('https://business.facebook.com/latest/home?asset_id=497577420112654', wait_until='domcontentloaded', timeout=25000)
    time.sleep(4)
    res = page.evaluate("""() => {
        // Look for the asset name in the top left
        const el = document.querySelector('div[role="banner"]');
        return el ? el.innerText : document.title;
    }""")
    print('MBS Banner Text:', res)
finally:
    ctx.close()
    p.stop()
