import json
import os
import requests
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APP_REGISTRY = [
    {
        "account": "USA Account 1",
        "owner": "Account 1 Admin",
        "app_id": "1366459798891922",
        "app_secret": None
    },
    {
        "account": "UK Account 1",
        "owner": "Binjal Mehra",
        "app_id": "862294890211778",
        "app_secret": "0144023bc1641732366249cf4ef97c3d"
    },
    {
        "account": "UK Account 2",
        "owner": "Chanda Nai",
        "app_id": "1451479893170026",
        "app_secret": "5281e76f4d91680f2791fbabbb5194a3"
    },
    {
        "account": "UK Account 3",
        "owner": "Mahi Patel",
        "app_id": "2816581568717007",
        "app_secret": None
    }
]

EXPECTED_DOMAIN = "maitryshah365-coder.github.io"
EXPECTED_PRIVACY = "https://maitryshah365-coder.github.io/fb-pages-automation/privacy.html"
EXPECTED_DELETION = "https://maitryshah365-coder.github.io/fb-pages-automation/data-deletion.html"
EXPECTED_SITE_URL = "https://maitryshah365-coder.github.io/fb-pages-automation/"

def audit_app(app_info: dict):
    acc = app_info["account"]
    owner = app_info["owner"]
    app_id = app_info["app_id"]
    secret = app_info.get("app_secret")

    print(f"\n=======================================================")
    print(f"🔍 AUDITING META DEVELOPER APP: {acc} ({owner})")
    print(f"   App ID: {app_id}")
    print(f"=======================================================")

    # 1. Unauthenticated Public Check (Tests if app is live to outside world)
    is_live = False
    try:
        pub_res = requests.get(f"https://graph.facebook.com/v20.0/{app_id}", timeout=10).json()
        if "error" in pub_res:
            err = pub_res["error"]
            print(f"❌ PUBLIC VISIBILITY ERROR: {err.get('message')} (Code: {err.get('code')})")
            if err.get('code') == 200 or 'development' in err.get('message', '').lower():
                print("🚨 CRITICAL WARNING: App is in 'DEVELOPMENT MODE'. Reels will have 0 public views!")
            else:
                print(f"⚠️ App query returned error: {err}")
        else:
            is_live = True
            print(f"✅ APP IS IN LIVE MODE (Publicly Indexed on Meta):")
            print(f"   - App Name: {pub_res.get('name')}")
            print(f"   - Category: {pub_res.get('category')}")
            print(f"   - Site Link: {pub_res.get('link')}")
    except Exception as e:
        print(f"❌ Public check network failure: {e}")

    # 2. Authenticated Deep Check (if app_secret available)
    if secret:
        app_token = f"{app_id}|{secret}"
        try:
            fields = "id,name,link,privacy_policy_url,category"
            auth_res = requests.get(f"https://graph.facebook.com/v20.0/{app_id}?access_token={app_token}&fields={fields}", timeout=10).json()
            if "error" in auth_res:
                print(f"ℹ️ Deep settings check response: {auth_res['error'].get('message')}")
            else:
                priv = auth_res.get("privacy_policy_url")
                link = auth_res.get("link")
                cat = auth_res.get("category")
                print(f"\n📋 MANDATORY COMPLIANCE CHECKLIST:")
                print(f"   - Privacy Policy URL: {priv} {'✅ OK' if priv and 'privacy.html' in priv else '⚠️ CHECK REQUIRED'}")
                print(f"   - Website Platform URL: {link} {'✅ OK' if link and EXPECTED_DOMAIN in link else '⚠️ CHECK REQUIRED'}")
                print(f"   - Category: {cat} ✅")
        except Exception as e:
            print(f"❌ Authenticated check failed: {e}")

    return is_live

if __name__ == "__main__":
    print("=================================================================")
    print("🚨 META DEVELOPER APPS 'LIVE MODE' & COMPLIANCE MASTER AUDIT")
    print("=================================================================")
    all_ok = True
    for item in APP_REGISTRY:
        ok = audit_app(item)
        if not ok:
            all_ok = False

    print("\n=================================================================")
    if all_ok:
        print("🎉 ALL META DEVELOPER APPS ARE 100% VERIFIED LIVE!")
    else:
        print("⚠️ SOME APPS REQUIRE REVIEW (SEE DETAILS ABOVE)")
    print("=================================================================\n")
