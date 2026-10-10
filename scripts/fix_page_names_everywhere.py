#!/usr/bin/env python3
"""
Fix Page Names Everywhere
Ensures all 156 Facebook pages across docs/data/pages_data.json, web/data/pages_data.json,
and configuration files have their real display names instead of generic 'Page X' or numbers.
"""

import os
import sys
import json
import re
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load name mappings from gold_app.js DRIVE_CONFIGURED_PAGES
with open(os.path.join(BASE_DIR, "docs", "js", "gold_app.js"), "r", encoding="utf-8") as f:
    js_text = f.read()

name_map = dict(re.findall(r'"(\d{14,17})":\s*\{\s*pageName:\s*"[^"]+",\s*displayName:\s*"([^"]+)"', js_text))
print(f"Loaded {len(name_map)} authentic page display names from DRIVE_CONFIGURED_PAGES.")

# 1. Update docs/data/pages_data.json and web/data/pages_data.json
for folder in ["docs/data", "web/data"]:
    target_path = os.path.join(BASE_DIR, folder, "pages_data.json")
    if not os.path.exists(target_path):
        continue
    
    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    updated_count = 0
    for p in data.get("pages", []):
        pid = str(p.get("id"))
        curr_name = (p.get("name") or "").strip()
        curr_dname = (p.get("display_name") or "").strip()
        
        # Check if page has real name mapped
        if pid in name_map:
            real_name = name_map[pid]
            if curr_name.startswith("Page ") or curr_name.startswith("page_") or not curr_name:
                p["name"] = real_name
                updated_count += 1
            if not curr_dname or curr_dname.startswith("Page ") or curr_dname.startswith("page_"):
                p["display_name"] = real_name
                
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Updated {updated_count} page names in {target_path}")

# 2. Update config.yaml with display_name for pages 1-30 if missing
config_path = os.path.join(BASE_DIR, "config.yaml")
if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    
    cfg_updated = 0
    for p in cfg.get("pages", []):
        pid = str(p.get("page_id", ""))
        if pid in name_map:
            real_name = name_map[pid]
            if not p.get("display_name") or p.get("display_name").startswith("page_"):
                p["display_name"] = real_name
                cfg_updated += 1
                
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True)
    print(f"Updated {cfg_updated} display_name entries in {config_path}")

print("✅ All page names successfully updated across datasets and configs!")
