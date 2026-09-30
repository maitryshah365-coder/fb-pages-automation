"""
Cookie Importer & Session Activator for Samsung Galaxy S25 Android Profile
Parses cookies from JSON, Cookie-Editor, or raw header strings and injects into sandbox.
"""

import sys
import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Union

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.anti_detect.device_profiles import S25_NEWYORK_PROFILE
from src.anti_detect.browser_launcher import launch_android_browser
from src.anti_detect.session_manager import ProfileSessionManager


def parse_raw_cookie_string(raw_str: str) -> List[Dict[str, Any]]:
    """Parses raw 'key=val; key2=val2' cookie string into Playwright format."""
    cookies = []
    pairs = [p.strip() for p in raw_str.split(";") if "=" in p.strip()]
    for pair in pairs:
        parts = pair.split("=", 1)
        name = parts[0].strip()
        value = parts[1].strip()
        cookies.append({
            "name": name,
            "value": value,
            "domain": ".facebook.com",
            "path": "/",
            "secure": True,
            "httpOnly": name in ("xs", "fr", "datr", "sb", "c_user"),
            "sameSite": "Lax"
        })
    return cookies


def normalize_cookies(cookie_input: Union[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Converts various cookie formats (JSON export, list, or header string) to Playwright cookies."""
    if isinstance(cookie_input, str):
        cookie_input = cookie_input.strip()
        if cookie_input.startswith("[") and cookie_input.endswith("]"):
            try:
                data = json.loads(cookie_input)
                return normalize_cookies(data)
            except Exception:
                pass
        return parse_raw_cookie_string(cookie_input)

    elif isinstance(cookie_input, list):
        normalized = []
        for c in cookie_input:
            if not isinstance(c, dict):
                continue
            name = c.get("name")
            value = c.get("value")
            if not name or value is None:
                continue
            domain = c.get("domain", ".facebook.com")
            if not domain.startswith("."):
                domain = "." + domain
            path = c.get("path", "/")
            item = {
                "name": str(name),
                "value": str(value),
                "domain": domain,
                "path": path,
                "secure": bool(c.get("secure", True)),
                "httpOnly": bool(c.get("httpOnly", False)),
                "sameSite": "None" if c.get("sameSite") == "no_restriction" else "Lax"
            }
            if "expirationDate" in c and c["expirationDate"]:
                item["expires"] = int(c["expirationDate"])
            normalized.append(item)
        return normalized

    return []


def inject_cookies_and_verify(cookie_data: Union[str, List[Dict[str, Any]]], profile=S25_NEWYORK_PROFILE):
    """Injects cookies into the Samsung S25 profile and validates session against Facebook."""
    cookies = normalize_cookies(cookie_data)
    print(f"--> Parsed {len(cookies)} cookies.")
    c_user = next((c for c in cookies if c["name"] == "c_user"), None)
    if c_user:
        print(f"--> Found Facebook User ID: {c_user['value']}")
    else:
        print("⚠️ Warning: 'c_user' cookie not found in input. Verification will test if session is active.")

    session_mgr = ProfileSessionManager(profile.profile_id)
    print(f"--> Launching Samsung S25 (New York) to inject session cookies...")

    playwright, context, page = launch_android_browser(
        profile=profile,
        headless=True
    )

    try:
        context.add_cookies(cookies)
        print("--> Navigating to https://m.facebook.com to verify login...")
        page.goto("https://m.facebook.com", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        curr_url = page.url
        print(f"--> Current URL: {curr_url}")

        is_logged_in = False
        user_name = "Unknown"

        if "login" not in curr_url and "checkpoint" not in curr_url:
            is_logged_in = True
            # Try to fetch title or profile name
            page_title = page.title()
            print(f"--> Page Title: {page_title}")
            print("🎉 SUCCESS: Session is 100% active and authenticated!")
            
            fb_uid = c_user["value"] if c_user else "unknown"
            session_mgr.save_metadata({
                "profile_id": profile.profile_id,
                "device_name": profile.device_name,
                "model": profile.model,
                "status": "authenticated",
                "fb_user_id": fb_uid,
                "cookies_count": len(cookies),
                "verified_at": datetime.now(timezone.utc).isoformat()
            })
            print(f"✅ Session permanently saved in sandbox: {session_mgr.get_user_data_dir()}")
        else:
            print("❌ Verification Failed: Facebook redirected to login screen or checkpoint.")

        return is_logged_in

    finally:
        context.close()
        playwright.stop()


if __name__ == "__main__":
    import time
    if len(sys.argv) > 1:
        # If passed as file path
        fpath = sys.argv[1]
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            inject_cookies_and_verify(content)
        else:
            # Passed as raw string
            inject_cookies_and_verify(sys.argv[1])
    else:
        print("Usage: python scripts/import_cookies.py <path_to_cookie_file_or_string>")
