import sys
import os
import json
import time

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
from src.anti_detect.session_manager import ProfileSessionManager

def discover_sejal_pages():
    print("=================================================================")
    print("🔍 DISCOVERING SEJAL SONI PAGES VIA PIXEL 9 PRO NEW YORK")
    print("=================================================================")

    playwright, context, page = launch_android_browser(
        profile=PIXEL9_NEWYORK_PROFILE,
        headless=True,
        initial_url="https://business.facebook.com/latest/home"
    )

    try:
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        time.sleep(5)

        print(f"Loaded URL: {page.url}")
        print(f"Page Title: {page.title()}")

        if "login" in page.url.lower():
            print("❌ Redirected to login! Checking why cookies didn't authenticate.")
            return

        # Navigate to Pages list on mobile Facebook
        print("\n--> Navigating to https://m.facebook.com/pages/...")
        page.goto("https://m.facebook.com/pages/", wait_until="domcontentloaded", timeout=25000)
        time.sleep(4)

        pages_found = page.evaluate("""() => {
            const list = [];
            const links = Array.from(document.querySelectorAll('a'));
            const seen = new Set();
            links.forEach(a => {
                const text = a.innerText.trim();
                const href = a.href || '';
                if (text && text.length > 2 && text.length < 50) {
                    const skip = ['Create', 'Discover', 'Liked Pages', 'Invitations', 'Pages', 'Home', 'Menu', 'Log Out', 'Facebook', 'See More', 'Switch', 'Edit', 'Invite', 'Notifications'];
                    if (!skip.includes(text) && !text.includes('notification') && !seen.has(text)) {
                        seen.add(text);
                        list.push({ name: text, url: href });
                    }
                }
            });
            return list;
        }""")

        print(f"Found {len(pages_found)} items from m.facebook.com/pages/:")
        for p in pages_found:
            print(f"  • {p['name']} -> {p['url']}")

        # Also check Meta Business Suite switcher
        print("\n--> Checking Meta Business Suite assets / switcher...")
        page.goto("https://business.facebook.com/latest/home", wait_until="domcontentloaded", timeout=25000)
        time.sleep(6)

        mbs_assets = page.evaluate("""() => {
            const results = [];
            // Look for any asset-id in HTML
            const html = document.body.innerHTML;
            const matches = html.matchAll(/asset_id=(\\d+)/g);
            for (const m of matches) {
                results.push(m[1]);
            }
            return Array.from(new Set(results));
        }""")
        print(f"Found asset IDs in MBS HTML: {mbs_assets}")

        # Check drive subfolders to match
        drive_file = os.path.join(BASE_DIR, "data", "sejal_soni_drive_folders.json")
        if os.path.exists(drive_file):
            with open(drive_file, "r", encoding="utf-8") as df:
                drive_folders = json.load(df)
            print(f"\nMatching against {len(drive_folders)} Drive Folders:")
            for folder_name in drive_folders:
                print(f"  Drive: {folder_name}")

    finally:
        context.close()
        playwright.stop()

if __name__ == "__main__":
    discover_sejal_pages()
