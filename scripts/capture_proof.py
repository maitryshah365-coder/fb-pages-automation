import time
import os
from playwright.sync_api import sync_playwright

doc_path = os.path.abspath("docs/index.html")
file_url = f"file:///{doc_path.replace(os.sep, '/')}"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    print("Navigating to:", file_url)
    page.goto(file_url, wait_until="load", timeout=15000)
    time.sleep(3)
    page.screenshot(path="temp_verified_dashboard.png")

    # Switch to Monetization Hub
    btn = page.locator('text="Monetization Hub"').first
    if btn.count() > 0:
        btn.click()
        time.sleep(2)
        page.screenshot(path="temp_verified_monetization_hub.png")

    browser.close()

print("Screenshots captured successfully!")
