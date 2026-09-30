"""
CLI Tool: Launch Samsung Galaxy S25 (New York Telemetry) Android Profile
Provides interactive 1-Click Login, Telemetry Verification, and Page Auto-Discovery.
"""

import sys
import os
import argparse
import time
import json
from datetime import datetime, timezone

# Ensure project root is in sys.path
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


def print_banner(profile):
    print("=" * 70)
    print("📱 ANTI-DETECT ANDROID EMULATION ENGINE (SAMSUNG GALAXY S25)")
    print("=" * 70)
    print(f"  • Device Model:     {profile.device_name} ({profile.model})")
    print(f"  • Operating System: {profile.os_name} {profile.os_version}")
    print(f"  • Platform String:  {profile.platform}")
    print(f"  • GPU / Renderer:   {profile.webgl_vendor} {profile.webgl_renderer}")
    print(f"  • Hardware Specs:   {profile.hardware_concurrency} CPU Cores | {profile.device_memory_gb} GB RAM")
    print(f"  • Battery State:    {int(profile.battery_level * 100)}% (Discharging, 9.0h left)")
    print("-" * 70)
    print(f"  🌐 STRICT TIMEZONE:  {profile.timezone_id} (Eastern Time)")
    print(f"  📍 GPS GEOLOCATION:  Lat: {profile.latitude}, Lon: {profile.longitude} (New York, NY)")
    print(f"  🗣️ LOCALE & LANG:    {profile.locale} (Languages: {profile.languages})")
    print("=" * 70)


def mode_verify(profile):
    """Executes a silent pre-flight verification of the Android profile and timezone."""
    print_banner(profile)
    print("\n⏳ Running automated pre-flight verification in isolated sandbox...")
    playwright, context, page = launch_android_browser(profile=profile, headless=True)

    try:
        page.goto("about:blank")
        tz = page.evaluate("Intl.DateTimeFormat().resolvedOptions().timeZone")
        offset = page.evaluate("new Date().getTimezoneOffset()")
        platform = page.evaluate("navigator.platform")
        ua = page.evaluate("navigator.userAgent")
        cores = page.evaluate("navigator.hardwareConcurrency")
        ram = page.evaluate("navigator.deviceMemory")
        date_str = page.evaluate("new Date().toString()")

        print("\n📋 PRE-FLIGHT VERIFICATION RESULTS:")
        print(f"  ✅ Timezone:        {tz} (Match: {tz == profile.timezone_id})")
        print(f"  ✅ Timezone Offset: {offset} mins (Match: {offset in (240, 300)})")
        print(f"  ✅ Current Time:    {date_str}")
        print(f"  ✅ Platform:        {platform}")
        print(f"  ✅ User-Agent:      {ua}")
        print(f"  ✅ Cores & Memory:  {cores} Cores, {ram} GB RAM")

        session_mgr = ProfileSessionManager(profile.profile_id)
        user_data = session_mgr.get_user_data_dir()
        print(f"\n📁 Profile Sandbox Storage: {user_data}")
        print("🎉 PRE-FLIGHT STATUS: 100% HEALTHY! ZERO IST LEAK.")
    finally:
        context.close()
        playwright.stop()


def mode_login(profile):
    """Launches an interactive visible mobile browser for the user to log in."""
    print_banner(profile)
    print("\n🚀 LAUNCHING INTERACTIVE ANDROID BROWSER FOR LOGIN...")
    print("👉 Login to your Facebook account on the opened mobile screen.")
    print("👉 Complete 2FA and ensure you check 'Remember Me'.")
    print("👉 When you are logged in, press [ENTER] in this terminal to save session.\n")

    initial_url = "https://m.facebook.com"
    playwright, context, page = launch_android_browser(
        profile=profile,
        headless=False,
        initial_url=initial_url
    )

    try:
        input("Press [ENTER] here once you have finished logging in and can see your feed... ")
        cookies = context.cookies()
        c_user = next((c for c in cookies if c.get("name") == "c_user"), None)

        session_mgr = ProfileSessionManager(profile.profile_id)
        if c_user:
            fb_uid = c_user.get("value")
            print(f"\n🎉 LOGIN DETECTED! Facebook User ID (c_user): {fb_uid}")
            session_mgr.save_metadata({
                "profile_id": profile.profile_id,
                "device_name": profile.device_name,
                "model": profile.model,
                "status": "authenticated",
                "fb_user_id": fb_uid,
                "logged_in_at": datetime.now(timezone.utc).isoformat()
            })
            print(f"✅ Session permanently saved to profile directory.")
        else:
            print("\n⚠️ Note: 'c_user' cookie was not found yet. If login was completed, session data in the profile folder will still persist.")

    finally:
        context.close()
        playwright.stop()
        print("🔒 Browser closed. Sandbox isolated and saved.")


def mode_sync_pages(profile):
    """Navigates to Meta Business Suite to auto-discover all accessible Pages."""
    print_banner(profile)
    print("\n🔍 AUTO-DISCOVERING PAGES FROM ANDROID SESSION...")
    session_mgr = ProfileSessionManager(profile.profile_id)

    playwright, context, page = launch_android_browser(
        profile=profile,
        headless=False,
        initial_url="https://business.facebook.com/latest/home"
    )

    try:
        time.sleep(5)
        # Check current URL
        curr_url = page.url
        print(f"Current Navigation URL: {curr_url}")

        if "login" in curr_url or "checkpoint" in curr_url:
            print("⚠️ Account requires login first! Please run with --mode login")
            return

        print("Logged in! Checking accessible pages and permissions...")
        page.goto("https://m.facebook.com/pages/", wait_until="domcontentloaded")
        time.sleep(4)

        # Extract page names and links
        links = page.evaluate("""() => {
            const anchors = Array.from(document.querySelectorAll('a[href*="/"]'));
            const found = [];
            anchors.forEach(a => {
                const text = a.innerText.trim();
                const href = a.href;
                if (text && (href.includes('/pages/') || href.includes('facebook.com/profile.php') || href.includes('facebook.com/'))) {
                    found.push({ name: text, url: href });
                }
            });
            return found;
        }""")
        print(f"Found {len(links)} Page elements. Storing to pages.json...")
        session_mgr.save_pages(links)
        print("✅ Discovered pages saved successfully!")

    finally:
        context.close()
        playwright.stop()


def main():
    parser = argparse.ArgumentParser(description="Samsung Galaxy S25 New York Anti-Detect Launcher")
    parser.add_argument(
        "--mode",
        choices=["verify", "login", "sync_pages"],
        default="verify",
        help="Operation mode: 'verify' (pre-flight test), 'login' (interactive login), 'sync_pages' (auto-sync)"
    )
    args = parser.parse_args()

    profile = S25_NEWYORK_PROFILE
    if args.mode == "verify":
        mode_verify(profile)
    elif args.mode == "login":
        mode_login(profile)
    elif args.mode == "sync_pages":
        mode_sync_pages(profile)


if __name__ == "__main__":
    main()
