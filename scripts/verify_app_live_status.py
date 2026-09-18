import json
import os
import requests
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def check_app_live_status(app_id: str, app_secret: str = None):
    print(f"\n==========================================")
    print(f"🔍 AUDITING META APP ID: {app_id}")
    print(f"==========================================")
    
    # 1. Unauthenticated Public Check (Tests if app is live to outside world)
    try:
        pub_res = requests.get(f"https://graph.facebook.com/v20.0/{app_id}").json()
        if "error" in pub_res:
            err = pub_res["error"]
            print(f"❌ PUBLIC VISIBILITY ERROR: {err.get('message')} (Code: {err.get('code')})")
            if err.get('code') == 200 or 'development' in err.get('message', '').lower():
                print("🚨 CRITICAL WARNING: App is in 'DEVELOPMENT MODE'. Reels will have 0 public views!")
        else:
            print(f"✅ App is publicly indexed on Meta:")
            print(f"   - Name: {pub_res.get('name')}")
            print(f"   - Category: {pub_res.get('category')}")
            print(f"   - Link: {pub_res.get('link')}")
    except Exception as e:
        print(f"❌ Public check failed: {e}")

    # 2. Authenticated Deep Check (if app_secret available)
    if app_secret:
        app_token = f"{app_id}|{app_secret}"
        try:
            fields = "id,name,link,privacy_policy_url,category,roles"
            auth_res = requests.get(f"https://graph.facebook.com/v20.0/{app_id}?access_token={app_token}&fields={fields}").json()
            if "error" in auth_res:
                print(f"❌ AUTHENTICATED CHECK ERROR: {auth_res['error'].get('message')}")
            else:
                priv = auth_res.get("privacy_policy_url")
                print(f"\n📋 MANDATORY SETTINGS AUDIT:")
                print(f"   - Privacy Policy URL: {priv} {'✅ OK' if priv and 'privacy.html' in priv or 'fb-pages-automation' in str(priv) else '⚠️ CHECK REQUIRED'}")
                print(f"   - Category: {auth_res.get('category', 'Not Set')} ✅")
        except Exception as e:
            print(f"❌ Authenticated check failed: {e}")

if __name__ == "__main__":
    # Check UK Account 1
    uk_path = os.path.join(BASE_DIR, "data", "uk_account1_binjal_permanent_pages.json")
    if os.path.exists(uk_path):
        with open(uk_path, "r", encoding="utf-8") as f:
            uk_data = json.load(f)
        if isinstance(uk_data, dict) and "app_id" in uk_data:
            check_app_live_status(uk_data["app_id"], uk_data.get("app_secret"))
