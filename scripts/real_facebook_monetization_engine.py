import sys
import os
import json
import time
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright

BASE_DIR = r"E:\Anty Working\Google_Drive_to_Facebook_Automation_Master_Spec"
MASTER_JSON_PATHS = [
    os.path.join(BASE_DIR, "data", "master_fleet_monetization.json"),
    os.path.join(BASE_DIR, "docs", "data", "master_fleet_monetization.json"),
    os.path.join(BASE_DIR, "web", "data", "master_fleet_monetization.json")
]

def load_master_data():
    primary_path = MASTER_JSON_PATHS[0]
    if os.path.exists(primary_path):
        with open(primary_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"total_accounts": 12, "total_fleet_pages": 158, "accounts": []}

def save_master_data(data):
    data["last_live_audit_at"] = datetime.now(timezone.utc).isoformat()
    for p in MASTER_JSON_PATHS:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    print(f"  [SAVED] Master fleet data synced to all 3 paths.")

def parse_cookies_for_playwright(ck_path):
    if not os.path.exists(ck_path):
        return None
    with open(ck_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    pw_cookies = []
    for c in raw:
        if isinstance(c, dict) and "name" in c and "value" in c:
            pc = {
                "name": str(c["name"]),
                "value": str(c["value"]),
                "domain": c.get("domain", ".facebook.com"),
                "path": c.get("path", "/"),
                "secure": True
            }
            if "expirationDate" in c:
                pc["expires"] = float(c["expirationDate"])
            pw_cookies.append(pc)
    return pw_cookies

def audit_single_page_live(page, pid, pname):
    url = f"https://business.facebook.com/latest/monetization/monetization_home/monetization_home_main/?asset_id={pid}"
    print(f"    --> Loading [{pname}] ({pid})...")
    
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=35000)
    except Exception as e:
        print(f"        Navigation warning: {e}")
        return None

    time.sleep(4)

    # 1. Overall Policy Status from Screen
    body_text = page.locator("body").inner_text()
    
    overall_status = "No Monetization Violations"
    if "Monetization issue" in body_text or "Policy violation" in body_text or "Restricted" in body_text:
        overall_status = "Policy Issues"
    elif "No Monetization Violations" in body_text:
        overall_status = "No Monetization Violations"

    # 2. Main screen "Programs to set up"
    programs_setup = []
    if "Programs to set up" in body_text:
        try:
            setup_section = body_text.split("Programs to set up")[1].split("Meta Business Suite")[0]
            if "Subscriptions" in setup_section:
                programs_setup.append("Subscriptions")
            if "Stars" in setup_section:
                programs_setup.append("Stars")
            if "Content Monetization" in setup_section:
                programs_setup.append("Content Monetization")
        except Exception:
            pass

    # 3. Open "View Page Eligibility" drawer
    eligibility_drawer_opened = False
    btn = page.locator("text='View Page Eligibility'").first
    if btn.is_visible():
        try:
            btn.click()
            time.sleep(3)
            eligibility_drawer_opened = True
        except Exception:
            pass

    content_mon_status = "Policy Issues"
    subs_status = "Criteria Not Met"
    stars_status = "Criteria Not Met"

    if eligibility_drawer_opened:
        drawer_text = page.locator("body").inner_text()
        
        # Content Monetization in drawer
        if "Content Monetization" in drawer_text:
            cm_part = drawer_text.split("Content Monetization")[1][:250]
            if "Criteria Not Met" in cm_part:
                content_mon_status = "Criteria Not Met"
            elif "Available to set up" in cm_part or "Set up" in cm_part:
                content_mon_status = "Set Up"
            elif "Waitlist" in cm_part:
                content_mon_status = "Waitlist criteria▼"

        # Subscriptions in drawer
        if "Subscriptions" in drawer_text:
            sub_part = drawer_text.split("Subscriptions")[1][:250]
            if "Set Up" in sub_part or "Available to set up" in sub_part:
                subs_status = "Set Up"
            elif "Criteria Not Met" in sub_part:
                subs_status = "Criteria Not Met"
            elif "Not Found" in sub_part:
                subs_status = "Not Found"

        # Check if Subscriptions was in Programs to set up on main card
        if "Subscriptions" in programs_setup:
            subs_status = "Set Up"

        if "Stars" in programs_setup:
            stars_status = "Set Up"
    else:
        if "Subscriptions" in programs_setup:
            subs_status = "Set Up"
        if "Stars" in programs_setup:
            stars_status = "Set Up"

    result = {
        "overall_status": overall_status,
        "content_monetization": content_mon_status,
        "subscriptions": subs_status,
        "stars": stars_status,
        "policy_details": "No Violations (Clean)" if "No Monetization" in overall_status else "Issues Detected",
        "recommendation": "Recommendable",
        "verified_live": True,
        "verified_at": datetime.now(timezone.utc).isoformat()
    }
    print(f"        [RESULT] Policy: {overall_status} | CM: {content_mon_status} | Subs: {subs_status} | Stars: {stars_status}")
    return result

def audit_account_fleet(account_id, max_pages=None, target_page_id=None, progress_callback=None):
    master_data = load_master_data()
    acc_entry = next((a for a in master_data.get("accounts", []) if a["account_id"] == account_id), None)
    if not acc_entry:
        print(f"Account {account_id} not found in master data.")
        return

    ck_path = os.path.join(BASE_DIR, "data", "profiles", account_id, "cookies.json")
    pw_cookies = parse_cookies_for_playwright(ck_path)
    if not pw_cookies:
        print(f"No cookies found for {account_id}.")
        return

    print(f"\n=======================================================")
    print(f"🚀 RUNNING REAL FACEBOOK AUDIT FOR: {acc_entry.get('account_name', account_id)}")
    print(f"=======================================================")

    pages = acc_entry.get("pages", [])
    if target_page_id:
        pages = [p for p in pages if str(p.get("page_id", "")) == str(target_page_id)]
    elif max_pages:
        pages = pages[:max_pages]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900}
        )
        ctx.add_cookies(pw_cookies)
        page = ctx.new_page()

        # Step 1: Warmup & verify session
        print("  --> Checking session with Facebook...")
        page.goto("https://www.facebook.com/", wait_until="domcontentloaded", timeout=25000)
        time.sleep(3)
        if "login" in page.url.lower() or "checkpoint" in page.url.lower():
            print("  ❌ Session expired or checkpoint redirect!")
            browser.close()
            return

        print("  ✅ Session verified active! Auditing pages...")
        for idx, page_item in enumerate(pages, 1):
            pid = str(page_item.get("page_id", ""))
            pname = page_item.get("name", f"Page {idx}")
            if not pid or not pid.isdigit():
                continue

            if progress_callback:
                progress_callback(idx, len(pages), pname, pid)

            audit_res = audit_single_page_live(page, pid, pname)
            if audit_res:
                page_item.update(audit_res)
                # Save after each page to preserve progress immediately
                save_master_data(master_data)

        browser.close()

    print(f"\n✅ Audit complete for {account_id}!")

if __name__ == "__main__":
    target_acc = sys.argv[1] if len(sys.argv) > 1 else "usa_account1_meghal"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    audit_account_fleet(target_acc, limit)
