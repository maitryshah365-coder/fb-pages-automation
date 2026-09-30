"""
Auto-Discover Pages and Profile Information from Authenticated Samsung S25 Session
"""

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

from src.anti_detect.device_profiles import S25_NEWYORK_PROFILE
from src.anti_detect.browser_launcher import launch_android_browser
from src.anti_detect.session_manager import ProfileSessionManager


def discover_account_and_pages():
    profile = S25_NEWYORK_PROFILE
    session_mgr = ProfileSessionManager(profile.profile_id)

    print("=================================================================")
    print("🔍 DISCOVERING ACCOUNT DETAILS & PAGES (SAMSUNG S25 NY SESSION)")
    print("=================================================================")

    playwright, context, page = launch_android_browser(
        profile=profile,
        headless=True
    )

    try:
        # 1. Fetch user's own profile page
        print("--> Navigating to user profile...")
        page.goto("https://m.facebook.com/profile.php", wait_until="domcontentloaded", timeout=25000)
        time.sleep(3)

        title = page.title()
        print(f"--> Profile Page Title: {title}")

        # Try to extract the user's name from profile
        user_name = page.evaluate("""() => {
            const h1 = document.querySelector('h1');
            if (h1 && h1.innerText.trim()) return h1.innerText.trim();
            const strong = document.querySelector('strong');
            if (strong && strong.innerText.trim()) return strong.innerText.trim();
            return document.title.replace(' | Facebook', '').trim();
        }""")
        print(f"--> Account Name: {user_name}")

        # 2. Navigate to Pages section
        print("--> Navigating to https://m.facebook.com/pages/...")
        page.goto("https://m.facebook.com/pages/", wait_until="domcontentloaded", timeout=25000)
        time.sleep(4)

        # Extract page listings
        pages_data = page.evaluate("""() => {
            const results = [];
            // Look for links that link to pages or have aria-labels or strong text
            const links = Array.from(document.querySelectorAll('a'));
            const seen = new Set();
            links.forEach(a => {
                const href = a.href || '';
                const text = a.innerText.trim();
                // Check if it's a page link
                if (href && text && text.length > 1 && text.length < 50) {
                    if ((href.includes('/pages/') || href.includes('facebook.com/') && !href.includes('/friends') && !href.includes('/groups') && !href.includes('/watch') && !href.includes('/notifications') && !href.includes('/messages') && !href.includes('/settings') && !href.includes('/help') && !href.includes('/menu')) && !seen.has(text)) {
                        // Avoid standard UI words
                        const skip = ['Create', 'Discover', 'Liked Pages', 'Invitations', 'Pages', 'Home', 'Menu', 'Log Out', 'Facebook', 'See More', 'Switch', 'Edit'];
                        if (!skip.includes(text) && !text.includes('notification') && !text.includes('Invite')) {
                            seen.add(text);
                            results.push({ name: text, url: href });
                        }
                    }
                }
            });
            return results;
        }""")

        print(f"--> Found {len(pages_data)} candidate page elements:")
        for p in pages_data:
            print(f"    • {p['name']} ({p['url']})")

        # 3. Check Meta Business Suite or professional dashboard
        print("\n--> Checking Meta Business Suite accounts...")
        page.goto("https://business.facebook.com/latest/home", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)

        mbs_url = page.url
        print(f"--> Meta Business Suite URL: {mbs_url}")

        mbs_pages = page.evaluate("""() => {
            const list = [];
            // Look for page selector or business names
            const buttons = Array.from(document.querySelectorAll('div[role="button"], span, div'));
            // Search local storage or window data if accessible
            return {
                url: window.location.href,
                title: document.title
            };
        }""")
        print(f"--> Meta Business Suite Title: {mbs_pages.get('title')}")

        # Update metadata
        meta = session_mgr.load_metadata()
        meta["user_name"] = user_name
        meta["pages_found"] = pages_data
        session_mgr.save_metadata(meta)
        session_mgr.save_pages(pages_data)

        print("\n🎉 Discovery completed and saved into profile sandbox!")
        return user_name, pages_data

    finally:
        context.close()
        playwright.stop()


if __name__ == "__main__":
    discover_account_and_pages()
