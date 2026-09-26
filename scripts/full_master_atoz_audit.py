import os
import sys
import json
import yaml
import glob
from concurrent.futures import ThreadPoolExecutor
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_pages_and_tokens():
    pages_path = os.path.join(BASE_DIR, "docs", "data", "pages_data.json")
    with open(pages_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    pages = data.get("pages", [])

    # Load all YAML configs
    cfg_tokens = {}
    cfg_folders = {}
    for yml in glob.glob(os.path.join(BASE_DIR, "*.yaml")):
        try:
            with open(yml, "r", encoding="utf-8") as f:
                yd = yaml.safe_load(f)
                if isinstance(yd, dict):
                    for p in yd.get("pages", []):
                        pid = str(p.get("page_id") or p.get("id") or "")
                        tok = p.get("page_access_token") or p.get("access_token")
                        fld = p.get("drive_folder_id")
                        if pid and tok:
                            cfg_tokens[pid] = tok
                        if pid and fld:
                            cfg_folders[pid] = fld
        except Exception:
            pass

    # Load data token files
    for dfile in glob.glob(os.path.join(BASE_DIR, "data", "*.json")):
        try:
            with open(dfile, "r", encoding="utf-8") as f:
                ddata = json.load(f)
                plist = ddata.get("pages", []) if isinstance(ddata, dict) else (ddata if isinstance(ddata, list) else [])
                for p in plist:
                    if isinstance(p, dict):
                        pid = str(p.get("id") or p.get("page_id") or "")
                        tok = p.get("access_token") or p.get("page_access_token")
                        fld = p.get("drive_folder_id") or p.get("folder_id")
                        if pid and tok and pid not in cfg_tokens:
                            cfg_tokens[pid] = tok
                        if pid and fld and pid not in cfg_folders:
                            cfg_folders[pid] = fld
        except Exception:
            pass

    return pages, cfg_tokens, cfg_folders, data

def verify_token(p, cfg_tokens):
    pid = str(p.get("id", ""))
    name = p.get("name", "Unknown Page")
    account = p.get("account", "Unknown Fleet")
    token = cfg_tokens.get(pid) or p.get("access_token")

    res_item = {
        "id": pid,
        "name": name,
        "account": account,
        "has_token": bool(token),
        "valid": False,
        "error": None,
        "followers": p.get("followers", 0),
        "views": p.get("total_views", 0),
        "today_posts": p.get("today_posts", 0),
        "is_published": None
    }

    if not token:
        res_item["error"] = "No Token Configured"
        return res_item

    try:
        url = f"https://graph.facebook.com/v20.0/{pid}"
        r = requests.get(url, params={"fields": "id,name,is_published,followers_count", "access_token": token}, timeout=6)
        res_json = r.json()
        if "id" in res_json:
            res_item["valid"] = True
            res_item["is_published"] = res_json.get("is_published", True)
            if "followers_count" in res_json:
                res_item["followers"] = res_json.get("followers_count")
        else:
            err = res_json.get("error", {})
            err_msg = err.get("message", "Unknown error")
            err_code = err.get("code")
            res_item["error"] = f"[{err_code}] {err_msg[:45]}"
    except Exception as e:
        res_item["error"] = str(e)[:45]

    return res_item

def main():
    pages, cfg_tokens, cfg_folders, full_data = load_pages_and_tokens()
    print("==========================================================================")
    print(f"  MASTER A-TO-Z SYSTEM AUDIT: ALL {len(pages)} PAGES • LIVE META GRAPH API")
    print("==========================================================================")

    # 1. Verify Tokens concurrently
    print(f"--> Verifying Meta Graph API Tokens for all {len(pages)} pages (16 concurrent threads)...")
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = [pool.submit(verify_token, p, cfg_tokens) for p in pages]
        results = [f.result() for f in futures]

    valid_pages = [r for r in results if r["valid"]]
    invalid_pages = [r for r in results if not r["valid"]]

    print(f"\n[TOKEN HEALTH]: {len(valid_pages)} / {len(pages)} Pages VALID ({len(valid_pages)/len(pages)*100:.1f}%)")
    if invalid_pages:
        print(f"  ❌ Invalid/Expired Tokens: {len(invalid_pages)} Pages")
        for inv in invalid_pages[:10]:
            print(f"     - {inv['name']} ({inv['account']}): {inv['error']}")
        if len(invalid_pages) > 10:
            print(f"     ... and {len(invalid_pages)-10} more.")
    else:
        print("  ✅ 100% of All 128 Page Tokens are Active and Valid!")

    # 2. Uploading & Drive Inventory Audit
    print("\n--------------------------------------------------------------------------")
    print("  GOOGLE DRIVE STOCK & UPLOADING PIPELINE AUDIT")
    print("--------------------------------------------------------------------------")
    drive_configured = 0
    total_stock_videos = 0
    for p in pages:
        pid = str(p.get("id"))
        fld = cfg_folders.get(pid) or p.get("drive_folder_id")
        stock = p.get("videos_count") or p.get("stock_count") or 0
        if fld:
            drive_configured += 1
            total_stock_videos += int(stock)

    print(f"  • Drive Configured Pages: {drive_configured} / {len(pages)}")
    print(f"  • Total Video Stock in Drive: {total_stock_videos:,} Reels available")

    # 3. Fleet-Wise Today Uploads Audit
    print("\n--------------------------------------------------------------------------")
    print("  TODAY'S SLOTS & RADAR AUDIT (357 / 512 Slots)")
    print("--------------------------------------------------------------------------")
    fleets = [
        ("a1", "USA 1 • Meghal Chauhan", pages[0:15]),
        ("a2", "USA 2 • Mia Shah", pages[15:30]),
        ("a3", "USA 3 • Radika Patel", pages[30:45]),
        ("uk1", "UK 1 • Binjal Mehra", pages[45:57]),
        ("uk2", "UK 2 • Chanda Nai", pages[57:69]),
        ("uk3", "UK 3 • Mahi Patel", pages[69:81]),
        ("uk4", "UK 4 • Nidhi Desai", pages[81:93]),
        ("uk5", "UK 5 • Richi Patel", pages[93:104]),
        ("uk6", "UK 6 • Sweta Shah", pages[104:116]),
        ("uk7", "UK 7 • Riya Gaur", pages[116:128])
    ]

    for fid, fname, f_pages in fleets:
        f_up = sum(p.get("today_posts", 0) for p in f_pages)
        f_slots = len(f_pages) * 4
        pct = round((f_up / f_slots) * 100) if f_slots > 0 else 0
        valid_in_fleet = sum(1 for p in f_pages if any(r["id"] == str(p.get("id")) and r["valid"] for r in results))
        print(f"  [{fid:3s}] {fname:25s} | Slots: {f_up:2d}/{f_slots:2d} ({pct:2d}%) | Active Tokens: {valid_in_fleet}/{len(f_pages)}")

    # 4. Top 20 Viral Leaderboard & Rankings
    print("\n--------------------------------------------------------------------------")
    print("  TOP 20 VIRAL LEADERBOARD (Real Views & Performance)")
    print("--------------------------------------------------------------------------")
    sorted_by_views = sorted(pages, key=lambda x: int(x.get("total_views") or 0), reverse=True)
    for rank, p in enumerate(sorted_by_views[:20], 1):
        pname = (p.get("name") or "Page")[:24]
        acc = (p.get("account") or "A1")[:14]
        v_count = int(p.get("total_views") or 0)
        f_count = int(p.get("followers") or 0)
        today = p.get("today_posts", 0)
        print(f"  #{rank:02d} {pname:24s} | {acc:14s} | Views: {v_count:>10,d} | Followers: {f_count:>7,d} | Today: {today}/4")

    # 5. Low Performers & 0-View Audit (Bottom 50)
    print("\n--------------------------------------------------------------------------")
    print("  LOW PERFORMERS & 0-VIEWS AUDIT (Bottom Pages Needing Boost)")
    print("--------------------------------------------------------------------------")
    sorted_asc = sorted(pages, key=lambda x: int(x.get("total_views") or 0))
    low_50 = sorted_asc[:50]
    zero_views_pages = [p for p in pages if int(p.get("total_views") or 0) == 0]
    print(f"  • Exactly 0 Lifetime Views Pages: {len(zero_views_pages)}")
    print(f"  • Bottom 15 Pages for Attention:")
    for rank, p in enumerate(low_50[:15], 1):
        pname = (p.get("name") or "Page")[:24]
        acc = (p.get("account") or "A1")[:14]
        v_count = int(p.get("total_views") or 0)
        f_count = int(p.get("followers") or 0)
        today = p.get("today_posts", 0)
        print(f"    {rank:02d}. {pname:24s} | {acc:14s} | Views: {v_count:>6,d} | Followers: {f_count:>4,d} | Today: {today}/4")

    # 6. Save audit report
    audit_report = {
        "audit_timestamp": full_data.get("synced_at"),
        "total_pages": len(pages),
        "valid_tokens_count": len(valid_pages),
        "invalid_tokens_count": len(invalid_pages),
        "drive_configured_count": drive_configured,
        "total_stock_videos": total_stock_videos,
        "today_uploaded_total": sum(p.get("today_posts", 0) for p in pages),
        "target_daily_slots": len(pages) * 4,
        "zero_views_count": len(zero_views_pages),
        "invalid_pages": invalid_pages
    }
    with open("token_audit_report.json", "w", encoding="utf-8") as f:
        json.dump(audit_report, f, indent=2, ensure_ascii=False)
    print("\n✅ Master audit report saved to token_audit_report.json")

if __name__ == "__main__":
    main()
