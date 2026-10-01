import sys
import os
import json
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

def test_single_account(acc_id):
    ck_path = f"data/profiles/{acc_id}/cookies.json"
    if not os.path.exists(ck_path):
        print(f"No cookies for {acc_id}")
        return

    raw_cookies = json.load(open(ck_path, encoding="utf-8"))
    pw_cookies = []
    for c in raw_cookies:
        if isinstance(c, dict) and "name" in c and "value" in c:
            pc = {
                "name": str(c["name"]),
                "value": str(c["value"]),
                "domain": c.get("domain", ".facebook.com"),
                "path": c.get("path", "/"),
                "secure": True
            }
            if "expirationDate" in c:
                pc["expires"] = float(c["expirationDate"])
            pw_cookies.append(pc)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900}
        )
        ctx.add_cookies(pw_cookies)
        page = ctx.new_page()

        print(f"--> Navigating to Facebook home with {acc_id} cookies...")
        page.goto("https://www.facebook.com/", wait_until="domcontentloaded", timeout=25000)
        time.sleep(4)
        print(f"Current URL: {page.url}")

        if "login" in page.url.lower() or "checkpoint" in page.url.lower():
            print("❌ Session invalid / Checkpoint redirect!")
            browser.close()
            return

        print("✅ Session OK! Navigating to Meta Business Suite Home...")
        page.goto("https://business.facebook.com/latest/home", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        print(f"MBS URL: {page.url}")

        os.makedirs("temp/diagnostic", exist_ok=True)
        page.screenshot(path=f"temp/diagnostic/{acc_id}_mbs_home.png")
        print(f"Saved: temp/diagnostic/{acc_id}_mbs_home.png")

        browser.close()

if __name__ == "__main__":
    test_single_account("usa_account1_meghal")
