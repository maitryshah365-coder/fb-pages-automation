"""
Synchronize exact deep-scanned video stock for Sejal Soni (3,131 Reels • 45.57 GB)
across all configurations, datasets, diagnostics, and UI dashboard files.
"""

import os
import sys
import json
import re

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SEJAL_JSON = os.path.join(BASE_DIR, "data", "sejal_soni_drive_folders.json")
PERM_PAGES_JSON = os.path.join(BASE_DIR, "data", "usa_account5_sejal_permanent_pages.json")
AUDIT_JSON_1 = os.path.join(BASE_DIR, "data", "drive_folders_audit.json")
AUDIT_JSON_2 = os.path.join(BASE_DIR, "docs", "data", "drive_folders_audit.json")
PAGES_DATA_DOCS = os.path.join(BASE_DIR, "docs", "data", "pages_data.json")
PAGES_DATA_WEB = os.path.join(BASE_DIR, "web", "data", "pages_data.json")
INDEX_HTML_DOCS = os.path.join(BASE_DIR, "docs", "index.html")
INDEX_HTML_WEB = os.path.join(BASE_DIR, "web", "index.html")
GOLD_APP_DOCS = os.path.join(BASE_DIR, "docs", "js", "gold_app.js")
GOLD_APP_WEB = os.path.join(BASE_DIR, "web", "js", "gold_app.js")


def update_everything():
    print("=" * 70)
    print("🔄 SYNCING DEEP SCAN SEJAL SONI DRIVE STOCK (3,131 REELS) EVERYWHERE")
    print("=" * 70)

    with open(SEJAL_JSON, "r", encoding="utf-8") as f:
        scan_data = json.load(f)

    scanned_folders = scan_data["folders"]
    total_videos = scan_data["total_videos"]
    total_gb = scan_data["total_gb"]
    print(f"Loaded {len(scanned_folders)} deep-scanned folders ({total_videos:,} videos, {total_gb} GB)")

    def find_match(p_name):
        p_clean = p_name.lower().replace(" ", "").replace("'", "")
        for fname, fdata in scanned_folders.items():
            f_clean = fname.lower().replace(" ", "").replace("'", "")
            if f_clean == p_clean or f_clean in p_clean or p_clean in f_clean:
                return fdata
        return None

    # 1. Update data/usa_account5_sejal_permanent_pages.json
    with open(PERM_PAGES_JSON, "r", encoding="utf-8") as f:
        perm_data = json.load(f)

    perm_total = 0
    for p in perm_data.get("pages", []):
        m = find_match(p["name"])
        if m:
            p["drive_videos_count"] = m["video_count"]
            p["drive_folder_id"] = m["folder_id"]
            p["drive_folder_name"] = m["folder_name"]
            perm_total += m["video_count"]
            print(f"  {p['name']:25s} ➔ {m['video_count']:4d} videos ({m['size_mb']} MB)")
        else:
            print(f"  ⚠️ Warning: No match for {p['name']}")

    perm_data["total_stock_videos"] = perm_total
    perm_data["total_stock_gb"] = total_gb
    with open(PERM_PAGES_JSON, "w", encoding="utf-8") as f:
        json.dump(perm_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Updated {PERM_PAGES_JSON} (Total: {perm_total:,} videos)")

    # 2. Update drive_folders_audit.json in data/ and docs/data/
    for audit_path in [AUDIT_JSON_1, AUDIT_JSON_2]:
        if os.path.exists(audit_path):
            with open(audit_path, "r", encoding="utf-8") as f:
                audit = json.load(f)

            for p in perm_data["pages"]:
                p_name = p["name"]
                m = find_match(p_name)
                audit[p_name] = {
                    "video_count": p["drive_videos_count"],
                    "folder_id": p["drive_folder_id"],
                    "folder_name": p["drive_folder_name"],
                    "size_mb": m["size_mb"] if m else 0,
                    "account": "Sejal Soni (USA 5)",
                    "region": "US"
                }

            total_stock_all = sum(v.get("video_count", 0) for k, v in audit.items() if isinstance(v, dict))
            audit["total_videos"] = total_stock_all

            with open(audit_path, "w", encoding="utf-8") as f:
                json.dump(audit, f, indent=2, ensure_ascii=False)
            print(f"✅ Updated {audit_path} (Global Total: {total_stock_all:,} videos)")

    # 3. Update docs/data/pages_data.json and web/data/pages_data.json
    for pages_path in [PAGES_DATA_DOCS, PAGES_DATA_WEB]:
        if os.path.exists(pages_path):
            with open(pages_path, "r", encoding="utf-8") as f:
                pdata = json.load(f)

            for p in pdata.get("pages", []):
                p_owner = p.get("account_owner", "")
                p_acc = p.get("account", "")
                if "Sejal" in p_owner or "Sejal" in p_acc:
                    m = find_match(p["name"])
                    if m:
                        p["drive_videos_count"] = m["video_count"]
                        p["drive_folder_id"] = m["folder_id"]
                        p["drive_folder_name"] = m["folder_name"]
                        p["has_drive_folder"] = True

            with open(pages_path, "w", encoding="utf-8") as f:
                json.dump(pdata, f, indent=2, ensure_ascii=False)
            print(f"✅ Updated {pages_path}")

    # 4. Calculate total portfolio cloud stock across all pages
    with open(PAGES_DATA_DOCS, "r", encoding="utf-8") as f:
        pdata = json.load(f)
    portfolio_total_stock = sum(p.get("drive_videos_count", 0) for p in pdata.get("pages", []))
    print(f"\n🌟 GRAND TOTAL PORTFOLIO CLOUD STOCK: {portfolio_total_stock:,} Videos across all pages")
    print(f"🌟 SEJAL SONI DEEP STOCK:             {perm_total:,} Videos ({total_gb} GB)")

    # 5. Update index.html in docs/ and web/
    for html_path in [INDEX_HTML_DOCS, INDEX_HTML_WEB]:
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                html = f.read()

            # Update total cloud stock stat
            html = re.sub(
                r'id="driveHeroTotalCount">[\d,]+ Videos<',
                f'id="driveHeroTotalCount">{portfolio_total_stock:,} Videos<',
                html
            )
            # Update Sejal hero stock stat
            html = re.sub(
                r'id="driveHeroA5Count"[^>]*>[\d,]+ Videos<',
                f'id="driveHeroA5Count" style="color: #a78bfa;">{perm_total:,} Videos<',
                html
            )

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"✅ Updated {html_path} with {perm_total:,} Sejal Stock & {portfolio_total_stock:,} Global Total")

    # 6. Update gold_app.js in docs/ and web/
    for js_path in [GOLD_APP_DOCS, GOLD_APP_WEB]:
        if os.path.exists(js_path):
            with open(js_path, "r", encoding="utf-8") as f:
                js = f.read()

            # Update stock_videos & stock_gb for Sejal Soni profile
            js = re.sub(
                r'(profile_code:\s*"USA-NYC-PIXEL9"[\s\S]*?stock_videos:\s*)\d+',
                r'\g<1>' + str(perm_total),
                js
            )
            js = re.sub(
                r'(profile_code:\s*"USA-NYC-PIXEL9"[\s\S]*?stock_gb:\s*)"[^"]+"',
                r'\g<1>"' + f"{total_gb} GB" + '"',
                js
            )

            # Update individual page stock counts inside Sejal Soni profile in gold_app.js
            for p in perm_data["pages"]:
                p_name = p["name"]
                cnt = p["drive_videos_count"]
                # Match { name: "The Daily Spark", stock: 100, ... }
                pattern = rf'(\{{\s*name:\s*"{re.escape(p_name)}",\s*stock:\s*)\d+'
                js = re.sub(pattern, rf'\g<1>{cnt}', js)

            with open(js_path, "w", encoding="utf-8") as f:
                f.write(js)
            print(f"✅ Updated {js_path} with individual page deep stock counts")

    # 7. Re-generate pixel9_device_health.json
    import subprocess
    subprocess.run([sys.executable, os.path.join(BASE_DIR, "scripts", "generate_pixel9_health_data.py")], check=True)
    print("✅ Re-generated pixel9_device_health.json with exact deep stock!")

    print("\n🎉 ALL DATA SOURCES SUCCESSFULLY SYNCHRONIZED WITH ACCURATE DEEP SCAN NUMBERS!")


if __name__ == "__main__":
    update_everything()
