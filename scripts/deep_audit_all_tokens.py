import os
import sys
import json
import time
import requests
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES_JSON = os.path.join(BASE_DIR, "docs", "data", "pages_data.json")

def check_token(page):
    pid = str(page.get("id"))
    name = page.get("name", "Unknown")
    token = page.get("access_token")
    acc = page.get("account", "Unknown")
    
    if not token:
        return {
            "page_id": pid,
            "name": name,
            "account": acc,
            "valid": False,
            "status": "NO_TOKEN",
            "error": "No token provided",
            "followers": page.get("followers", 0)
        }

    url = f"https://graph.facebook.com/v20.0/{pid}"
    params = {
        "fields": "id,name,is_published,fan_count,followers_count",
        "access_token": token
    }
    try:
        r = requests.get(url, params=params, timeout=12)
        res = r.json()
        if "error" in res:
            err = res["error"]
            return {
                "page_id": pid,
                "name": name,
                "account": acc,
                "valid": False,
                "status": f"ERROR_{err.get('code')}",
                "error": err.get("message"),
                "followers": page.get("followers", 0)
            }
        else:
            fol = res.get("followers_count") or res.get("fan_count") or 0
            return {
                "page_id": pid,
                "name": res.get("name", name),
                "account": acc,
                "valid": True,
                "status": "VALID",
                "error": None,
                "followers": fol,
                "is_published": res.get("is_published", True)
            }
    except Exception as e:
        return {
            "page_id": pid,
            "name": name,
            "account": acc,
            "valid": False,
            "status": "NETWORK_TIMEOUT",
            "error": str(e),
            "followers": page.get("followers", 0)
        }

def main():
    print("=" * 80)
    print("🚀 LIVE SCANNING ALL 156 FACEBOOK PAGE TOKENS VIA META GRAPH API...")
    print("=" * 80)

    if not os.path.exists(PAGES_JSON):
        print(f"Error: {PAGES_JSON} not found!")
        sys.exit(1)

    with open(PAGES_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    pages = data.get("pages", [])
    print(f"Loaded {len(pages)} pages from {PAGES_JSON}.\n")

    results = []
    start_t = time.time()

    # Use ThreadPoolExecutor to verify concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_page = {executor.submit(check_token, p): p for p in pages}
        for future in as_completed(future_to_page):
            res = future.result()
            results.append(res)
            icon = "✅" if res["valid"] else "❌"
            if not res["valid"]:
                print(f"  {icon} [{res['account']}] {res['name']} ({res['page_id']}): {res['status']} - {res['error']}")

    valid_count = sum(1 for r in results if r["valid"])
    invalid_count = len(results) - valid_count
    elapsed = time.time() - start_t

    print("\n" + "=" * 80)
    print("📊 META GRAPH API TOKEN SCAN RESULTS:")
    print("=" * 80)
    print(f"  Total Pages Audited: {len(results)}")
    print(f"  Valid Active Tokens: {valid_count} ({valid_count / len(results) * 100:.1f}%)")
    print(f"  Invalid / Expired Tokens: {invalid_count}")
    print(f"  Time Elapsed: {elapsed:.2f} seconds")
    print("=" * 80)

    # Save token audit report
    audit_report = {
        "audit_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_pages": len(results),
        "valid_tokens_count": valid_count,
        "invalid_tokens_count": invalid_count,
        "valid_percentage": round(valid_count / len(results) * 100, 1),
        "invalid_pages": [r for r in results if not r["valid"]],
        "valid_pages_summary_by_account": {}
    }

    for r in results:
        acc = r["account"]
        if acc not in audit_report["valid_pages_summary_by_account"]:
            audit_report["valid_pages_summary_by_account"][acc] = {"total": 0, "valid": 0, "invalid": 0}
        audit_report["valid_pages_summary_by_account"][acc]["total"] += 1
        if r["valid"]:
            audit_report["valid_pages_summary_by_account"][acc]["valid"] += 1
        else:
            audit_report["valid_pages_summary_by_account"][acc]["invalid"] += 1

    report_path = os.path.join(BASE_DIR, "token_audit_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(audit_report, f, indent=2)
    print(f"Saved token audit report to {report_path}")

    # Also save to docs/data/ and web/data/
    for sub in ["docs/data", "web/data"]:
        p = os.path.join(BASE_DIR, sub, "token_audit_report.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(audit_report, f, indent=2)

if __name__ == "__main__":
    main()
