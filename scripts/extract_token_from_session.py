"""
Extract Access Token from Meta Business Suite / Graph Explorer
"""

import sys
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.anti_detect.device_profiles import S25_NEWYORK_PROFILE
from src.anti_detect.browser_launcher import launch_android_browser


def extract_token_from_session():
    p, ctx, page = launch_android_browser(S25_NEWYORK_PROFILE, headless=True)
    try:
        page.goto("https://business.facebook.com/latest/home", wait_until="domcontentloaded", timeout=25000)
        time.sleep(5)

        # Inspect window and local storage for access tokens
        tokens = page.evaluate("""() => {
            const found = [];
            // Check localStorage
            for (let i = 0; i < localStorage.length; i++) {
                const k = localStorage.key(i);
                const v = localStorage.getItem(k);
                if (v && v.includes('EAA')) {
                    const match = v.match(/EAA[A-Za-z0-9]+/);
                    if (match) found.push({ source: 'localStorage: ' + k, token: match[0] });
                }
            }
            // Check sessionStorage
            for (let i = 0; i < sessionStorage.length; i++) {
                const k = sessionStorage.key(i);
                const v = sessionStorage.getItem(k);
                if (v && v.includes('EAA')) {
                    const match = v.match(/EAA[A-Za-z0-9]+/);
                    if (match) found.push({ source: 'sessionStorage: ' + k, token: match[0] });
                }
            }
            // Check scripts in DOM
            const scripts = Array.from(document.querySelectorAll('script'));
            scripts.forEach(s => {
                const text = s.innerText || '';
                if (text.includes('EAAB') || text.includes('EAA')) {
                    const match = text.match(/\"(EAA[A-Za-z0-9]+)\"/);
                    if (match) found.push({ source: 'script', token: match[1] });
                }
            });
            return found;
        }""")
        print("Found tokens in session:", tokens)
    finally:
        ctx.close()
        p.stop()


if __name__ == "__main__":
    extract_token_from_session()
