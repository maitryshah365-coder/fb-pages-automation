"""
Playwright Browser Launcher for Anti-Detect Android Emulation
Configures pristine sandbox environments with deep stealth injections.
"""

import os
from typing import Tuple, Optional
from playwright.sync_api import sync_playwright, BrowserContext, Page, Playwright

from .device_profiles import DeviceProfile
from .stealth_scripts import generate_stealth_js
from .session_manager import ProfileSessionManager


def launch_android_browser(
    profile: DeviceProfile,
    headless: bool = False,
    initial_url: Optional[str] = None
) -> Tuple[Playwright, BrowserContext, Page]:
    """
    Launches a dedicated Playwright persistent browser context mimicking
    the authentic Android device profile with hard-locked timezone & geolocation.
    """
    session_mgr = ProfileSessionManager(profile.profile_id)
    user_data_dir = session_mgr.get_user_data_dir()

    # Save/update profile metadata
    session_mgr.save_metadata({
        "profile_id": profile.profile_id,
        "device_name": profile.device_name,
        "brand": profile.brand,
        "model": profile.model,
        "os_version": profile.os_version,
        "timezone_id": profile.timezone_id,
        "locale": profile.locale,
        "latitude": profile.latitude,
        "longitude": profile.longitude,
        "viewport": {
            "width": profile.viewport_width,
            "height": profile.viewport_height,
            "dpr": profile.device_scale_factor
        },
        "user_data_dir": user_data_dir
    })

    playwright = sync_playwright().start()

    # Chromium anti-bot flags & mobile arguments
    args = [
        "--disable-blink-features=AutomationControlled",
        "--enable-features=NetworkService,NetworkServiceInProcess",
        "--disable-features=IsolateOrigins,site-per-process",
        f"--lang={profile.locale}",
        "--no-default-browser-check",
        "--disable-infobars"
    ]

    context = playwright.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=headless,
        viewport={
            "width": profile.viewport_width,
            "height": profile.viewport_height
        },
        device_scale_factor=profile.device_scale_factor,
        is_mobile=profile.is_mobile,
        has_touch=profile.has_touch,
        user_agent=profile.user_agent,
        locale=profile.locale,
        timezone_id=profile.timezone_id,
        geolocation={
            "latitude": profile.latitude,
            "longitude": profile.longitude,
            "accuracy": profile.accuracy
        },
        permissions=["geolocation"],
        ignore_https_errors=True,
        args=args
    )

    # Inject stealth scripts before ANY page scripts execute
    stealth_code = generate_stealth_js(profile)
    context.add_init_script(stealth_code)

    # Inject session cookies into context if available
    cookies_path = os.path.join(session_mgr.profile_dir, "cookies.json")
    if os.path.exists(cookies_path):
        try:
            import json as _json
            with open(cookies_path, "r", encoding="utf-8") as f:
                raw_cookies = _json.load(f)
            playwright_cookies = []
            for c in raw_cookies:
                pc = {
                    "name": c["name"],
                    "value": c["value"],
                    "domain": c.get("domain", ".facebook.com"),
                    "path": c.get("path", "/"),
                    "secure": c.get("secure", True)
                }
                if "expirationDate" in c and c["expirationDate"]:
                    pc["expires"] = float(c["expirationDate"])
                ss = c.get("sameSite")
                if ss:
                    ss_lower = str(ss).lower()
                    if "lax" in ss_lower:
                        pc["sameSite"] = "Lax"
                    elif "strict" in ss_lower:
                        pc["sameSite"] = "Strict"
                    elif "none" in ss_lower or "no_restriction" in ss_lower:
                        pc["sameSite"] = "None"
                playwright_cookies.append(pc)
            context.add_cookies(playwright_cookies)
        except Exception as e:
            print(f"Warning: Could not inject cookies into context: {e}")

    # Get or create the main page
    page = context.pages[0] if context.pages else context.new_page()

    if initial_url:
        page.goto(initial_url, wait_until="domcontentloaded")

    return playwright, context, page
