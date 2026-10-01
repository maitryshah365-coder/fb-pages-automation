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

    # Navigate to Facebook Professional Dashboard
    print("Navigating to Facebook Professional Dashboard...")
    page.goto("https://www.facebook.com/professional_dashboard/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(6)
    print("URL:", page.url)
    page.screenshot(path="temp_fb_pro_dash.png")

    # Navigate to Monetization tools tab
    print("Navigating to Professional Dashboard Monetization...")
    page.goto("https://www.facebook.com/professional_dashboard/monetization", wait_until="domcontentloaded", timeout=30000)
    time.sleep(6)
    print("Monetization URL:", page.url)
    page.screenshot(path="temp_fb_pro_monetize.png")

    body = page.inner_text("body")
    print("Monetization page text preview:")
    for line in body.split("\n"):
        if any(w in line.lower() for w in ["star", "bonus", "stream", "subscription", "earn", "eligible", "payout", "tool"]):
            print("  ->", line.strip())

    browser.close()
