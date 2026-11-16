import yaml
import json
import glob
import re
import os

print("=" * 80)
print("COMPREHENSIVE FLEET UPLOAD READINESS AUDIT (GROUND TRUTH)")
print("=" * 80)

# 1. Read Workflows
with open('.github/workflows/post.yml', 'r', encoding='utf-8') as f:
    post_yml = f.read()

uk_yml = ""
if os.path.exists('.github/workflows/uk_london_post.yml'):
    with open('.github/workflows/uk_london_post.yml', 'r', encoding='utf-8') as f:
        uk_yml = f.read()

# 2. Check each account
fleet_definitions = [
    {"fleet": "USA 01", "name": "Meghal Chauhan", "config": "config.yaml", "pages_slice": (0, 15), "wf": "post.yml"},
    {"fleet": "USA 02", "name": "Mia Shah", "config": "config.yaml", "pages_slice": (15, 30), "wf": "post.yml"},
    {"fleet": "USA 03", "name": "Radika Patel", "config": "config.yaml", "pages_slice": (30, 45), "wf": "post.yml"},
    {"fleet": "USA 04", "name": "Rohini Dutt", "config": "config_usa_account4.yaml", "pages_slice": (0, 15), "wf": "post.yml"},
    {"fleet": "USA 05", "name": "Sejal Soni", "config": "config_usa_account5.yaml", "pages_slice": (0, 12), "wf": "post.yml"},
    {"fleet": "USA 06", "name": "Kalpesh Shah", "config": "config_usa_account6.yaml", "pages_slice": (0, 14), "wf": "post.yml"},
    {"fleet": "USA 07", "name": "Henny Panchal", "config": "config_usa_account7.yaml", "pages_slice": (0, 14), "wf": "post.yml"},
    {"fleet": "USA 08", "name": "Kiya Taily", "config": "config_usa_account8.yaml", "pages_slice": (0, 14), "wf": "post.yml"},
    {"fleet": "USA 09", "name": "Prince Shah", "config": "config_usa_account9.yaml", "pages_slice": (0, 13), "wf": "post.yml"},
    {"fleet": "USA 10", "name": "Sweta Mummu", "config": "config_usa_account10.yaml", "pages_slice": (0, 18), "wf": "post.yml"},
    {"fleet": "UK 01", "name": "Binjal Mehra", "config": "config_uk_account1.yaml", "pages_slice": (0, 12), "wf": "uk_london_post.yml"},
    {"fleet": "UK 02", "name": "Chanda Nai", "config": "config_uk_account2.yaml", "pages_slice": (0, 12), "wf": "uk_london_post.yml"},
    {"fleet": "UK 03", "name": "Mahi Patel", "config": "config_uk_account3.yaml", "pages_slice": (0, 12), "wf": "uk_london_post.yml"},
    {"fleet": "UK 04", "name": "Nidhi Desai", "config": "config_uk_account4.yaml", "pages_slice": (0, 11), "wf": "uk_london_post.yml"},
    {"fleet": "UK 05", "name": "Richi Patel", "config": "config_uk_account5.yaml", "pages_slice": (0, 11), "wf": "uk_london_post.yml"},
    {"fleet": "UK 06", "name": "Sweta Shah", "config": "config_uk_account6.yaml", "pages_slice": (0, 12), "wf": "uk_london_post.yml"},
    {"fleet": "UK 07", "name": "Riya Gaur", "config": "config_uk_account7.yaml", "pages_slice": (0, 11), "wf": "uk_london_post.yml"},
]

results = []

for item in fleet_definitions:
    cpath = item["config"]
    if not os.path.exists(cpath):
        results.append({
            "fleet": item["fleet"],
            "name": item["name"],
            "status": "CONFIG_MISSING",
            "details": f"File {cpath} not found"
        })
        continue

    with open(cpath, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)

    all_pages = cfg.get("pages", [])
    s, e = item["pages_slice"]
    fleet_pages = all_pages[s:e] if cpath == "config.yaml" else all_pages

    total = len(fleet_pages)
    enabled = sum(1 for p in fleet_pages if p.get("enabled", False))
    has_token = sum(1 for p in fleet_pages if bool(p.get("page_access_token")))
    
    # Check drive folder ids
    pending_drive = sum(1 for p in fleet_pages if not p.get("drive_folder_id") or str(p.get("drive_folder_id")).startswith("PENDING"))
    valid_drive = total - pending_drive

    # Check workflow cron for this account
    cron_match = None
    target_wf = post_yml if item["wf"] == "post.yml" else uk_yml
    
    # Search for account name or fleet in workflow
    pattern = rf'cron:\s*"([^"]+)"\s*#?\s*.*{item["name"].split()[0]}'
    m = re.search(pattern, target_wf, re.IGNORECASE)
    if not m:
        # try searching for Account number e.g. "Account 1" or "Account 9"
        num = item["fleet"].split()[-1].lstrip("0")
        pattern2 = rf'cron:\s*"([^"]+)"\s*#?\s*.*Account {num}'
        m = re.search(pattern2, target_wf, re.IGNORECASE)

    cron_str = m.group(1) if m else "NO_CRON_FOUND"

    # Overall verdict
    if enabled == total and valid_drive == total and has_token == total and cron_str != "NO_CRON_FOUND":
        verdict = "100% READY"
    elif pending_drive > 0 or enabled == 0:
        verdict = "ON_HOLD (Awaiting Drive/Disabled)"
    else:
        verdict = "PARTIAL_OR_CHECK"

    results.append({
        "fleet": item["fleet"],
        "name": item["name"],
        "total_pages": total,
        "enabled": enabled,
        "tokens": has_token,
        "valid_drive": valid_drive,
        "pending_drive": pending_drive,
        "cron": cron_str,
        "verdict": verdict
    })

print(f"{'Fleet':7} | {'Account Name':16} | {'Pages':5} | {'Enabled':7} | {'Tokens':6} | {'Drive Mapped':12} | {'Cron Schedule':22} | {'Readiness'}")
print("-" * 110)
for r in results:
    print(f"{r['fleet']:7} | {r['name']:16} | {r['total_pages']:5} | {r['enabled']:7} | {r['tokens']:6} | {r['valid_drive']}/{r['total_pages']} mapped    | {r['cron']:22} | {r['verdict']}")

print("\n" + "=" * 80)

