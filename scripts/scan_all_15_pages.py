"""
Deep Scan to Extract All 15 Pages from Facebook Account & Meta Business Suite
"""

import sys
import os
import time
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.anti_detect.device_profiles import S25_NEWYORK_PROFILE
from src.anti_detect.browser_launcher import launch_android_browser
from src.anti_detect.session_manager import ProfileSessionManager


def scan_all_pages():
    print("=================================================================")
    print("🔍 DEEP SCANNING ALL 15 PAGES IN FACEBOOK ACCOUNT")
    print("=================================================================")

    p, ctx, page = launch_android_browser(S25_NEWYORK_PROFILE, headless=True)
    session_mgr = ProfileSessionManager(S25_NEWYORK_PROFILE.profile_id)

    all_pages = []

    try:
        # Method 1: Meta Business Suite Home & Page Switcher Dropdown
        print("--> Step 1: Navigating to Meta Business Suite Home...")
        page.goto("https://business.facebook.com/latest/home", wait_until="domcontentloaded", timeout=30000)
        time.sleep(6)

        # Look for the asset switcher / dropdown button in MBS
        print("--> Looking for Asset Switcher in MBS...")
        # In MBS, the dropdown at top left usually has aria-haspopup or role="button" next to the current page name
        switcher_clicked = page.evaluate("""() => {
            // Find dropdown button near the page name in top left
            const buttons = Array.from(document.querySelectorAll('div[role="button"], button'));
            for (const b of buttons) {
                const text = b.innerText || '';
                if (text.includes('Apex House') || b.getAttribute('aria-haspopup') === 'menu' || b.getAttribute('aria-haspopup') === 'listbox' || b.getAttribute('aria-haspopup') === 'dialog') {
                    b.click();
                    return true;
                }
            }
            return false;
        }""")
        print(f"--> Switcher clicked: {switcher_clicked}")
        time.sleep(4)

        # Grab all list items or page elements in the open menu/dialog
        mbs_list = page.evaluate("""() => {
            const items = [];
            // Look for dialog, menu, listbox, or popover
            const els = Array.from(document.querySelectorAll('div[role="dialog"] div[role="button"], div[role="menu"] div[role="menuitem"], div[role="listbox"] div[role="option"], ul li, div[data-testid*="asset"]'));
            els.forEach(el => {
                const text = el.innerText ? el.innerText.trim() : '';
                if (text && text.length > 2 && text.length < 50 && !text.includes('Search') && !text.includes('Business Account') && !text.includes('Settings')) {
                    items.push(text);
                }
            });
            return Array.from(new Set(items));
        }""")
        print(f"--> MBS Dropdown items found: {len(mbs_list)}")
        if mbs_list:
            print("Items:", mbs_list[:15])

        # Method 2: Meta Business Suite Settings -> Pages
        print("\n--> Step 2: Navigating to Meta Business Suite Pages Settings...")
        page.goto("https://business.facebook.com/latest/settings/pages", wait_until="domcontentloaded", timeout=30000)
        time.sleep(6)

        pages_settings = page.evaluate("""() => {
            const found = [];
            // Look for table rows or list items in Pages settings
            const rows = Array.from(document.querySelectorAll('div[role="row"], div[role="listitem"], a[href*="/pages/"], tr'));
            rows.forEach(r => {
                const t = r.innerText ? r.innerText.trim() : '';
                if (t && t.length > 2) {
                    found.push(t);
                }
            });
            return found;
        }""")
        print(f"--> Settings Pages items: {len(pages_settings)}")
        if pages_settings:
            for s in pages_settings[:15]:
                print("   •", s.split('\n')[0])

        # Method 3: Facebook Desktop Pages URL
        print("\n--> Step 3: Navigating to https://www.facebook.com/pages/?category=your_pages...")
        page.goto("https://www.facebook.com/pages/?category=your_pages", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)

        fb_pages = page.evaluate("""() => {
            const results = [];
            const links = Array.from(document.querySelectorAll('a[href*="facebook.com/"], a[role="link"]'));
            const seen = new Set();
            links.forEach(a => {
                const text = a.innerText ? a.innerText.trim() : '';
                const href = a.href || '';
                if (text && text.length > 2 && text.length < 50) {
                    if (!['Home', 'Watch', 'Marketplace', 'Groups', 'Gaming', 'Facebook', 'See all', 'Create new page', 'Pages'].includes(text)) {
                        if (!seen.has(text) && !text.includes('\n')) {
                            seen.add(text);
                            results.push({ name: text, url: href });
                        }
                    }
                }
            });
            return results;
        }""")
        print(f"--> Facebook Your Pages found: {len(fb_pages)}")
        for p_item in fb_pages:
            print(f"   • {p_item['name']} ({p_item['url']})")

        # Method 4: Bookmarks / Shortcuts menu
        print("\n--> Step 4: Navigating to https://www.facebook.com/bookmarks/pages...")
        page.goto("https://www.facebook.com/bookmarks/pages", wait_until="domcontentloaded", timeout=25000)
        time.sleep(4)
        b_pages = page.evaluate("""() => {
            const list = [];
            const els = Array.from(document.querySelectorAll('span, a'));
            const seen = new Set();
            els.forEach(el => {
                const t = el.innerText ? el.innerText.trim() : '';
                if (t && t.length > 2 && t.length < 40 && !seen.has(t) && !t.includes('\n')) {
                    if (!['Pages', 'Home', 'Create', 'Notifications', 'Messages', 'Settings', 'Log Out'].includes(t)) {
                        seen.add(t);
                        list.push(t);
                    }
                }
            });
            return list;
        }""")
        print(f"--> Bookmark items: {len(b_pages)}")

    finally:
        ctx.close()
        p.stop()


if __name__ == "__main__":
    scan_all_pages()
