import json
import requests
import yaml
import sys

def audit():
    print("=================================================================")
    print("🔍 META FACEBOOK PAGES & TOKEN HEALTH FULL AUDIT")
    print("=================================================================")

    # 1. Load config
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    cfg_pages = {str(p["page_id"]): p for p in cfg.get("pages", [])}
    print(f"Loaded {len(cfg_pages)} pages configured in config.yaml.")

    # 2. Load tokens
    with open("data/pages_tokens.json", "r", encoding="utf-8") as f:
        tokens_list = json.load(f)

    print(f"Loaded {len(tokens_list)} page tokens from data/pages_tokens.json.\n")

    audit_results = []
    expected_app_id = "1366459798891922"

    for idx, item in enumerate(tokens_list, 1):
        pid = str(item.get("id"))
        pname = item.get("name")
        token = item.get("access_token")
        cfg_entry = cfg_pages.get(pid, {})
        is_enabled = cfg_entry.get("enabled", False)
        drive_folder = cfg_entry.get("drive_folder_id", "NOT_CONFIGURED")

        # A. Debug Token API
        debug_url = f"https://graph.facebook.com/v20.0/debug_token?input_token={token}&access_token={token}"
        try:
            d_res = requests.get(debug_url, timeout=15).json()
        except Exception as e:
            d_res = {"error": str(e)}

        d_data = d_res.get("data", {})
        app_id = d_data.get("app_id")
        app_name = d_data.get("application")
        is_valid = d_data.get("is_valid", False)
        expires_at = d_data.get("expires_at")
        scopes = d_data.get("scopes", [])

        # B. Query Page Details directly via token
        me_url = f"https://graph.facebook.com/v20.0/{pid}?fields=id,name,is_published,verification_status&access_token={token}"
        try:
            me_res = requests.get(me_url, timeout=15).json()
        except Exception as e:
            me_res = {"error": str(e)}

        page_is_published = me_res.get("is_published", "Unknown")
        real_fb_name = me_res.get("name", pname)

        # Check permissions needed for Reels publishing
        has_manage_posts = "pages_manage_posts" in scopes
        has_read_eng = "pages_read_engagement" in scopes

        # Drive folder validity
        has_valid_drive = drive_folder not in ["", "NOT_CONFIGURED"] and not drive_folder.startswith("REPLACE_WITH_")

        status_flags = []
        if not is_valid:
            status_flags.append("❌ TOKEN_INVALID")
        if app_id != expected_app_id:
            status_flags.append(f"⚠️ APP_MISMATCH({app_id})")
        if not has_manage_posts:
            status_flags.append("❌ NO_PAGES_MANAGE_POSTS")
        if page_is_published is False:
            status_flags.append("⚠️ PAGE_UNPUBLISHED_ON_FB")
        if is_enabled and not has_valid_drive:
            status_flags.append("⚠️ DRIVE_FOLDER_MISSING")

        status_str = "HEALTHY" if not status_flags else " | ".join(status_flags)

        result = {
            "index": idx,
            "page_id": pid,
            "page_name": real_fb_name,
            "token_app_id": app_id,
            "token_app_name": app_name,
            "token_valid": is_valid,
            "never_expires": (expires_at == 0),
            "has_manage_posts": has_manage_posts,
            "page_is_published": page_is_published,
            "enabled_in_config": is_enabled,
            "has_valid_drive": has_valid_drive,
            "drive_folder": drive_folder,
            "status": status_str
        }
        audit_results.append(result)

        print(f"[{idx:02d}/15] Page: {real_fb_name[:22]:<22} | ID: {pid} | App: {app_name} ({app_id})")
        print(f"       Token: Valid={is_valid}, NeverExpires={expires_at == 0}, ManagePosts={has_manage_posts}")
        print(f"       FB Published: {page_is_published} | Config Enabled: {is_enabled} | Drive: {drive_folder[:18]}...")
        print(f"       Result: {'✅ ' + status_str if status_str == 'HEALTHY' else '⚠️ ' + status_str}\n")

    # Summary
    print("=================================================================")
    print("📊 AUDIT SUMMARY REPORT")
    print("=================================================================")
    all_valid = all(r["token_valid"] for r in audit_results)
    all_correct_app = all(r["token_app_id"] == expected_app_id for r in audit_results)
    all_perm = all(r["never_expires"] for r in audit_results)
    active_pages = [r for r in audit_results if r["enabled_in_config"] and r["has_valid_drive"]]
    paused_pages = [r for r in audit_results if not r["enabled_in_config"] or not r["has_valid_drive"]]

    print(f"• Total Pages Checked: {len(audit_results)}")
    print(f"• Tokens Valid & Active: {sum(1 for r in audit_results if r['token_valid'])} / {len(audit_results)}")
    print(f"• Connected to App '{expected_app_id}': {sum(1 for r in audit_results if r['token_app_id'] == expected_app_id)} / {len(audit_results)}")
    print(f"• Permanent Tokens (Never Expire): {sum(1 for r in audit_results if r['never_expires'])} / {len(audit_results)}")
    print(f"• Active Posting Channels: {len(active_pages)} (With valid Drive folders)")
    print(f"• Inactive / Placeholder Drive Channels: {len(paused_pages)}")
    print("=================================================================")

if __name__ == "__main__":
    audit()
