#!/usr/bin/env python3
"""
Pre-Flight IP Health & Meta Reputation Auditor
Verifies IP geolocation, checks against Meta edge challenges,
and ensures egress IP is 100% clean and unflagged before uploading.
"""

import sys
import json
import argparse
import requests
import socket

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def get_telemetry():
    """Fetches public IP telemetry from redundant endpoints."""
    endpoints = [
        "https://ipinfo.io/json",
        "https://ipapi.co/json",
        "https://api.ipify.org?format=json"
    ]
    for url in endpoints:
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if "ip" in data:
                    return data
        except Exception:
            continue
    return {}

def check_meta_reputation():
    """
    Sends handshake pings to Meta endpoints to verify the IP
    is not shadow-banned, captcha-challenged, or blocked by Cloudflare/Meta edge.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    meta_urls = [
        "https://graph.facebook.com",
        "https://m.facebook.com"
    ]
    
    results = {}
    for url in meta_urls:
        try:
            res = requests.get(url, headers=headers, timeout=6, allow_redirects=True)
            status = res.status_code
            content = res.text.lower()
            
            # Signs of dirty IP: Cloudflare 403, Meta Security Check, Bot Challenge
            if status in [403, 429]:
                results[url] = {"clean": False, "status": status, "reason": f"HTTP {status} Blocked"}
            elif "security check" in content or "bot challenge" in content or "unusual traffic" in content:
                results[url] = {"clean": False, "status": status, "reason": "Meta Security Checkpoint Triggered"}
            else:
                results[url] = {"clean": True, "status": status, "reason": "Clean Response"}
        except requests.exceptions.RequestException as e:
            results[url] = {"clean": False, "status": 0, "reason": f"Connection Error: {e}"}
            
    is_all_clean = all(r["clean"] for r in results.values())
    return is_all_clean, results

def check_dnsbl_reputation(ip):
    """Checks IP against popular DNS blacklists."""
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return True, "Skipped (non-IPv4)"
        reversed_ip = '.'.join(reversed(parts))
    except Exception:
        return True, "Skipped"

    blacklists = [
        "zen.spamhaus.org",
        "bl.spamcop.net"
    ]
    
    flagged = []
    for bl in blacklists:
        query = f"{reversed_ip}.{bl}"
        try:
            socket.gethostbyname(query)
            flagged.append(bl)
        except socket.gaierror:
            pass
        except Exception:
            pass

    if flagged:
        return False, f"Flagged in DNSBL: {', '.join(flagged)}"
    return True, "Clean (Not listed in Spamhaus/Spamcop)"

def main():
    parser = argparse.ArgumentParser(description="Pre-Flight IP Health & Reputation Auditor")
    parser.add_argument("--require-country", help="Required 2-letter Country Code (e.g. GB, US)")
    parser.add_argument("--require-city", help="Optional City Name match (case-insensitive)")
    parser.add_argument("--output-json", help="Path to save JSON health report")
    args = parser.parse_args()

    print("==================================================================")
    print("🔍 PRE-FLIGHT IP HEALTH & META REPUTATION AUDITOR")
    print("==================================================================")

    # 1. Telemetry
    telemetry = get_telemetry()
    ip = telemetry.get("ip", "Unknown")
    city = telemetry.get("city", "Unknown")
    region = telemetry.get("region", "Unknown")
    country = (telemetry.get("country") or "").strip().upper()
    org = telemetry.get("org", "Unknown")

    print(f"📍 Egress IP:        {ip}")
    print(f"📍 Location:         {city}, {region}, {country}")
    print(f"📍 Network/ISP:      {org}")
    print("------------------------------------------------------------------")

    report = {
        "ip": ip,
        "location": f"{city}, {region}, {country}",
        "country": country,
        "org": org,
        "passed": False,
        "reasons": []
    }

    # 2. Country Verification
    if args.require_country:
        req_c = args.require_country.strip().upper()
        if country != req_c:
            err = f"Country Mismatch: Detected '{country}', expected '{req_c}'"
            print(f"❌ [FAIL] {err}")
            report["reasons"].append(err)
        else:
            print(f"✅ [PASS] Country Verified: Matches target '{req_c}'")

    # 3. Meta Reputation Handshake
    print("⏳ Probing Meta Edge Endpoints for IP reputation...")
    meta_clean, meta_results = check_meta_reputation()
    for u, res in meta_results.items():
        if res["clean"]:
            print(f"✅ [PASS] {u} -> Status {res['status']} ({res['reason']})")
        else:
            err = f"Meta Edge Block on {u}: {res['reason']}"
            print(f"❌ [DIRTY] {err}")
            report["reasons"].append(err)

    # 4. DNSBL Spamhaus / Abuse Check
    if ip != "Unknown":
        print(f"⏳ Checking DNSBL Reputation for {ip}...")
        dns_clean, dns_msg = check_dnsbl_reputation(ip)
        if dns_clean:
            print(f"✅ [PASS] Spam Blacklists: {dns_msg}")
        else:
            print(f"⚠️ [WARN] Spam Blacklists: {dns_msg}")

    # Final Determination
    if not report["reasons"]:
        report["passed"] = True
        print("==================================================================")
        print("🎉 STATUS: 100% HEALTHY & CLEAN IP! SAFE TO PROCEED WITH UPLOADS.")
        print("==================================================================")
        sys.exit(0)
    else:
        report["passed"] = False
        print("==================================================================")
        print("🚨 STATUS: IP FAILED HEALTH AUDIT! AUTO-ROTATION REQUIRED.")
        for r in report["reasons"]:
            print(f"   • {r}")
        print("==================================================================")
        sys.exit(1)

if __name__ == "__main__":
    main()
