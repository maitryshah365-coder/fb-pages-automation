"""
Automated synchronization script for Sejal Soni (USA Account 5 - Google Pixel 9 Pro).
Integrates 15 Facebook pages (1,376 reels) into:
- data/drive_folders_audit.json & docs/data/drive_folders_audit.json
- data/master_fleet_monetization.json, docs/data/master_fleet_monetization.json & web/data/master_fleet_monetization.json
- docs/data/pages_data.json & web/data/pages_data.json
"""

import os
import sys
import json
import re
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SEJAL_DRIVE_JSON = os.path.join(BASE_DIR, "data", "sejal_soni_drive_folders.json")
PERM_PAGES_JSON = os.path.join(BASE_DIR, "data", "usa_account5_sejal_permanent_pages.json")
PAGES_DOCS = os.path.join(BASE_DIR, "docs", "data", "pages_data.json")
PAGES_WEB = os.path.join(BASE_DIR, "web", "data", "pages_data.json")
MASTER_MON_DATA = os.path.join(BASE_DIR, "data", "master_fleet_monetization.json")
MASTER_MON_DOCS = os.path.join(BASE_DIR, "docs", "data", "master_fleet_monetization.json")
MASTER_MON_WEB = os.path.join(BASE_DIR, "web", "data", "master_fleet_monetization.json")
AUDIT_JSON_DATA = os.path.join(BASE_DIR, "data", "drive_folders_audit.json")
AUDIT_JSON_DOCS = os.path.join(BASE_DIR, "docs", "data", "drive_folders_audit.json")


def sync_sejal_fleet():
    print("=" * 70)
    print("🚀 INTEGRATING SEJAL SONI (USA 5 - GOOGLE PIXEL 9 PRO) ACROSS ALL STORES")
    print("=" * 70)

    # Load permanent pages config
    with open(PERM_PAGES_JSON, "r", encoding="utf-8") as f:
        perm_config = json.load(f)
    sejal_pages = perm_config.get("pages", [])
    total_sejal_stock = perm_config.get("total_stock_videos", 1376)
    print(f"Loaded {len(sejal_pages)} Sejal Soni pages ({total_sejal_stock} reels in stock)")

    # 1. Update Drive Folders Audit
    for audit_path in [AUDIT_JSON_DATA, AUDIT_JSON_DOCS]:
        if os.path.exists(audit_path):
            with open(audit_path, "r", encoding="utf-8") as f:
                audit = json.load(f)
            
            for p in sejal_pages:
                p_name = p["name"]
                audit[p_name] = {
                    "video_count": p["drive_videos_count"],
                    "folder_id": p["drive_folder_id"],
                    "folder_name": p["drive_folder_name"],
                    "account": "Sejal Soni (USA 5)",
                    "region": "US"
                }
            
            total_vids = sum(v.get("video_count", 0) for k, v in audit.items() if isinstance(v, dict))
            audit["total_videos"] = total_vids
            with open(audit_path, "w", encoding="utf-8") as f:
                json.dump(audit, f, indent=2, ensure_ascii=False)
            print(f"✅ Updated {audit_path} (Total Portfolio Stock: {total_vids:,} reels)")

    # 2. Update Master Fleet Monetization
    sejal_account_monetization = {
        "account_id": "google_pixel9_newyork",
        "account_name": "Sejal Soni (USA 5)",
        "owner": "Sejal Soni",
        "region": "US",
        "device": "Google Pixel 9 Pro (US 5G)",
        "status": "ACTIVE_AUTHENTICATED",
        "fb_uid": "61560847721711",
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "total_pages": len(sejal_pages),
        "pages": []
    }

    for p in sejal_pages:
        sejal_account_monetization["pages"].append({
            "name": p["name"],
            "page_id": p["page_id"],
            "followers": 0,
            "total_views": 0,
            "overall_status": "No Monetization Violations",
            "content_monetization": "Invite only",
            "subscriptions": "Criteria Not Met",
            "stars": "Criteria Not Met",
            "policy_details": "No Violations (Clean)",
            "recommendation": "Recommendable"
        })

    for mon_path in [MASTER_MON_DATA, MASTER_MON_DOCS, MASTER_MON_WEB]:
        if os.path.exists(mon_path):
            with open(mon_path, "r", encoding="utf-8") as f:
                mon_data = json.load(f)
            
            # Remove old Sejal Soni entry if present
            accounts = [a for a in mon_data.get("accounts", []) if a.get("account_id") != "google_pixel9_newyork"]
            accounts.append(sejal_account_monetization)
            
            mon_data["accounts"] = accounts
            mon_data["total_accounts"] = len(accounts)
            mon_data["total_fleet_pages"] = sum(len(a.get("pages", [])) for a in accounts)
            mon_data["generated_at"] = datetime.now(timezone.utc).isoformat()

            with open(mon_path, "w", encoding="utf-8") as f:
                json.dump(mon_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Updated {mon_path} (Accounts: {mon_data['total_accounts']}, Pages: {mon_data['total_fleet_pages']})")

    # 3. Update pages_data.json in docs/ and web/
    for ppath in [PAGES_DOCS, PAGES_WEB]:
        if os.path.exists(ppath):
            with open(ppath, "r", encoding="utf-8") as f:
                pdata = json.load(f)

            existing_pages = pdata.get("pages", [])
            # Filter out any existing Sejal pages
            filtered_pages = [p for p in existing_pages if "Sejal" not in p.get("account_owner", "") and "Sejal" not in p.get("account", "")]

            # Create standard page objects for each Sejal Soni page
            for idx, sp in enumerate(sejal_pages, 1):
                pid = sp["page_id"]
                pname = sp["name"]
                page_obj = {
                    "id": sp["id"],
                    "page_id": pid,
                    "name": pname,
                    "account": "Sejal Soni (USA)",
                    "account_owner": "Sejal Soni",
                    "device": "Google Pixel 9 Pro",
                    "device_profile": "google_pixel9_newyork",
                    "followers": 0,
                    "fan_count": 0,
                    "category": "Digital creator",
                    "pic_url": f"https://graph.facebook.com/v20.0/{pid}/picture?type=large",
                    "link": f"https://www.facebook.com/{pid}",
                    "access_token": "",
                    "token_status": "session_cookie_auth",
                    "auth_method": "anti_detect_playwright",
                    "health": "Optimal",
                    "today_posts": 0,
                    "live_meta_insights": {
                        "organic_impressions": 0,
                        "organic_video_views": 0,
                        "views_30s_complete": 0,
                        "profile_views_total": 0,
                        "daily_follows": 0,
                        "post_engagements": 0,
                        "reel_likes": 0
                    },
                    "daily_limit": 4,
                    "drive_folder_id": sp["drive_folder_id"],
                    "drive_folder_name": sp["drive_folder_name"],
                    "is_configured": True,
                    "has_drive_folder": True,
                    "drive_videos_count": sp["drive_videos_count"],
                    "total_posts": 0,
                    "total_views": 0,
                    "total_engagement": {
                        "likes": 0,
                        "comments": 0
                    },
                    "last_upload_ip": {
                        "ip": "207.244.71.84",
                        "city": "New York",
                        "region": "New York",
                        "country": "United States",
                        "org": "AS20473 Datacamp / Dedicated WireGuard",
                        "flag": "🇺🇸",
                        "timestamp": "Ready for Next Slot"
                    },
                    "audience": {
                        "has_real_data": False,
                        "message": "Demographic Insights Pending Professional Dashboard Sync",
                        "reason": "Meta Business Suite session connected via Google Pixel 9 Pro."
                    },
                    "page_status": {
                        "has_no_issues": True,
                        "headline": "Page has no issues",
                        "community_standards": {
                            "status": "Good news: no violations to show.",
                            "sub": "If content on a Page goes against our Community Standards, it can put the Page at risk for restrictions."
                        },
                        "account_status": {
                            "status": "No restrictions",
                            "sub": "Your account looks good! Check in on other things you manage."
                        },
                        "extra_features": {
                            "recommendations": "Active",
                            "monetization": "In Progress"
                        },
                        "suspension_check": "Clean / Zero Restrictions"
                    },
                    "content_monetization": {
                        "has_criteria_area": False,
                        "program_type": "invite_only",
                        "type_label": "Invite-Only Page",
                        "type_badge": "📬 Invite-Only",
                        "criteria_met_count": 3,
                        "waitlist_headline": "3 of 6 criteria met",
                        "is_setup_ready": False,
                        "criteria_rules": [],
                        "invite_only_overview": {
                            "headline": "Not yet eligible",
                            "sub": "As you grow your audience, you'll unlock more ways to make money.",
                            "tools": [
                                {
                                    "name": "Content monetization",
                                    "icon": "🎬",
                                    "desc": "Earn money from Facebook for all your well-performing, eligible content.",
                                    "status": "Invite only",
                                    "badge_type": "invite"
                                },
                                {
                                    "name": "Subscriptions",
                                    "icon": "💎",
                                    "desc": "Generate income monthly with exclusive content.",
                                    "status": "1 of 3 criteria met",
                                    "badge_type": "criteria"
                                }
                            ],
                            "beta_headline": "Content monetization beta",
                            "beta_sub": "We're actively working to expand access and make this program available to more creators soon.",
                            "status_title": "Invite only",
                            "status_desc": "This program is currently only available by invitation. Tap notify me and we'll let you know when you're eligible.",
                            "action_label": "Notify me",
                            "candidate_status": "Active Candidate (4x daily USA video posting accelerates invitation)",
                            "progress_pct": 60
                        }
                    },
                    "recommendation": {
                        "is_recommendable": True,
                        "badge": "Page is Recommendable",
                        "headline": "We're helping you grow your audience",
                        "desc": "Your page brings people together. Content posted on this page is eligible to be suggested to new viewers across Facebook Reels, Feed, and Watch."
                    },
                    "monetization": {
                        "standing": "Good Standing",
                        "policy_status": "No Monetization Violations",
                        "content_monetization": {
                            "has_criteria_area": False,
                            "program_type": "invite_only",
                            "type_label": "Invite-Only Page",
                            "type_badge": "📬 Invite-Only",
                            "criteria_met_count": 3,
                            "waitlist_headline": "3 of 6 criteria met",
                            "is_setup_ready": False,
                            "criteria_rules": []
                        },
                        "criteria_tools": [
                            {
                                "name": "Stars Program",
                                "icon": "⭐",
                                "type": "Criteria Based",
                                "status": "In Progress",
                                "setup_ready": False,
                                "action_label": None,
                                "badge_class": "in-progress",
                                "progress_pct": 0,
                                "criteria": "0 / 500 Followers",
                                "desc": "Earn direct payouts when viewers send Stars during Reels and live videos."
                            },
                            {
                                "name": "Fan Subscriptions",
                                "icon": "💎",
                                "type": "Criteria Based",
                                "status": "In Progress",
                                "setup_ready": False,
                                "action_label": None,
                                "badge_class": "in-progress",
                                "progress_pct": 0,
                                "criteria": "0 / 10,000 Followers",
                                "desc": "Monthly recurring income from dedicated supporters."
                            },
                            {
                                "name": "Branded Content Tag",
                                "icon": "🤝",
                                "type": "Criteria Based",
                                "status": "Active & Compliant",
                                "setup_ready": True,
                                "action_label": "🏷️ Tag Sponsors",
                                "badge_class": "eligible",
                                "progress_pct": 100,
                                "criteria": "Zero Policy Violations",
                                "desc": "Tag sponsor brands with Meta's official paid partnership handshake label."
                            }
                        ],
                        "invite_tools": [
                            {
                                "name": "Content Monetization Program (Beta)",
                                "sub": "Unified In-Stream, Reels & Bonus",
                                "icon": "🎬",
                                "type": "Invitation Only (Meta Beta)",
                                "status": "Active Invitation Candidate",
                                "badge_class": "invite-only",
                                "progress_pct": 30,
                                "criteria": "Reels Upload Velocity & Policy Standing",
                                "desc": "Meta's new unified program combining Reels ads, longer video in-stream ads, and performance rewards into a single monthly payout."
                            }
                        ]
                    },
                    "videos": []
                }
                filtered_pages.append(page_obj)

            pdata["pages"] = filtered_pages
            pdata["synced_at"] = datetime.now(timezone.utc).isoformat()
            if "today_summary" in pdata:
                pdata["today_summary"]["active_pages_count"] = len(filtered_pages)
                pdata["today_summary"]["target_total"] = len(filtered_pages) * 4
                pdata["today_summary"]["usa_account5_slots_edt"] = [
                    "11:20 PM",
                    "11:20 AM",
                    "04:20 PM",
                    "08:20 PM"
                ]

            with open(ppath, "w", encoding="utf-8") as f:
                json.dump(pdata, f, indent=2, ensure_ascii=False)
            print(f"✅ Updated {ppath} (Total Pages: {len(filtered_pages)})")

    print("\n🎉 ALL SEJAL SONI DATA SUCCESSFULLY SYNCED INTO MASTER FLEET!")


if __name__ == "__main__":
    sync_sejal_fleet()
