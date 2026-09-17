import os
from playwright.sync_api import sync_playwright

def verify_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # 1. Desktop Viewport
        page_desktop = browser.new_page(viewport={"width": 1280, "height": 900})
        page_desktop.goto("http://localhost:8888")
        page_desktop.wait_for_timeout(2000)
        page_desktop.screenshot(path="scratch/raj_pro_desktop.png", full_page=True)
        print("Desktop screenshot captured.")

        # 2. Mobile Viewport (iPhone 14)
        page_mobile = browser.new_page(viewport={"width": 390, "height": 844})
        page_mobile.goto("http://localhost:8888")
        page_mobile.wait_for_timeout(2000)
        page_mobile.screenshot(path="scratch/raj_pro_mobile_main.png", full_page=True)
        print("Mobile main screenshot captured.")

        # 3. Test opening Drawer on Mobile
        page_mobile.click("#btnOpenPageDrawer")
        page_mobile.wait_for_timeout(1000)
        page_mobile.screenshot(path="scratch/raj_pro_mobile_drawer.png")
        print("Mobile drawer screenshot captured.")

        browser.close()

if __name__ == "__main__":
    verify_app()
