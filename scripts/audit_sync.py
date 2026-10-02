import json
import os
import glob
import yaml

base_dir = r"e:\Anty Working\Google_Drive_to_Facebook_Automation_Master_Spec"

print("--- AUDITING PAGES_DATA.JSON ---")
for p_path in [os.path.join(base_dir, "docs", "data", "pages_data.json"), os.path.join(base_dir, "web", "data", "pages_data.json")]:
    if not os.path.exists(p_path):
        print(f"MISSING: {p_path}")
        continue
    with open(p_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    pages = data.get("pages", [])
    print(f"\nFile: {p_path}")
    print(f"Total Pages Count: {len(pages)}")
    print(f"Portfolio Total Pages: {data.get('portfolio', {}).get('total_pages')}")
    print(f"Portfolio Total Stock: {data.get('portfolio', {}).get('total_stock_videos')}")
    print(f"Portfolio Total Views: {data.get('portfolio', {}).get('total_views')}")
    print(f"Portfolio Total Followers: {data.get('portfolio', {}).get('total_followers')}")
    print(f"Today Summary: {data.get('today_summary')}")
    
    # Check nulls or missing fields across pages
    missing_views = [p["name"] for p in pages if p.get("total_views") is None]
    missing_followers = [p["name"] for p in pages if p.get("followers") is None]
    missing_stock = [p["name"] for p in pages if p.get("drive_videos_count") is None]
    zero_stock = [p["name"] for p in pages if p.get("drive_videos_count") == 0]
    
    print(f"Missing views count: {len(missing_views)}")
    print(f"Missing followers count: {len(missing_followers)}")
    print(f"Missing stock count: {len(missing_stock)}")
    print(f"Zero stock count: {len(zero_stock)}")
    if zero_stock:
        print(f"Pages with 0 stock: {zero_stock[:10]}")

print("\n--- CHECKING DRIVE_CONFIGURED_PAGES IN GOLD_APP.JS ---")
for js_path in [os.path.join(base_dir, "docs", "js", "gold_app.js"), os.path.join(base_dir, "web", "js", "gold_app.js")]:
    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()
    start = content.find("const DRIVE_CONFIGURED_PAGES = {")
    end = content.find("};", start)
    block = content[start:end]
    lines = [l.strip() for l in block.splitlines() if l.strip().startswith('"')]
    print(f"{js_path}: {len(lines)} entries in DRIVE_CONFIGURED_PAGES")
