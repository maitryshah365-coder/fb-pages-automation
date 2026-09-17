import os
import sys
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = r"C:\Users\Win\.gemini\antigravity-ide\brain\313a3f26-ac39-434f-8050-53be5bd48383"

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 1100})

        print("Navigating to local dashboard...")
        page.goto("http://127.0.0.1:8888", timeout=15000)
        page.wait_for_selector("#boxMonetizationHub")
        page.wait_for_timeout(1000)

        # 1. Capture Initial State (Portfolio)
        page.locator("#boxMonetizationHub").scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "monetize_portfolio_view.png"))
        print("Captured monetize_portfolio_view.png")

        # 2. Select Lopez Edward (Invite-Only Page)
        print("Clicking Lopez Edward...")
        lopez_btn = page.locator(".page-list-item:has-text('Lopez')").first
        lopez_btn.click()
        page.wait_for_timeout(800)

        # Scroll to monetization hub
        page.locator("#boxMonetizationHub").scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "lopez_invite_auto_view.png"))
        print("Captured lopez_invite_auto_view.png (Auto-detected Invite-Only)")

        # 3. On Lopez Edward, click Option 1: Criteria Area Page tab to switch view
        print("Switching to Option 1: Criteria Area on Lopez...")
        btn_crit = page.locator("#btnTabCriteria")
        btn_crit.click()
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "lopez_criteria_tab_view.png"))
        print("Captured lopez_criteria_tab_view.png")

        # 4. Select Fresh Hive Network (Criteria Page matching user's Screenshot 1)
        print("Clicking Fresh Hive Network...")
        fresh_hive_btn = page.locator(".page-list-item:has-text('Fresh Hive')").first
        if fresh_hive_btn.count() > 0:
            fresh_hive_btn.click()
        else:
            # Fallback to Me Text
            page.locator(".page-list-item:has-text('Me Text')").first.click()
        page.wait_for_timeout(800)

        page.locator("#boxMonetizationHub").scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "criteria_page_auto_view.png"))
        print("Captured criteria_page_auto_view.png (Auto-detected Criteria Area Page)")

        # 5. Click Notify Me button
        print("Testing Notify Me button...")
        notify_btn = page.locator("#btnNotifyCriteria")
        notify_btn.click()
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "criteria_notify_active_view.png"))
        print("Captured criteria_notify_active_view.png")

        # 6. Mobile Viewport Test (iPhone 14 Pro Max 430x932)
        print("Testing Mobile View...")
        page.set_viewport_size({"width": 430, "height": 932})
        page.wait_for_timeout(500)
        page.locator("#boxMonetizationHub").scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(ARTIFACT_DIR, "mobile_monetize_dual_view.png"))
        print("Captured mobile_monetize_dual_view.png")

        browser.close()
        print("All tests completed successfully!")

if __name__ == "__main__":
    run_test()
