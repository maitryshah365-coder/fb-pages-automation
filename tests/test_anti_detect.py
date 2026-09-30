"""
Unit Tests for Anti-Detect Android Emulation Engine
Verifies hardware spoofing, New York timezone lock, and stealth JavaScript overrides.
"""

import pytest
from src.anti_detect.device_profiles import S25_NEWYORK_PROFILE
from src.anti_detect.browser_launcher import launch_android_browser


def test_samsung_s25_profile_specs():
    """Validates Samsung S25 profile hardware configuration."""
    profile = S25_NEWYORK_PROFILE
    assert profile.brand == "Samsung"
    assert profile.model == "SM-S931U"
    assert profile.timezone_id == "America/New_York"
    assert profile.locale == "en-US"
    assert profile.platform == "Linux armv8l"
    assert profile.hardware_concurrency == 8
    assert profile.device_memory_gb == 12
    assert profile.webgl_vendor == "Qualcomm"
    assert profile.webgl_renderer == "Adreno (TM) 830"
    assert profile.latitude == 40.7128
    assert profile.longitude == -74.0060


def test_anti_detect_stealth_in_browser():
    """Launches headless browser and evaluates injected JS values to guarantee zero leakage."""
    playwright, context, page = launch_android_browser(
        profile=S25_NEWYORK_PROFILE,
        headless=True
    )

    try:
        page.goto("about:blank")

        # 1. Timezone Check (Zero IST leak)
        tz = page.evaluate("Intl.DateTimeFormat().resolvedOptions().timeZone")
        assert tz == "America/New_York", f"Timezone leaked! Got {tz}"

        offset = page.evaluate("new Date().getTimezoneOffset()")
        # NY EDT is 240, EST is 300. IST would be -330.
        assert offset in (240, 300), f"Timezone offset leaked! Expected 240 or 300, got {offset}"

        date_str = page.evaluate("new Date().toString()")
        assert "India" not in date_str and "IST" not in date_str and "+0530" not in date_str, f"IST leaked in Date.toString: {date_str}"

        # 2. Hardware Identifiers
        platform = page.evaluate("navigator.platform")
        assert platform == "Linux armv8l", f"Platform leaked! Got {platform}"

        ua = page.evaluate("navigator.userAgent")
        assert "SM-S931U" in ua and "Android 15" in ua

        touch_points = page.evaluate("navigator.maxTouchPoints")
        assert touch_points == 5

        cores = page.evaluate("navigator.hardwareConcurrency")
        assert cores == 8

        ram = page.evaluate("navigator.deviceMemory")
        assert ram == 12

        # 3. Battery API
        battery_level = page.evaluate("async () => (await navigator.getBattery()).level")
        assert battery_level == 0.88

        # 4. WebGL GPU Spoofing
        webgl_info = page.evaluate("""() => {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl');
            if (!gl) return { vendor: null, renderer: null };
            const ext = gl.getExtension('WEBGL_debug_renderer_info');
            return {
                vendor: gl.getParameter(ext ? ext.UNMASKED_VENDOR_WEBGL : gl.VENDOR),
                renderer: gl.getParameter(ext ? ext.UNMASKED_RENDERER_WEBGL : gl.RENDERER)
            };
        }""")
        assert webgl_info["vendor"] == "Qualcomm"
        assert webgl_info["renderer"] == "Adreno (TM) 830"

    finally:
        context.close()
        playwright.stop()
