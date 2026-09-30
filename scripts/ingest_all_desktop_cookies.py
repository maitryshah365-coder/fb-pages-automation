import os
import sys
import glob
import json
import shutil

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = r"E:\Anty Working\Google_Drive_to_Facebook_Automation_Master_Spec"
PROFILES_DIR = os.path.join(BASE_DIR, "data", "profiles")
DESKTOP_COOKIES = r"C:\Users\Win\Desktop\Cookis"

# Load pages_tokens.json for USA 1 and USA 2
with open(os.path.join(BASE_DIR, "data", "pages_tokens.json"), "r", encoding="utf-8") as f:
    pt_pages = json.load(f)

usa1_pages = [{"page_id": str(p["id"]), "name": p["name"], "folder": p["name"]} for p in pt_pages if p.get("account") == "Account 1"]
usa2_pages = [{"page_id": str(p["id"]), "name": p["name"], "folder": p["name"]} for p in pt_pages if p.get("account") == "Account 2"]

def load_pages(fpath):
    full_p = os.path.join(BASE_DIR, fpath)
    if not os.path.exists(full_p): return []
    with open(full_p, "r", encoding="utf-8") as f:
        d = json.load(f)
    items = d if isinstance(d, list) else d.get("pages", [])
    out = []
    for it in items:
        pid = it.get("page_id") or it.get("id") or it.get("pageId")
        pname = it.get("name") or it.get("page_name") or it.get("title") or it.get("folder")
        folder = it.get("folder") or pname
        if pid or pname:
            out.append({"page_id": str(pid) if pid else "", "name": pname or "", "folder": folder or ""})
    return out

ACCOUNTS = [
    {
        "id": "samsung_s25_newyork",
        "name": "Rohini Dutt (USA 4)",
        "owner": "Rohini Dutt",
        "region": "US",
        "timezone": "America/New_York",
        "device": "Samsung Galaxy S25 (SM-S931U)",
        "cookie_file": None, # Already exists
        "pages_file": "data/profiles/samsung_s25_newyork/pages.json"
    },
    {
        "id": "usa_account1_meghal",
        "name": "Meghal Chauhan (USA 1)",
        "owner": "Meghal Chauhan",
        "region": "US",
        "timezone": "America/New_York",
        "device": "Samsung Galaxy S25 (US 5G)",
        "cookie_file": os.path.join(DESKTOP_COOKIES, "Meghal Chauhan (USA).txt"),
        "pages": usa1_pages
    },
    {
        "id": "usa_account2_mia",
        "name": "Mia Shah (USA 2)",
        "owner": "Mia Shah",
        "region": "US",
        "timezone": "America/New_York",
        "device": "Samsung Galaxy S25 (US 5G)",
        "cookie_file": os.path.join(DESKTOP_COOKIES, "Mia Shah (USA).txt"),
        "pages": usa2_pages
    },
    {
        "id": "usa_account3_radika",
        "name": "Radika Patel (USA 3)",
        "owner": "Radika Patel",
        "region": "US",
        "timezone": "America/New_York",
        "device": "Samsung Galaxy S25 (US 5G)",
        "cookie_file": os.path.join(DESKTOP_COOKIES, "Radika Patel (USA).txt"),
        "pages_file": "data/usa_account3_radika_permanent_pages.json"
    },
    {
        "id": "uk_account1_binjal",
        "name": "Binjal Mehra (UK 1)",
        "owner": "Binjal Mehra",
        "region": "UK",
        "timezone": "Europe/London",
        "device": "Samsung Galaxy S24 Ultra (UK 5G)",
        "cookie_file": os.path.join(DESKTOP_COOKIES, "Binjal Mehra (UK).txt"),
        "pages_file": "data/uk_account1_binjal_pages.json"
    },
    {
        "id": "uk_account2_chanda",
        "name": "Chanda Nai (UK 2)",
        "owner": "Chanda Nai",
        "region": "UK",
        "timezone": "Europe/London",
        "device": "Google Pixel 9 Pro (UK)",
        "cookie_file": os.path.join(DESKTOP_COOKIES, "Chanda Nai (UK).txt"),
        "pages_file": "data/uk_account2_chanda_pages.json"
    },
    {
        "id": "uk_account3_mahi",
        "name": "Mahi Patel (UK 3)",
        "owner": "Mahi Patel",
        "region": "UK",
        "timezone": "Europe/London",
        "device": "Samsung Galaxy S25 (UK)",
        "cookie_file": os.path.join(DESKTOP_COOKIES, "Mahi Patel (UK).txt"),
        "pages_file": "data/uk_account3_mahi_pages.json"
    },
    {
        "id": "uk_account4_nidhi",
        "name": "Nidhi Desai (UK 4)",
        "owner": "Nidhi Desai",
        "region": "UK",
        "timezone": "Europe/London",
        "device": "Samsung Galaxy S25 (UK)",
        "cookie_file": os.path.join(DESKTOP_COOKIES, "Nidhi Desai (UK).txt"),
        "pages_file": "data/uk_account4_nidhi_pages.json"
    },
    {
        "id": "uk_account5_richi",
        "name": "Richi Patel (UK 5)",
        "owner": "Richi Patel",
        "region": "UK",
        "timezone": "Europe/London",
        "device": "Google Pixel 9 (UK)",
        "cookie_file": os.path.join(DESKTOP_COOKIES, "Richi Patel  )UK).txt"),
        "pages_file": "data/uk_account5_richi_pages.json"
    },
    {
        "id": "uk_account6_sweta",
        "name": "Sweta Shah (UK 6)",
        "owner": "Sweta Shah",
        "region": "UK",
        "timezone": "Europe/London",
        "device": "Samsung Galaxy S24 (UK)",
        "cookie_file": os.path.join(DESKTOP_COOKIES, "Sweta Shah (UK).txt"),
        "pages_file": "data/uk_account6_sweta_permanent_pages.json"
    },
    {
        "id": "uk_account7_riya",
        "name": "Riya (UK 7)",
        "owner": "Riya",
        "region": "UK",
        "timezone": "Europe/London",
        "device": "OnePlus 13 (UK)",
        "cookie_file": None, # Missing from desktop
        "pages_file": "data/uk_account7_riya_permanent_pages.json"
    }
]

print("Setting up all 11 account profiles...")
for acc in ACCOUNTS:
    acc_dir = os.path.join(PROFILES_DIR, acc["id"])
    os.makedirs(acc_dir, exist_ok=True)
    
    # Copy cookie if provided
    has_cookies = False
    c_user = None
    if acc["cookie_file"] and os.path.exists(acc["cookie_file"]):
        with open(acc["cookie_file"], "r", encoding="utf-8") as f:
            cdata = json.load(f)
        dest_cookie = os.path.join(acc_dir, "cookies.json")
        with open(dest_cookie, "w", encoding="utf-8") as f:
            json.dump(cdata, f, indent=2)
        has_cookies = True
        for c in cdata:
            if c.get("name") == "c_user":
                c_user = c.get("value")
    elif acc["id"] == "samsung_s25_newyork":
        dest_cookie = os.path.join(acc_dir, "cookies.json")
        if os.path.exists(dest_cookie):
            has_cookies = True
            with open(dest_cookie, "r", encoding="utf-8") as f:
                cdata = json.load(f)
            for c in cdata:
                if c.get("name") == "c_user":
                    c_user = c.get("value")

    # Load pages
    if "pages" in acc:
        pages = acc["pages"]
    elif "pages_file" in acc:
        pages = load_pages(acc["pages_file"])
    else:
        pages = []

    pages_dest = os.path.join(acc_dir, "pages.json")
    with open(pages_dest, "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=2)

    meta = {
        "id": acc["id"],
        "name": acc["name"],
        "owner": acc["owner"],
        "region": acc["region"],
        "timezone": acc["timezone"],
        "device": acc["device"],
        "status": "ACTIVE_AUTHENTICATED" if has_cookies else "AWAITING_COOKIES",
        "fb_uid": c_user,
        "total_pages": len(pages),
        "cookies_present": has_cookies
    }
    with open(os.path.join(acc_dir, "profile_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"[{'LIVE' if has_cookies else 'QUEUED':<6}] {acc['name']:<25} | UID: {str(c_user):<16} | Pages: {len(pages)}")

print("\nDone setting up all account profile vaults!")
