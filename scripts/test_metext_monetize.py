import sys
import os
import json
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

raw_cookies = json.load(open("C:/Users/Win/Desktop/Cookis/Meghal Chauhan (USA).txt", encoding="utf-8"))
playwright_cookies = []
for c in raw_cookies:
    if isinstance(c, dict) and "name" in c and "value" in c:
        pc = {
            "name": c["name"],
            "value": c["value"],
            "domain": c.get("domain", ".facebook.com"),
            "path": c.get("path", "/"),
            "secure": True
        }
        if "expirationDate" in c:
            pc["expires"] = float(c["expirationDate"])
        playwright_cookies.append(pc)

# Test Me Text (asset_id = 500794979779192)
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_cookies(playwright_cookies)
    page = ctx.new_page()
    url = "https://business.facebook.com/latest/monetization/monetization_home/monetization_home_main/?asset_id=500794979779192"
    print("Navigating to Me Text monetization:", url)
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(6)

    btn = page.locator('text="View Page Eligibility"').first
    if btn.count() > 0:
        print("Clicking View Page Eligibility button...")
        btn.click()
        time.sleep(4)

    page.screenshot(path="temp_metext_monetize.png")
    
    # Also extract text of all visible dialogs or cards
    for card in page.locator('div[role="dialog"], div[role="region"], div.x1n2onr6').all():
        try:
            t = card.inner_text()
            if any(k in t for k in ["Star", "Subscription", "Content Monetization", "In-Stream", "Set up"]):
                print("Found match in card:\n", t[:400])
                print("-" * 40)
        except:
            pass

    browser.close()
