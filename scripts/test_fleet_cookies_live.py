import os
import sys
import glob
import json
import urllib.request
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

cookie_dir = r"C:\Users\Win\Desktop\Cookis"
files = sorted(glob.glob(os.path.join(cookie_dir, "*.txt")))

print(f"Found {len(files)} cookie files in {cookie_dir}\n")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}

results = []

for f in files:
    fname = os.path.basename(f)
    try:
        with open(f, "r", encoding="utf-8") as fp:
            cookie_json = json.load(fp)
    except Exception as e:
        print(f"[-] {fname}: Failed to parse JSON: {e}")
        continue

    cookie_dict = {}
    c_user = None
    xs = None
    for c in cookie_json:
        name = c.get("name")
        val = c.get("value")
        if name:
            cookie_dict[name] = val
        if name == "c_user": c_user = val
        if name == "xs": xs = val

    cookie_str = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
    req_headers = dict(headers)
    req_headers["Cookie"] = cookie_str

    req = urllib.request.Request("https://mbasic.facebook.com/me", headers=req_headers)
    status = "UNKNOWN"
    profile_name = "N/A"
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            final_url = resp.geturl()
            html = resp.read().decode("utf-8", errors="ignore")
            if "checkpoint" in final_url or "checkpoint" in html:
                status = "CHECKPOINT_LOCKED"
            elif "login" in final_url or "/login.php" in html:
                status = "EXPIRED / LOGGED_OUT"
            else:
                status = "LIVE_ACTIVE"
                # try extract name
                title_match = re.search(r"<title>(.*?)</title>", html, re.I)
                if title_match:
                    profile_name = title_match.group(1).replace(" | Facebook", "").strip()
    except Exception as e:
        status = f"HTTP_ERROR: {e}"

    res_item = {
        "file": fname,
        "c_user": c_user,
        "status": status,
        "detected_profile_name": profile_name,
        "total_cookies": len(cookie_json)
    }
    results.append(res_item)
    print(f"[{res_item['status']:<15}] {fname:<25} | UID: {c_user:<16} | Name: {profile_name}")

print("\n--- Summary ---")
live_count = sum(1 for r in results if r["status"] == "LIVE_ACTIVE")
print(f"Live Active: {live_count} / {len(results)}")
