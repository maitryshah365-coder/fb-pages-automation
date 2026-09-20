import requests
import json
import os

user_token = "EAAk7kW6ymkIBSqM4IZAhZApbuZCh4u8sWv33iiuiF5MUMrhsNq0wgGjTq9kTAiQXoGyAcpIGgh61HUyjKcqblBIZBdOuLASh8Tcjb9e0nwkKDxEulvheAdX26ZCSUrxVZAWTw2PxuhI0ZClgTkZCrnVZAoFIwRyrcQg60gXw7SZBt4sZBR13OLFT4YzkoZCsVbtz"
app_secret = "e6f996108e23ff91cb5247b86982ef44"

print("--- 1. Testing User Token ---")
r_me = requests.get(f"https://graph.facebook.com/v19.0/me?fields=id,name&access_token={user_token}")
print("ME:", r_me.status_code, r_me.text)

print("\n--- 2. Getting App ID ---")
r_app = requests.get(f"https://graph.facebook.com/v19.0/app?access_token={user_token}")
print("APP:", r_app.status_code, r_app.text)
app_id = r_app.json().get("id")

print("\n--- 3. Exchanging for Long-Lived User Token ---")
if app_id:
    exchange_url = "https://graph.facebook.com/v19.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": user_token
    }
    r_ex = requests.get(exchange_url, params=params)
    print("Exchange Status:", r_ex.status_code, r_ex.text)
    if r_ex.status_code == 200:
        long_lived_token = r_ex.json().get("access_token")
        print("Obtained Long-Lived User Token!")
        user_token = long_lived_token

print("\n--- 4. Fetching Pages with Permanent Tokens ---")
r_pages = requests.get(f"https://graph.facebook.com/v19.0/me/accounts?fields=id,name,access_token,category,tasks,fan_count,followers_count&limit=100&access_token={user_token}")
print("PAGES STATUS:", r_pages.status_code)
pages_data = r_pages.json()
pages = pages_data.get("data", [])
print(f"Total Pages Found: {len(pages)}")
for idx, p in enumerate(pages, 1):
    print(f"  {idx}. {p.get('name')} (ID: {p.get('id')})")

with open("data/uk_account6_sweta_pages.json", "w", encoding="utf-8") as f:
    json.dump(pages_data, f, indent=2)

with open("data/uk_account6_sweta_permanent_pages.json", "w", encoding="utf-8") as f:
    json.dump(pages, f, indent=2)

print("\nSaved pages to data/uk_account6_sweta_pages.json & permanent_pages.json")
