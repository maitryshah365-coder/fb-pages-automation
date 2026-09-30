import os
import sys
import glob
import json
import urllib.request
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = r"E:\Anty Working\Google_Drive_to_Facebook_Automation_Master_Spec"
PROFILES_DIR = os.path.join(BASE_DIR, "data", "profiles")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}

# Test 1 page from each active account
profiles = [d for d in os.listdir(PROFILES_DIR) if os.path.isdir(os.path.join(PROFILES_DIR, d))]

for pid in sorted(profiles):
    pdir = os.path.join(PROFILES_DIR, pid)
    cookie_path = os.path.join(pdir, "cookies.json")
    pages_path = os.path.join(pdir, "pages.json")
    if not os.path.exists(cookie_path) or not os.path.exists(pages_path):
        continue

    with open(cookie_path, "r", encoding="utf-8") as f:
        cookie_json = json.load(f)
    with open(pages_path, "r", encoding="utf-8") as f:
        pages = json.load(f)

    if not pages:
        continue

    sample_page = pages[0]
    page_id = sample_page.get("page_id")
    page_name = sample_page.get("name")

    if not page_id:
        continue

    cookie_dict = {c["name"]: c["value"] for c in cookie_json if "name" in c and "value" in c}
    cookie_str = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])

    req_headers = dict(headers)
    req_headers["Cookie"] = cookie_str

    url = f"https://business.facebook.com/latest/monetization/tools?asset_id={page_id}"
    req = urllib.request.Request(url, headers=req_headers)

    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            has_no_violations = "No Monetization Violations" in html or "no monetization violations" in html.lower()
            has_content_mon = "Content Monetization" in html
            has_subs = "Subscriptions" in html
            has_stars = "Stars" in html
            has_policy_issues = "Policy Issues" in html
            has_set_up = "Set Up" in html or "Get Started" in html
            
            print(f"[{pid:<22}] Page: {page_name:<20} (ID: {page_id}) | Clean: {has_no_violations} | ContentMon: {has_content_mon} | PolicyIssues: {has_policy_issues} | SetUp: {has_set_up}")
    except Exception as e:
        print(f"[{pid:<22}] Page: {page_name:<20} | ERROR: {e}")
