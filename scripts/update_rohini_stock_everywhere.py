"""
Update Rohini Dutt deep scan results (3,779 videos) across all data stores,
configurations, and dashboard JSON files.
"""

import os
import sys
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROHINI_JSON = os.path.join(BASE_DIR, "data", "rohini_dutt_drive_folders.json")
PERM_PAGES_JSON = os.path.join(BASE_DIR, "data", "usa_account4_rohini_permanent_pages.json")
CONFIG_YAML = os.path.join(BASE_DIR, "config_usa_account4.yaml")
AUDIT_JSON_1 = os.path.join(BASE_DIR, "data", "drive_folders_audit.json")
AUDIT_JSON_2 = os.path.join(BASE_DIR, "docs", "data", "drive_folders_audit.json")
PAGES_DATA_DOCS = os.path.join(BASE_DIR, "docs", "data", "pages_data.json")
PAGES_DATA_WEB = os.path.join(BASE_DIR, "web", "data", "pages_data.json")
INDEX_HTML_DOCS = os.path.join(BASE_DIR, "docs", "index.html")
INDEX_HTML_WEB = os.path.join(BASE_DIR, "web", "index.html")


def update_all():
    print("=" * 70)
    print("🔄 SYNCING DEEP SCAN ROHINI DUTT DRIVE STOCK (3,779 VIDEOS) EVERYWHERE")
    print("=" * 70)

    with open(ROHINI_JSON, "r", encoding="utf-8") as f:
        scan_data = json.load(f)

    folders = scan_data["folders"]
    print(f"Loaded {len(folders)} deep-scanned folders from {ROHINI_JSON}")
    total_rohini_videos = scan_data["total_videos"]
    print(f"Total Deep-Scanned Videos: {total_rohini_videos}")

    # Helper to match page name to scanned folder
    def find_matched_folder(page_name):
        p_clean = page_name.lower().replace(" ", "").replace("'", "")
        for fname, fdata in folders.items():
            f_clean = fname.lower().replace(" ", "").replace("'", "")
            if f_clean == p_clean:
                return fdata
            if "joker" in f_clean and "joker" in p_clean:
                return fdata
            if ("vally" in f_clean or "valley" in f_clean) and ("vally" in p_clean or "valley" in p_clean):
                return fdata
            if f_clean in p_clean or p_clean in f_clean:
                return fdata
        return None

    # 1. Update data/usa_account4_rohini_permanent_pages.json
    with open(PERM_PAGES_JSON, "r", encoding="utf-8") as f:
        perm_data = json.load(f)

    perm_total = 0
    for p in perm_data.get("pages", []):
        m = find_matched_folder(p["name"])
        if m:
            p["drive_videos_count"] = m["video_count"]
            p["drive_folder_id"] = m["folder_id"]
            p["drive_folder_name"] = m["folder_name"]
            perm_total += m["video_count"]
            print(f"  {p['name']:20s} ➔ {m['video_count']} videos (Folder: {m['folder_name']})")
        else:
            print(f"  ⚠️ Warning: No folder match for {p['name']}")

    perm_data["total_stock_videos"] = perm_total
    with open(PERM_PAGES_JSON, "w", encoding="utf-8") as f:
        json.dump(perm_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Updated {PERM_PAGES_JSON} (Total: {perm_total} videos)")

    # 2. Update drive_folders_audit.json in data/ and docs/data/
    for audit_path in [AUDIT_JSON_1, AUDIT_JSON_2]:
        if os.path.exists(audit_path):
            with open(audit_path, "r", encoding="utf-8") as f:
                audit = json.load(f)

            for k, val in list(audit.items()):
                if k == "total_videos":
                    continue
                if isinstance(val, dict):
                    m = find_matched_folder(k)
                    if m:
                        val["video_count"] = m["video_count"]
                        val["total_size_mb"] = m.get("size_mb", 0)

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
                if "Rohini" in p_owner or "Rohini" in p_acc:
                    m = find_matched_folder(p["name"])
                    if m:
                        p["drive_videos_count"] = m["video_count"]
                        p["drive_folder_id"] = m["folder_id"]
                        p["drive_folder_name"] = m["folder_name"]
                        p["has_drive_folder"] = True

            with open(pages_path, "w", encoding="utf-8") as f:
                json.dump(pdata, f, indent=2, ensure_ascii=False)
            print(f"✅ Updated {pages_path}")

    # 4. Calculate total portfolio cloud stock across all 141 pages
    with open(PAGES_DATA_DOCS, "r", encoding="utf-8") as f:
        pdata = json.load(f)
    portfolio_total_stock = sum(p.get("drive_videos_count", 0) for p in pdata.get("pages", []))
    print(f"\n🌟 GRAND TOTAL PORTFOLIO CLOUD STOCK: {portfolio_total_stock:,} Videos across 141 Pages")
    print(f"🌟 ROHINI DUTT STOCK:                 {perm_total:,} Videos")

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
            # Update Rohini hero stock stat
            html = re.sub(
                r'id="driveHeroA4Count"[^>]*>[\d,]+ Videos<',
                f'id="driveHeroA4Count" style="color: #38bdf8;">{perm_total:,} Videos<',
                html
            )

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"✅ Updated {html_path} with {portfolio_total_stock:,} Total & {perm_total:,} Rohini Stock")

    print("\n🎉 ALL DATA SOURCES SUCCESSFULLY SYNCHRONIZED WITH REAL DEEP SCAN NUMBERS!")
    print("=" * 70)


if __name__ == "__main__":
    update_all()
