"""
Helper script to exchange a short-lived User Access Token for long-lived Page Access Tokens.
Follows Section 23 of the Facebook Master Spec.

Usage:
  python scripts/exchange_tokens.py --app-id <APP_ID> --app-secret <APP_SECRET> --user-token <USER_TOKEN>
"""

import sys
import argparse
import requests

GRAPH_API_VERSION = "v20.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


def exchange_token(app_id: str, app_secret: str, short_lived_token: str):
    print("\n=======================================================")
    print("   FACEBOOK GRAPH API TOKEN EXCHANGE UTILITY")
    print("=======================================================\n")

    # Step 1: Exchange short-lived user token for long-lived user token (approx 60 days)
    print("1. Exchanging short-lived User Token for Long-Lived User Token...")
    exchange_url = f"{BASE_URL}/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_lived_token
    }
    resp = requests.get(exchange_url, params=params, timeout=20)
    if not resp.ok:
        print(f"FAILED to exchange token: {resp.status_code} - {resp.text}")
        sys.exit(1)

    long_lived_user_token = resp.json().get("access_token")
    print("   SUCCESS! Long-Lived User Token obtained.")

    # Step 2: Fetch Page Access Tokens for all administered Pages
    print("\n2. Fetching Page Access Tokens from /me/accounts...")
    accounts_url = f"{BASE_URL}/me/accounts"
    acc_params = {
        "access_token": long_lived_user_token,
        "limit": 100
    }
    acc_resp = requests.get(accounts_url, params=acc_params, timeout=20)
    if not acc_resp.ok:
        print(f"FAILED to fetch pages: {acc_resp.status_code} - {acc_resp.text}")
        sys.exit(1)

    pages_data = acc_resp.json().get("data", [])
    if not pages_data:
        print("   WARNING: No Facebook Pages found under this user account!")
        print("   Ensure the user account has CREATE_CONTENT or Admin task on the target Pages.")
        return

    print(f"   Found {len(pages_data)} Facebook Page(s).\n")
    print("=======================================================")
    print("   PAGE ACCESS TOKENS (NON-EXPIRING)")
    print("   Copy and add these into your GitHub Repository Secrets:")
    print("=======================================================\n")

    for p in pages_data:
        p_name = p.get("name", "Unknown")
        p_id = p.get("id", "")
        p_token = p.get("access_token", "")
        safe_name = p_name.upper().replace(" ", "_").replace("-", "_")

        secret_name = f"FB_TOKEN_{safe_name}"

        print(f"Page Name  : {p_name}")
        print(f"Page ID    : {p_id}")
        print(f"Secret Name: {secret_name}")
        print(f"Secret Value:\n{p_token}\n")
        print("-" * 55)

    print("\n[NOTE] Page tokens generated from a long-lived user token are permanent")
    print("(non-expiring) unless your Facebook password changes or access is manually revoked.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Facebook Token Exchange Utility")
    parser.add_argument("--app-id", required=True, help="Meta App ID")
    parser.add_argument("--app-secret", required=True, help="Meta App Secret")
    parser.add_argument("--user-token", required=True, help="Short-lived User Access Token from Graph API Explorer")
    args = parser.parse_args()

    exchange_token(args.app_id, args.app_secret, args.user_token)
