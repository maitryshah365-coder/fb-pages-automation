"""
Extract exact Facebook Page IDs for all 15 Rohini Dutt pages from Meta Business Suite.
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


def extract_page_ids_deep():
    print("--> Launching browser to fetch exact Page IDs from Meta Business Suite...")
    p, ctx, page = launch_android_browser(S25_NEWYORK_PROFILE, headless=True)

    try:
        page.goto("https://business.facebook.com/latest/settings/pages", wait_until="domcontentloaded", timeout=30000)
        time.sleep(6)

        # Let's inspect all rows
        rows_data = page.evaluate("""() => {
            const results = [];
            const rows = Array.from(document.querySelectorAll('div[role="row"]'));
            rows.forEach((r, idx) => {
                const text = r.innerText.trim();
                const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                // Look for links or buttons
                const links = Array.from(r.querySelectorAll('a')).map(a => a.href);
                results.push({
                    index: idx,
                    lines: lines,
                    links: links,
                    html: r.innerHTML.slice(0, 300)
                });
            });
            return results;
        }""")

        print(f"--> Found {len(rows_data)} rows in settings:")
        for r in rows_data[:18]:
            print(f"Row {r['index']}: {r['lines']}")

        # Now let's click on each page row or check the right pane to get the Page ID
        # In MBS, clicking a row displays the Page ID in the right detail pane (e.g. "Page ID: 1234567890")
        page_id_map = {}
        for row_idx in range(1, 16):
            try:
                # Click row
                row_selector = f'div[role="row"]:nth-child({row_idx + 1})'
                row_el = page.query_selector(row_selector)
                if row_el:
                    row_el.click()
                    time.sleep(1.5)
                    # Check right pane text for Page ID
                    pane_text = page.evaluate("""() => {
                        const bodyText = document.body.innerText;
                        const match = bodyText.match(/Page ID[:\\s]+(\\d{10,20})/i) || bodyText.match(/ID[:\\s]+(\\d{10,20})/i);
                        return match ? match[1] : null;
                    }""")
                    row_text = row_el.inner_text().split('\n')[0]
                    if pane_text:
                        page_id_map[row_text] = pane_text
                        print(f"  ✅ {row_text} -> Page ID: {pane_text}")
            except Exception as e:
                pass

        print(f"\n--> Successfully mapped {len(page_id_map)} page IDs directly from detail pane!")
        return page_id_map

    finally:
        ctx.close()
        p.stop()


if __name__ == "__main__":
    extract_page_ids_deep()
