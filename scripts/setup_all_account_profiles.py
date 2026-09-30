import os
import sys
import json
import glob

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES_DIR = os.path.join(BASE_DIR, "data", "profiles")
os.makedirs(PROFILES_DIR, exist_ok=True)

# Account Definitions mapping
ACCOUNTS_MAP = [
    {
        "id": "samsung_s25_newyork",
        "name": "Rohini Dutt (USA 4)",
        "owner": "Rohini Dutt",
        "region": "US",
        "timezone": "America/New_York",
        "device": "Samsung Galaxy S25 (SM-S931U)",
        "source_file": "data/usa_account4_rohini_permanent_pages.json"
    },
    {
        "id": "uk_account1_binjal",
        "name": "Binjal Mehra (UK 1)",
        "owner": "Binjal Mehra",
        "region": "UK",
        "timezone": "Europe/London",
        "device": "Samsung Galaxy S24 Ultra (UK 5G)",
        "source_file": "data/uk_account1_binjal_permanent_pages.json"
    },
    {
        "id": "uk_account2_chanda",
        "name": "Chanda (UK 2)",
        "owner": "Chanda",
        "region": "UK",
        "timezone": "Europe/London",
        "device": "Google Pixel 9 Pro (UK)",
        "source_file": "data/uk_account2_chanda_permanent_pages.json"
    },
    {
        "id": "uk_account3_mahi",
        "name": "Mahi (UK 3)",
        "owner": "Mahi",
        "region": "UK",
        "timezone": "Europe/London",
        "device": "Samsung Galaxy S25 (UK)",
        "source_file": "data/uk_account3_mahi_permanent_pages.json"
    },
    {
        "id": "uk_account4_nidhi",
        "name": "Nidhi Desai (UK 4)",
        "owner": "Nidhi Desai",
        "region": "UK",
        "timezone": "Europe/London",
        "device": "Samsung Galaxy S25 (UK)",
        "source_file": "data/uk_account4_nidhi_permanent_pages.json"
    },
    {
        "id": "uk_account5_richi",
        "name": "Richi (UK 5)",
        "owner": "Richi",
        "region": "UK",
        "timezone": "Europe/London",
        "device": "Google Pixel 9 (UK)",
        "source_file": "data/uk_account5_richi_permanent_pages.json"
    },
    {
        "id": "uk_account6_sweta",
        "name": "Sweta (UK 6)",
        "owner": "Sweta",
        "region": "UK",
        "timezone": "Europe/London",
        "device": "Samsung Galaxy S24 (UK)",
        "source_file": "data/uk_account6_sweta_permanent_pages.json"
    },
    {
        "id": "uk_account7_riya",
        "name": "Riya (UK 7)",
        "owner": "Riya",
        "region": "UK",
        "timezone": "Europe/London",
        "device": "OnePlus 13 (UK)",
        "source_file": "data/uk_account7_riya_permanent_pages.json"
    },
    {
        "id": "usa_account3_radika",
        "name": "Radika (USA 3)",
        "owner": "Radika",
        "region": "US",
        "timezone": "America/New_York",
        "device": "Samsung Galaxy S25 (US 5G)",
        "source_file": "data/usa_account3_radika_permanent_pages.json"
    },
    {
        "id": "usa_account1_nidhi",
        "name": "Nidhi Desai (USA 1)",
        "owner": "Nidhi Desai",
        "region": "US",
        "timezone": "America/New_York",
        "device": "Samsung Galaxy S25 (US 5G)",
        "source_fleet": "FLEET_USA_01_IDS"
    },
    {
        "id": "usa_account2_fleet",
        "name": "USA Account 2",
        "owner": "USA 2 Fleet",
        "region": "US",
        "timezone": "America/New_York",
        "device": "Samsung Galaxy S25 (US 5G)",
        "source_fleet": "FLEET_USA_02_IDS"
    }
]

created_count = 0

for acc in ACCOUNTS_MAP:
    acc_dir = os.path.join(PROFILES_DIR, acc["id"])
    os.makedirs(acc_dir, exist_ok=True)

    # 1. Profile Metadata
    meta = {
        "profile_id": acc["id"],
        "account_name": acc["name"],
        "owner": acc["owner"],
        "region": acc["region"],
        "timezone_id": acc["timezone"],
        "device_model": acc["device"],
        "cookies_ready": os.path.exists(os.path.join(acc_dir, "cookies.json")) and os.path.getsize(os.path.join(acc_dir, "cookies.json")) > 20
    }
    with open(os.path.join(acc_dir, "profile_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # 2. Extract and save Pages
    pages = []
    if "source_file" in acc:
        src_path = os.path.join(BASE_DIR, acc["source_file"])
        if os.path.exists(src_path):
            try:
                with open(src_path, "r", encoding="utf-8") as sf:
                    sdata = json.load(sf)
                    if isinstance(sdata, list):
                        pages = sdata
                    elif isinstance(sdata, dict):
                        pages = sdata.get("pages", [])
            except Exception as e:
                print(f"Error reading {src_path}: {e}")
    elif "source_fleet" in acc:
        parsed_f = json.load(open("temp/parsed_fleets.json", encoding="utf-8"))
        pages = parsed_f.get(acc["source_fleet"], [])

    with open(os.path.join(acc_dir, "pages.json"), "w", encoding="utf-8") as pf:
        json.dump({"account": acc["name"], "count": len(pages), "pages": pages}, pf, indent=2)

    # 3. Create placeholder cookies.json if not present
    ck_path = os.path.join(acc_dir, "cookies.json")
    if not os.path.exists(ck_path):
        with open(ck_path, "w", encoding="utf-8") as cf:
            json.dump([], cf, indent=2)

    print(f"✅ Prepared Profile Slot: {acc['id']} ({acc['name']}) -> {len(pages)} Pages mapped.")
    created_count += 1

print(f"\nTotal Account Slots Ready in data/profiles/: {created_count}")
