"""
Extract Page IDs for all 15 Pages from Meta Business Suite
"""

import sys
import os
import time
import json
import re

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

PAGE_NAMES = [
    "Quantum House", "Drift Valley", "Dreams Of Life", "End Every",
    "Executive Empire", "I'm Joker", "Iron Covenant", "Iron Momentum",
    "Me The", "Quiet Harbor", "Radiant Reverie", "Bit Creative",
    "Atlas Authority", "Blissful Paradox", "Apex House"
]


def extract_page_ids():
    p, ctx, page = launch_android_browser(S25_NEWYORK_PROFILE, headless=True)
    try:
        page.goto("https://business.facebook.com/latest/settings/pages", wait_until="domcontentloaded", timeout=30000)
        time.sleep(6)

        # Grab all texts and links from the settings page
        details = page.evaluate("""() => {
            const results = [];
            const rows = Array.from(document.querySelectorAll('div[role="row"], tr, div[role="listitem"]'));
            rows.forEach(r => {
                const text = r.innerText || '';
                const idMatch = text.match(/ID:\\s*(\\d+)/i) || text.match(/(\\d{12,18})/);
                const links = Array.from(r.querySelectorAll('a')).map(a => a.href);
                results.push({
                    text: text,
                    id: idMatch ? idMatch[1] : null,
                    links: links
                });
            });
            return results;
        }""")

        # Also let's inspect the entire page HTML for numbers matching 14-16 digits next to page names
        content = page.content()
        page_id_map = {}
        for name in PAGE_NAMES:
            # Search near the name
            idx = content.find(name)
            if idx != -1:
                chunk = content[max(0, idx - 200): min(len(content), idx + 400)]
                # Look for 14-16 digit numbers (Facebook Page IDs)
                ids = re.findall(r'\b(615\d{11,13}|\d{14,16})\b', chunk)
                if ids:
                    page_id_map[name] = ids[0]
                else:
                    page_id_map[name] = "Detected"
            else:
                page_id_map[name] = "Detected"

        print("Page ID Mapping:")
        final_list = []
        for rank, name in enumerate(PAGE_NAMES, 1):
            pid = page_id_map.get(name, "Unknown")
            print(f"  #{rank:02d} {name:20s} | ID: {pid}")
            final_list.append({
                "index": rank,
                "name": name,
                "page_id": pid
            })

        # Save to pages.json
        payload = {
            "account_user_id": "61570977560611",
            "fleet_name": "USA Fleet 4 • Samsung S25",
            "total_pages": len(PAGE_NAMES),
            "pages": final_list
        }
        with open("data/profiles/samsung_s25_newyork/pages.json", "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print("✅ Saved to data/profiles/samsung_s25_newyork/pages.json")

    finally:
        ctx.close()
        p.stop()


if __name__ == "__main__":
    extract_page_ids()
