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

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_cookies(playwright_cookies)
    page = ctx.new_page()
    page.goto("https://business.facebook.com/latest/monetization/monetization_home/monetization_home_main/?asset_id=626061003919674", wait_until="domcontentloaded", timeout=30000)
    time.sleep(6)

    # Click View Page Eligibility
    btn = page.locator('text="View Page Eligibility"').first
    if btn.count() > 0:
        print("Clicking View Page Eligibility button...")
        btn.click()
        time.sleep(4)

        dialog = page.locator('div[role="dialog"]')
        if dialog.count() > 0:
            d_text = dialog.first.inner_text()
            print("--- MODAL DIALOG TEXT ---")
            print(d_text)
        else:
            print("No dialog found, checking page text...")
    else:
        print("Button View Page Eligibility not found!")

    page.screenshot(path="temp_eligibility_dialog.png")
    browser.close()
