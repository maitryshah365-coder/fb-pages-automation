import os
import sys
import json
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

APP_ID = "1797734997908147"
APP_SECRET = "ad6f2a1b6c6f7785c5f64491091db7dd"
USER_TOKEN = "EAAZAjB8vzWrMBSo3trv5FRZB5OUMsh6O1ieSnkMNt7ZAcUCmZANmZA4ZBrd88ZCxqEuAeOCkz1xapZBSmCTG99ZA2rZAZAYC22pUUwkPIOf7frr19kBOOpZA1qi6ZAOhLQpQlG3lOOg22HyxWGs0svu86x9e4D2iQMnCLPMEZAZBBk4IyvZA0IBqUZCSZAjeX9iYu2tEoK08NtcuPgU7GoSQJZArxTg"
DRIVE_PARENT_ID = "1wOPsQkTcLI-YFuGSdbf-jkp1U8txnuAf"

print("--- Step 1: Debugging User Token ---")
app_token = f"{APP_ID}|{APP_SECRET}"
dbg_url = f"https://graph.facebook.com/v20.0/debug_token?input_token={USER_TOKEN}&access_token={app_token}"
dbg = requests.get(dbg_url).json()
print("Debug Token:", json.dumps(dbg, indent=2))

print("\n--- Step 2: Exchanging for Long-Lived Token ---")
exch_url = f"https://graph.facebook.com/v20.0/oauth/access_token?grant_type=fb_exchange_token&client_id={APP_ID}&client_secret={APP_SECRET}&fb_exchange_token={USER_TOKEN}"
exch = requests.get(exch_url).json()
print("Exchange Response:", json.dumps(exch, indent=2))
long_token = exch.get("access_token", USER_TOKEN)

print("\n--- Step 3: Getting User Profile ---")
me = requests.get(f"https://graph.facebook.com/v20.0/me?access_token={long_token}").json()
print("User Profile:", json.dumps(me, indent=2))

print("\n--- Step 4: Fetching Managed Pages ---")
accs_url = f"https://graph.facebook.com/v20.0/me/accounts?fields=id,name,access_token,category,followers_count,fan_count,picture.type(large)&limit=100&access_token={long_token}"
accs = requests.get(accs_url).json()
pages = accs.get("data", [])
print(f"Total Pages Found: {len(pages)}")

output_pages = []
for p in pages:
    pid = p.get("id")
    pname = p.get("name")
    ptoken = p.get("access_token")
    followers = p.get("followers_count", 0)
    pic_url = p.get("picture", {}).get("data", {}).get("url", "")
    output_pages.append({
        "id": pid,
        "name": pname,
        "access_token": ptoken,
        "followers_count": followers,
        "picture_url": pic_url
    })
    print(f"[{pid}] {pname} (Followers: {followers})")

os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
with open(os.path.join(BASE_DIR, "data", "uk_account5_richi_pages.json"), "w", encoding="utf-8") as f:
    json.dump(output_pages, f, indent=2)

print("\nSaved pages to data/uk_account5_richi_pages.json")
