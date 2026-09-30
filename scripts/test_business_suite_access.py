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

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Dest": "document"
}

for f in files:
    fname = os.path.basename(f)
    with open(f, "r", encoding="utf-8") as fp:
        cookie_json = json.load(fp)

    cookie_dict = {c["name"]: c["value"] for c in cookie_json if "name" in c and "value" in c}
    cookie_str = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
    
    req_headers = dict(headers)
    req_headers["Cookie"] = cookie_str

    req = urllib.request.Request("https://business.facebook.com/latest/home", headers=req_headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            final_url = resp.geturl()
            html = resp.read().decode("utf-8", errors="ignore")
            # Extract asset IDs or page IDs from html
            page_ids = set(re.findall(r'"page_id":"(\d+)"', html))
            asset_ids = set(re.findall(r'asset_id=(\d+)', html))
            all_ids = page_ids.union(asset_ids)
            print(f"[{fname}] Suite URL: {final_url[:40]} | Found IDs in HTML: {len(all_ids)} | Sample: {list(all_ids)[:3]}")
    except Exception as e:
        print(f"[{fname}] Suite ERROR: {e}")
