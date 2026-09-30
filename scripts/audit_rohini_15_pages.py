import sys
import os
import json
import time
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright

raw_cookies = json.load(open("data/profiles/samsung_s25_newyork/cookies.json", encoding="utf-8"))
playwright_cookies = []
for c in raw_cookies:
    pc = {
        "name": c["name"],
        "value": c["value"],
        "domain": c.get("domain", ".facebook.com"),
        "path": c.get("path", "/"),
        "secure": True
    }
    if "expirationDate" in c:
        pc["expires"] = float(c["expirationDate"])
    playwright_cookies.append(pc)

with open("temp/discovered_page_ids.json", "r", encoding="utf-8") as f:
    page_ids = json.load(f)

print(f"Loaded {len(page_ids)} pages for monetization audit.")

audit_results = []
os.makedirs("temp/audit_debug/pages", exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        viewport={"width": 1440, "height": 900},
        locale="en-US"
    )
    ctx.add_cookies(playwright_cookies)
    page = ctx.new_page()

    for idx, (name, pid) in enumerate(page_ids.items(), 1):
        print(f"\n[{idx}/15] Auditing Page: {name} (ID: {pid})...")
        res = {
            "index": idx,
            "page_name": name,
            "page_id": pid,
            "overall_status": "Unknown",
            "content_monetization": "Unknown",
            "subscriptions": "Unknown",
            "stars": "Unknown",
            "policy_details": "None",
            "recommendation": "Checking..."
        }

        try:
            # 1. Monetization Main Page
            monetize_url = f"https://business.facebook.com/latest/monetization?asset_id={pid}"
            page.goto(monetize_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)

            body_text = page.inner_text("body")
            if "No Monetization Violations" in body_text:
                res["overall_status"] = "No Monetization Violations"
            elif "Monetization Violations" in body_text:
                res["overall_status"] = "Has Policy Violations"
            else:
                res["overall_status"] = "Review Required"

            # 2. Click "View Page Eligibility" to open modal
            btn = page.locator('text="View Page Eligibility"').first
            if btn.count() > 0:
                btn.click()
                time.sleep(3)
                dialog = page.locator('div[role="dialog"]')
                if dialog.count() > 0:
                    d_text = dialog.first.inner_text()
                    # Check Content Monetization
                    if "Content Monetization" in d_text:
                        cm_section = d_text[d_text.find("Content Monetization"):d_text.find("Content Monetization") + 250]
                        if "Policy Issues" in cm_section:
                            res["content_monetization"] = "Policy Issues"
                        elif "Available to set up" in cm_section or "Set up" in cm_section:
                            res["content_monetization"] = "Available to Set Up"
                        elif "In review" in cm_section:
                            res["content_monetization"] = "In Review"
                        elif "Criteria Not Met" in cm_section:
                            res["content_monetization"] = "Criteria Not Met"
                        else:
                            res["content_monetization"] = "Not Eligible"

                    # Check Subscriptions
                    if "Subscriptions" in d_text:
                        sub_section = d_text[d_text.find("Subscriptions"):d_text.find("Subscriptions") + 250]
                        if "Set up" in sub_section or "Get started" in sub_section:
                            res["subscriptions"] = "Available to Set Up"
                        elif "Criteria Not Met" in sub_section:
                            res["subscriptions"] = "Criteria Not Met"
                        else:
                            res["subscriptions"] = "Not Yet Eligible"

                    # Check Stars
                    if "Stars" in d_text:
                        stars_section = d_text[d_text.find("Stars"):d_text.find("Stars") + 250]
                        if "Set up" in stars_section or "Get started" in stars_section:
                            res["stars"] = "Available to Set Up"
                        elif "Criteria Not Met" in stars_section:
                            res["stars"] = "Criteria Not Met"
                        else:
                            res["stars"] = "Not Yet Eligible"

                    # Close modal
                    close_btn = dialog.locator('button[aria-label="Close"], i[aria-label="Close"], [role="button"]:has-text("✕")')
                    if close_btn.count() > 0:
                        close_btn.first.click()
                    else:
                        page.keyboard.press("Escape")
                    time.sleep(1)

            # 3. Policy Issues Tab
            policy_url = f"https://business.facebook.com/latest/monetization/policy_issues?asset_id={pid}"
            page.goto(policy_url, wait_until="domcontentloaded", timeout=25000)
            time.sleep(4)
            p_text = page.inner_text("body")
            if "No Monetization Violations" in p_text or "no recent monetization violations" in p_text.lower():
                res["policy_details"] = "No Violations (Clean)"
            elif "limited originality of content" in p_text.lower():
                res["policy_details"] = "Limited Originality of Content (LOC)"
            elif "unoriginal content" in p_text.lower():
                res["policy_details"] = "Unoriginal Content"
            elif "violations" in p_text.lower():
                res["policy_details"] = "Partner Policy Issues Detected"
            else:
                res["policy_details"] = "Clean / In Good Standing"

            # Screenshot
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
            page.screenshot(path=f"temp/audit_debug/pages/{clean_name}.png")

            print(f"  -> Overall: {res['overall_status']} | Content Monetization: {res['content_monetization']} | Subscriptions: {res['subscriptions']} | Stars: {res['stars']} | Policy: {res['policy_details']}")

        except Exception as e:
            print(f"  [ERROR] {name}: {e}")
            res["overall_status"] = f"Error: {e}"

        audit_results.append(res)

    browser.close()

with open("temp/rohini_15_pages_monetization_audit.json", "w", encoding="utf-8") as f:
    json.dump(audit_results, f, indent=2)

print("\n=======================================================")
print("✅ ALL 15 PAGES MONETIZATION AUDIT COMPLETE!")
print("Saved to temp/rohini_15_pages_monetization_audit.json")
print("=======================================================")
