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
    "Accept-Language": "en-US,en;q=0.9"
}

for f in files:
    fname = os.path.basename(f)
    with open(f, "r", encoding="utf-8") as fp:
        cookie_json = json.load(fp)

    cookie_dict = {c["name"]: c["value"] for c in cookie_json if "name" in c and "value" in c}
    cookie_str = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
    c_user = cookie_dict.get("c_user", "")

    req_headers = dict(headers)
    req_headers["Cookie"] = cookie_str

    req = urllib.request.Request("https://www.facebook.com/", headers=req_headers)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            # Look for NAME
            # e.g., "NAME":"..." or "user":{"name":"..."}
            names = re.findall(r'"NAME":"([^"]+)"', html)
            account_names = re.findall(r'"ACCOUNT_NAME":"([^"]+)"', html)
            short_names = re.findall(r'"SHORT_NAME":"([^"]+)"', html)
            
            # Check for access token EAAB or EAAG
            eaab_tokens = re.findall(r'"(EAAB[a-zA-Z0-9]+)"', html)
            eaag_tokens = re.findall(r'"(EAAG[a-zA-Z0-9]+)"', html)
            
            print(f"[{fname}] UID: {c_user} | Names: {names[:2]} | ShortNames: {short_names[:2]} | Tokens: {len(eaab_tokens) + len(eaag_tokens)}")
    except Exception as e:
        print(f"[{fname}] Err: {e}")
