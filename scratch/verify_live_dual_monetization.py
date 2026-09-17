import os
import time
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\Win\.gemini\antigravity-ide\brain\313a3f26-ac39-434f-8050-53be5bd48383"

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 1100})

        url = "https://maitryshah365-coder.github.io/fb-pages-automation/"
        print(f"Navigating to {url} ...")
        page.goto(url, timeout=30000)
        page.wait_for_selector("#boxMonetizationHub", timeout=15000)
        page.wait_for_timeout(1500)

        # 1. Click Lopez Edward
        print("Clicking Lopez Edward on Live Site...")
        lopez = page.locator(".page-list-item:has-text('Lopez')").first
        lopez.click()
        page.wait_for_timeout(1000)

        page.locator("#boxMonetizationHub").scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "live_gh_lopez_invite_monetize.png"))
        print("Captured live_gh_lopez_invite_monetize.png")

        # 2. Click Option 1 on Lopez
        print("Toggling Option 1 on Lopez...")
        page.locator("#btnTabCriteria").click()
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "live_gh_lopez_criteria_tab.png"))
        print("Captured live_gh_lopez_criteria_tab.png")

        # 3. Click Fresh Hive Network or Me Text
        print("Clicking Fresh Hive Network on Live Site...")
        fh = page.locator(".page-list-item:has-text('Fresh Hive')").first
        if fh.count() > 0:
            fh.click()
        else:
            page.locator(".page-list-item:has-text('Me Text')").first.click()
        page.wait_for_timeout(1000)

        page.locator("#boxMonetizationHub").scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "live_gh_criteria_auto_monetize.png"))
        print("Captured live_gh_criteria_auto_monetize.png")

        browser.close()
        print("Live GitHub Pages verification completed successfully!")

if __name__ == "__main__":
    run_test()
