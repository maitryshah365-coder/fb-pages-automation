import json
import time
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

raw_cookies = json.load(open("data/profiles/samsung_s25_newyork/cookies.json", encoding="utf-8"))
playwright_cookies = []
for c in raw_cookies:
    pc = {
        "name": c["name"],
        "value": c["value"],
        "domain": c.get("domain", ".facebook.com"),
        "path": c.get("path", "/"),
        "secure": c.get("secure", True),
        "httpOnly": c.get("httpOnly", False)
    }
    if "expirationDate" in c:
        pc["expires"] = float(c["expirationDate"])
    elif "expires" in c:
        pc["expires"] = float(c["expires"])

    ss = str(c.get("sameSite", "")).lower()
    if ss in ("no_restriction", "none"):
        pc["sameSite"] = "None"
    elif ss == "lax":
        pc["sameSite"] = "Lax"
    elif ss == "strict":
        pc["sameSite"] = "Strict"

    playwright_cookies.append(pc)

os.makedirs("temp/audit_debug", exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 800}
    )
    context.add_cookies(playwright_cookies)
    page = context.new_page()

    # 1. Test Meta Business Suite Home & Monetization
    urls_to_test = [
        ("fb_home", "https://www.facebook.com/"),
        ("mbs_home", "https://business.facebook.com/latest/home"),
        ("mbs_monetization", "https://business.facebook.com/latest/monetization"),
        ("apex_page_quality", "https://www.facebook.com/497577420112654/settings/?tab=page_quality"),
        ("apex_prof_dashboard", "https://www.facebook.com/professional_dashboard/overview/")
    ]

    for label, url in urls_to_test:
        print(f"\n--- Testing: {label} ({url}) ---")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            time.sleep(3)
            final_url = page.url
            title = page.title()
            print(f"  Title: {title}")
            print(f"  Final URL: {final_url}")
            shot_path = f"temp/audit_debug/{label}.png"
            page.screenshot(path=shot_path)
            print(f"  Screenshot: {shot_path}")

            # Check for key keywords
            text = page.inner_text("body")
            lower_text = text.lower()
            indicators = []
            if "monetization" in lower_text: indicators.append("Monetization Mentioned")
            if "policy issues" in lower_text or "policy" in lower_text: indicators.append("Policy Mentioned")
            if "in-stream" in lower_text: indicators.append("In-Stream Ads")
            if "stars" in lower_text: indicators.append("Stars")
            if "log in" in lower_text and "password" in lower_text: indicators.append("⚠️ Login Screen Prompt")
            if "apex house" in lower_text: indicators.append("Apex House Found")
            print(f"  Signals: {', '.join(indicators) if indicators else 'No specific signals'}")
        except Exception as e:
            print(f"  Error: {e}")

    browser.close()
