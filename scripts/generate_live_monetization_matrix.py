"""
Master Fleet Monetization Matrix Generator (USA & UK Fleets Only - 12 Accounts)
Strictly operates within the project repository workspace.
"""

import json
import os
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load existing master file as starting baseline
data_path = os.path.join(BASE_DIR, 'data', 'master_fleet_monetization.json')
with open(data_path, 'r', encoding='utf-8') as f:
    master = json.load(f)

# Normalize string helper
def norm(s):
    if not s:
        return ""
    return " ".join(str(s).lower().replace("  ", " ").strip().split())

# Filter strictly to the 12 USA & UK accounts (remove any IND accounts)
ALLOWED_ACCOUNT_IDS = {
    "usa_account1_meghal",
    "usa_account2_mia",
    "usa_account3_radika",
    "samsung_s25_newyork",
    "google_pixel9_newyork",
    "uk_account1_binjal",
    "uk_account2_chanda",
    "uk_account3_mahi",
    "uk_account4_nidhi",
    "uk_account5_richi",
    "uk_account6_sweta",
    "uk_account7_riya"
}

master['accounts'] = [acc for acc in master['accounts'] if acc.get('account_id') in ALLOWED_ACCOUNT_IDS]

# Criteria pages within USA and UK fleet accounts
CRITERIA_TARGETS = {
    # UK (Binjal Mehra)
    "wood stephen", "wooden speten", "roberts austin", "roberst austin",
    "bitter lullaby", "rogers albert", "mitchell jack", "michell jack",
    "young bradley", "young bredlly",
    # UK (Chanda Nai)
    "infinite stories", "dandelion diaries", "james jose", "hill alan",
    # UK (Mahi Patel)
    "shifting stone",
    # UK (Nidhi Desai)
    "smith arthur", "robinson stephen", "robinsom stephen", "rodriguez scott",
    "mitchell gabriel",
    # UK (Riya Gaur)
    "corner spe", "lee charles",
    
    # USA (Meghal Chauhan)
    "fresh hive network", "silent peak social",
    # USA (Mia Shah)
    "gonzales jordan",
    # USA (Radika Patel)
    "potato flamingo", "sthefany oliveira",
    # USA (Rohini Dutt)
    "me the",
}

# Setup Stars & Subscriptions targets (USA & UK fleet accounts)
SETUP_STARS_TARGETS = {
    "robinson jerry", "robison jerry",
    "alexander christopher",
    "johnson jerry",
    "prestige frontier",
    "me text",
    "mitchell gabriel",
    "roberts richard",
    "roberts austin",
    "rogers albert",
    "morgan donald",
    "cooper billy",
    "martin john",
    "memes & mischief",
    "crown empire",
    "the entertainment zone",
    "shadow executive",
    "alpha dynasty",
    "cracked bell",
    "collapse the sky",
    "broken halo",
    "blame the weather",
    "perez steven",
}

SETUP_SUBS_TARGETS = {
    "apex house",
    "prestige frontier",
    "me text",
    "robinson jerry", "robison jerry",
    "alexander christopher",
    "johnson jerry",
}

# Ensure missing UK pages from permanent registries are present in their accounts
for acc in master['accounts']:
    acc_id = acc.get('account_id')
    pages = acc.get('pages', [])
    
    if acc_id == "uk_account4_nidhi":
        if not any("857530914106167" == p.get('page_id') or "robinson jerry" in norm(p.get('name')) for p in pages):
            pages.append({
                "name": "Robinson  Jerry",
                "page_id": "857530914106167",
                "overall_status": "No Monetization Violations",
                "content_monetization": "Criteria Not Met",
                "subscriptions": "Set Up",
                "stars": "Set Up",
                "policy_details": "No Violations (Clean)",
                "recommendation": "Recommendable"
            })
            
    if acc_id == "uk_account7_riya":
        if not any("755318371007926" == p.get('page_id') or "alexander" in norm(p.get('name')) for p in pages):
            pages.append({
                "name": "Alexander  Christopher",
                "page_id": "755318371007926",
                "overall_status": "No Monetization Violations",
                "content_monetization": "Criteria Not Met",
                "subscriptions": "Set Up",
                "stars": "Set Up",
                "policy_details": "No Violations (Clean)",
                "recommendation": "Recommendable"
            })
            
    # Apply Criteria & Setup updates strictly for USA & UK
    for p in pages:
        p_norm = norm(p['name'])
        
        # Check criteria match
        is_criteria = False
        for ct in CRITERIA_TARGETS:
            if p_norm == ct:
                is_criteria = True
                break
        if is_criteria:
            p['content_monetization'] = "Waitlist criteria▼"
            
        # Check stars setup
        for st in SETUP_STARS_TARGETS:
            if p_norm == st:
                p['stars'] = "Set Up"
                break
                
        # Check subscriptions setup
        for sub_t in SETUP_SUBS_TARGETS:
            if p_norm == sub_t:
                p['subscriptions'] = "Set Up"
                break
                
    acc['pages'] = pages
    acc['total_pages'] = len(pages)

# Recompute totals for the 12 Accounts
all_pages = []
for acc in master['accounts']:
    all_pages.extend(acc.get('pages', []))

total_stars_active = sum(1 for p in all_pages if 'set up' in str(p.get('stars')).lower() or 'active' in str(p.get('stars')).lower())
total_subs_ready = sum(1 for p in all_pages if 'set up' in str(p.get('subscriptions')).lower() or 'ready' in str(p.get('subscriptions')).lower())
total_waitlist_cm = sum(1 for p in all_pages if 'waitlist' in str(p.get('content_monetization')).lower())

master['generated_at'] = datetime.datetime.now().isoformat()
master['total_accounts'] = len(master['accounts'])
master['active_live_accounts'] = len(master['accounts'])
master['total_fleet_pages'] = len(all_pages)
master['audited_pages_count'] = len(all_pages)
master['total_stars_active'] = total_stars_active
master['total_subs_ready'] = total_subs_ready
master['total_waitlist_criteria'] = total_waitlist_cm

print(f"==================================================")
print(f"Master Fleet Monetization Matrix (USA & UK Only):")
print(f"  • Accounts: {master['total_accounts']}")
print(f"  • Pages: {master['total_fleet_pages']}")
print(f"  • Content Monetization (Criteria/Waitlist): {total_waitlist_cm}")
print(f"  • Stars (Set Up Ready): {total_stars_active}")
print(f"  • Subscriptions (Set Up Ready): {total_subs_ready}")
print(f"==================================================")

# Write to data/, docs/data/, web/data/
for out_dir in ['data', 'docs/data', 'web/data']:
    target = os.path.join(BASE_DIR, out_dir, 'master_fleet_monetization.json')
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, 'w', encoding='utf-8') as out_f:
        json.dump(master, out_f, indent=2, ensure_ascii=False)
    print(f"Saved: {target}")
