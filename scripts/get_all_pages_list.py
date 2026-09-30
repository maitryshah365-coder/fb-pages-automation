"""
Extract complete list of all 15 Pages from Meta Business Suite Settings
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


def extract_all_15_pages():
    print("=================================================================")
    print("📋 EXTRACTING ALL PAGES FROM META BUSINESS SUITE SETTINGS")
    print("=================================================================")

    p, ctx, page = launch_android_browser(S25_NEWYORK_PROFILE, headless=True)
    session_mgr = ProfileSessionManager(S25_NEWYORK_PROFILE.profile_id)

    try:
        page.goto("https://business.facebook.com/latest/settings/pages", wait_until="domcontentloaded", timeout=30000)
        time.sleep(6)

        # Scroll multiple times to trigger virtualized table loading of all 15 pages
        for _ in range(5):
            page.mouse.wheel(0, 800)
            time.sleep(1)

        # Extract all rows from the Pages table
        pages_found = page.evaluate("""() => {
            const results = [];
            // Rows in MBS settings table
            const rows = Array.from(document.querySelectorAll('div[role="row"], tr, div[role="listitem"]'));
            const seen = new Set();
            
            rows.forEach(r => {
                const text = r.innerText || '';
                const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                if (lines.length > 0) {
                    const firstLine = lines[0];
                    const ignore = ['Profiles', 'Name', 'Authorizations and verifications', 'Language settings', 'Search', 'Filter', 'Add pages'];
                    if (!ignore.includes(firstLine) && !seen.has(firstLine) && firstLine.length > 2) {
                        seen.add(firstLine);
                        // Look for any links or IDs
                        const link = r.querySelector('a');
                        const href = link ? link.href : '';
                        results.push({
                            name: firstLine,
                            all_lines: lines,
                            url: href
                        });
                    }
                }
            });

            // Also check all links on page with page IDs
            const allLinks = Array.from(document.querySelectorAll('a[href*="facebook.com/"], a[href*="asset_id="]'));
            allLinks.forEach(a => {
                const t = a.innerText ? a.innerText.trim() : '';
                if (t && t.length > 2 && !seen.has(t)) {
                    const ignore = ['Home', 'Notifications', 'Inbox', 'Planner', 'Content', 'Insights', 'Ads', 'Settings', 'All tools', 'Help'];
                    if (!ignore.includes(t) && !t.includes('\\n')) {
                        seen.add(t);
                        results.push({
                            name: t,
                            all_lines: [t],
                            url: a.href
                        });
                    }
                }
            });

            return results;
        }""")

        print(f"\n🎉 Extracted {len(pages_found)} Pages:")
        final_list = []
        for idx, p_info in enumerate(pages_found, 1):
            pname = p_info["name"]
            print(f"  #{idx:02d} {pname}")
            final_list.append({
                "index": idx,
                "name": pname,
                "url": p_info.get("url", "")
            })

        # Save to pages.json
        payload = {
            "account_user_id": "61570977560611",
            "total_pages": len(final_list),
            "pages": final_list
        }
        with open("data/profiles/samsung_s25_newyork/pages.json", "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print("\n✅ All pages saved to data/profiles/samsung_s25_newyork/pages.json")
        return final_list

    finally:
        ctx.close()
        p.stop()


if __name__ == "__main__":
    extract_all_15_pages()
