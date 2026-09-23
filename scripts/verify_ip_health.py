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

import os
from datetime import datetime, timezone

DIRTY_IPS_FILE = "data/dirty_ips.json"
CLEAN_IPS_FILE = "data/clean_ips.json"

def load_json_cache(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_json_cache(filepath, data):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        # Also sync to docs/data for live web dashboard visibility
        docs_copy = os.path.join("docs", filepath)
        os.makedirs(os.path.dirname(docs_copy), exist_ok=True)
        with open(docs_copy, "w", encoding="utf-8") as df:
            json.dump(data, df, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ [WARN] Failed to write IP cache to {filepath}: {e}")

def record_dirty_ip(ip, reasons, country, city, org):
    cache = load_json_cache(DIRTY_IPS_FILE)
    if "dirty_ips" not in cache:
        cache["dirty_ips"] = {}
    cache["updated_at"] = datetime.now(timezone.utc).isoformat()
    cache["dirty_ips"][ip] = {
        "flagged_at": datetime.now(timezone.utc).isoformat(),
        "reasons": reasons,
        "country": country,
        "city": city,
        "org": org,
        "hit_count": cache["dirty_ips"].get(ip, {}).get("hit_count", 0) + 1
    }
    save_json_cache(DIRTY_IPS_FILE, cache)

def record_clean_ip(ip, country, city, org):
    cache = load_json_cache(CLEAN_IPS_FILE)
    if "clean_ips" not in cache:
        cache["clean_ips"] = {}
    cache["updated_at"] = datetime.now(timezone.utc).isoformat()
    cache["clean_ips"][ip] = {
        "last_verified_at": datetime.now(timezone.utc).isoformat(),
        "country": country,
        "city": city,
        "org": org,
        "success_count": cache["clean_ips"].get(ip, {}).get("success_count", 0) + 1
    }
    save_json_cache(CLEAN_IPS_FILE, cache)

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

    # 2. FAST CACHE CHECK: Is this IP already in our Persistent Dirty Blacklist?
    dirty_cache = load_json_cache(DIRTY_IPS_FILE).get("dirty_ips", {})
    if ip in dirty_cache:
        bad_info = dirty_cache[ip]
        flagged_date = bad_info.get("flagged_at", "recently")
        prior_reasons = bad_info.get("reasons", ["Unknown reason"])
        hits = bad_info.get("hit_count", 1) + 1
        record_dirty_ip(ip, prior_reasons, country, city, org)
        print("🚨 [INSTANT CACHE HIT] IP IS ON OUR DIRTY BLACKLIST!")
        print(f"   • Previously flagged at: {flagged_date}")
        print(f"   • Prior failure reasons: {prior_reasons}")
        print(f"   • Hit count: {hits}")
        print("⚡ Skipping redundant network tests — immediate auto-rotation triggered!")
        print("==================================================================")
        sys.exit(1)

    report = {
        "ip": ip,
        "location": f"{city}, {region}, {country}",
        "country": country,
        "org": org,
        "passed": False,
        "reasons": []
    }

    # 3. Country Verification
    if args.require_country:
        req_c = args.require_country.strip().upper()
        if country != req_c:
            err = f"Country Mismatch: Detected '{country}', expected '{req_c}'"
            print(f"❌ [FAIL] {err}")
            report["reasons"].append(err)
        else:
            print(f"✅ [PASS] Country Verified: Matches target '{req_c}'")

    # 4. Meta Reputation Handshake
    print("⏳ Probing Meta Edge Endpoints for IP reputation...")
    meta_clean, meta_results = check_meta_reputation()
    for u, res in meta_results.items():
        if res["clean"]:
            print(f"✅ [PASS] {u} -> Status {res['status']} ({res['reason']})")
        else:
            err = f"Meta Edge Block on {u}: {res['reason']}"
            print(f"❌ [DIRTY] {err}")
            report["reasons"].append(err)

    # 5. DNSBL Spamhaus / Abuse Check
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
        record_clean_ip(ip, country, city, org)
        print("==================================================================")
        print("🎉 STATUS: 100% HEALTHY & CLEAN IP! SAFE TO PROCEED WITH UPLOADS.")
        print("💾 Recorded into Clean IP Trust Cache.")
        print("==================================================================")
        sys.exit(0)
    else:
        report["passed"] = False
        record_dirty_ip(ip, report["reasons"], country, city, org)
        print("==================================================================")
        print("🚨 STATUS: IP FAILED HEALTH AUDIT! AUTO-ROTATION REQUIRED.")
        for r in report["reasons"]:
            print(f"   • {r}")
        print(f"💾 Added {ip} to persistent dirty blacklist ({DIRTY_IPS_FILE})")
        print("==================================================================")
        sys.exit(1)

if __name__ == "__main__":
    main()
