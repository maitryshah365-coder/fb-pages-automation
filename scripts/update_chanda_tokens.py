import os
import sys
import json
import yaml
import requests

sys.stdout.reconfigure(encoding='utf-8')

USER_TOKEN = "EAAUoHP9uV2oBSoHcoka8CeNeQuOQk1ov9f2CUuZC5cf4LENotFVSI7AZAtr8d1RHWU40HJ633knhRQX9NJqQLmnT32YIAKtVWgyAXsM103DR7uiCITKNQOmkZByXJnG9eRyVXfImSjSrgEMzCU8JpaOT1W1tmW5dscGPcwtyjo4t3QYREbAp9R5sKxGNW1d550JOxw5umF8WAxh"
BASE_URL = "https://graph.facebook.com/v21.0"

print("==================================================")
print("       UPDATING CHANDA NAI (UK 2) TOKENS          ")
print("==================================================")

# 1. Fetch user info
u_resp = requests.get(f"{BASE_URL}/me", params={"access_token": USER_TOKEN, "fields": "id,name"}, timeout=15)
if not u_resp.ok:
    print(f"❌ User authentication failed: {u_resp.status_code} - {u_resp.text}")
    sys.exit(1)

u_data = u_resp.json()
print(f"✅ User Authenticated: {u_data.get('name')} (ID: {u_data.get('id')})\n")

# 2. Fetch pages & tokens from /me/accounts
acc_resp = requests.get(f"{BASE_URL}/me/accounts", params={
    "access_token": USER_TOKEN,
    "limit": 100,
    "fields": "id,name,access_token,category,followers_count,fan_count,picture.type(large)"
}, timeout=15)
if not acc_resp.ok:
    print(f"❌ Failed to fetch accounts: {acc_resp.status_code} - {acc_resp.text}")
    sys.exit(1)

api_pages = acc_resp.json().get("data", [])
print(f"✅ Retrieved {len(api_pages)} pages from Meta Graph API.")

page_map = {}
for p in api_pages:
    pid = str(p.get("id"))
    page_map[pid] = {
        "id": pid,
        "name": p.get("name"),
        "access_token": p.get("access_token"),
        "category": p.get("category", "Digital Creator"),
        "followers": p.get("followers_count") or p.get("fan_count") or 0,
        "pic_url": p.get("picture", {}).get("data", {}).get("url", f"https://graph.facebook.com/v21.0/{pid}/picture?type=large")
    }

# 3. Verify each token independently
print("\n--- Verifying Each Page Token ---")
verified_count = 0
for pid, info in page_map.items():
    v_url = f"{BASE_URL}/{pid}?fields=id,name&access_token={info['access_token']}"
    vr = requests.get(v_url, timeout=10)
    if vr.ok:
        print(f"  ✅ [VALID] {info['name']:25} (ID: {pid})")
        verified_count += 1
    else:
        print(f"  ❌ [FAIL]  {info['name']:25} (ID: {pid}): {vr.text[:50]}")

print(f"\nSuccessfully verified {verified_count}/{len(page_map)} page tokens.")

# 4. Update config_uk_account2.yaml
cfg_file = "config_uk_account2.yaml"
if os.path.exists(cfg_file):
    with open(cfg_file, "r", encoding="utf-8") as fp:
        cfg = yaml.safe_load(fp)
    
    updated_cfg_pages = 0
    for page in cfg.get("pages", []):
        pid = str(page.get("page_id", ""))
        if pid in page_map:
            page["page_access_token"] = page_map[pid]["access_token"]
            updated_cfg_pages += 1
            
    with open(cfg_file, "w", encoding="utf-8") as fp:
        yaml.dump(cfg, fp, sort_keys=False, allow_unicode=True)
    print(f"✅ Updated {updated_cfg_pages} pages in {cfg_file}")

# 5. Update data/uk_account2_chanda_pages.json
chanda_json_1 = "data/uk_account2_chanda_pages.json"
if os.path.exists(chanda_json_1):
    with open(chanda_json_1, "r", encoding="utf-8") as fp:
        c_list = json.load(fp)
    c_updated = 0
    for item in c_list:
        pid = str(item.get("id") or item.get("page_id", ""))
        if pid in page_map:
            item["access_token"] = page_map[pid]["access_token"]
            c_updated += 1
    with open(chanda_json_1, "w", encoding="utf-8") as fp:
        json.dump(c_list, fp, indent=2, ensure_ascii=False)
    print(f"✅ Updated {c_updated} items in {chanda_json_1}")

# 6. Update data/uk_account2_chanda_permanent_pages.json
chanda_json_2 = "data/uk_account2_chanda_permanent_pages.json"
if os.path.exists(chanda_json_2):
    with open(chanda_json_2, "r", encoding="utf-8") as fp:
        c_perm = json.load(fp)
    c_perm_updated = 0
    target_list = c_perm if isinstance(c_perm, list) else c_perm.get("pages", [])
    for item in target_list:
        pid = str(item.get("id") or item.get("page_id", ""))
        if pid in page_map:
            item["access_token"] = page_map[pid]["access_token"]
            c_perm_updated += 1
    with open(chanda_json_2, "w", encoding="utf-8") as fp:
        json.dump(c_perm, fp, indent=2, ensure_ascii=False)
    print(f"✅ Updated {c_perm_updated} items in {chanda_json_2}")

# 7. Update docs/data/pages_data.json & web/data/pages_data.json
for ppath in ["docs/data/pages_data.json", "web/data/pages_data.json"]:
    if os.path.exists(ppath):
        with open(ppath, "r", encoding="utf-8") as fp:
            pdata = json.load(fp)
        p_up = 0
        for item in pdata.get("pages", []):
            pid = str(item.get("id") or item.get("page_id", ""))
            if pid in page_map:
                item["access_token"] = page_map[pid]["access_token"]
                item["is_configured"] = True
                p_up += 1
        with open(ppath, "w", encoding="utf-8") as fp:
            json.dump(pdata, fp, indent=2, ensure_ascii=False)
        print(f"✅ Updated {p_up} items in {ppath}")

print("\n==================================================")
print("SUCCESS: Chanda Nai (UK 2) tokens updated across all configs!")
print("==================================================")
