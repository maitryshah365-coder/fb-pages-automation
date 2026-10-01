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

def extract_sejal_pages():
    print("--> Launching Pixel 9 Pro to fetch Sejal Soni Pages from MBS Settings...")
    p, ctx, page = launch_android_browser(PIXEL9_NEWYORK_PROFILE, headless=True)

    try:
        page.goto("https://business.facebook.com/latest/settings/pages", wait_until="domcontentloaded", timeout=35000)
        time.sleep(8)
        print(f"URL: {page.url}")
        print(f"Title: {page.title()}")

        # Extract text and rows
        page_info = page.evaluate("""() => {
            const body = document.body.innerText;
            const rows = Array.from(document.querySelectorAll('div[role="row"]')).map(r => r.innerText.trim());
            // Also find all links
            const links = Array.from(document.querySelectorAll('a')).map(a => ({ text: a.innerText.trim(), href: a.href }));
            return { body: body.slice(0, 1500), rows: rows, links: links.slice(0, 50) };
        }""")

        print("\n--- BODY PREVIEW ---")
        print(page_info['body'])

        print(f"\n--- ROWS ({len(page_info['rows'])}) ---")
        for r in page_info['rows']:
            print("ROW:", r.replace('\n', ' | '))

        # Also let's check asset dropdown
        print("\n--> Checking asset switcher...")
        page.goto("https://business.facebook.com/latest/home", wait_until="domcontentloaded", timeout=25000)
        time.sleep(6)

        # Click on the business/page switcher in top left
        switcher = page.query_selector('div[role="button"]:has-text("Meta Business Suite"), div[role="button"]:has-text("Facebook"), div[role="button"][aria-haspopup="menu"]')
        if switcher:
            switcher.click()
            time.sleep(3)
            switcher_items = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('div[role="menuitem"], div[role="option"], div[role="button"]')).map(el => el.innerText.trim()).filter(t => t.length > 0 && t.length < 60);
            }""")
            print(f"Switcher items: {switcher_items[:30]}")

    finally:
        ctx.close()
        p.stop()

if __name__ == "__main__":
    extract_sejal_pages()
