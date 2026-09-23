import os
import sys
import argparse
import logging
import json
import requests
import time
import random
from datetime import datetime, timezone
from src.config import load_config
from src.db import DatabaseManager
from src.drive_client import DriveClient
from src.notifier import DiscordNotifier
from src.page_runner import PageRunner


def setup_logging() -> logging.Logger:
    """Configures structured logging to console and log files."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/run_{timestamp}.log"

    logger = logging.getLogger("fb_automation")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    c_handler = logging.StreamHandler(sys.stdout)
    c_handler.setFormatter(formatter)
    logger.addHandler(c_handler)

    # File Handler
    f_handler = logging.FileHandler(log_file, encoding="utf-8")
    f_handler.setFormatter(formatter)
    logger.addHandler(f_handler)

    return logger


def probe_runner_telemetry() -> dict:
    """Dynamically probes the public IP and geolocation of the runner environment."""
    env_geo = os.environ.get("RUNNER_GEO_JSON")
    if env_geo:
        try:
            d = json.loads(env_geo)
            if d.get("ip"):
                return d
        except Exception:
            pass

    endpoints = [
        "https://ipinfo.io/json",
        "https://ipapi.co/json",
        "https://api.ipify.org?format=json"
    ]
    for url in endpoints:
        try:
            resp = requests.get(url, timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                if "ip" in data:
                    return data
        except Exception:
            continue
    return {}


def calculate_organic_human_delay(profile_type: str, page_index: int, total_pages: int, custom_min: int = 120, custom_max: int = 480) -> tuple[int, str]:
    """
    Dual-Pattern Rotating Human Behavioral Engine:
    
    Pattern 1 (Profile A - User's Creative Burst & Break):
      - 35% Quick Post: 120s – 210s (2.0 to 3.5 min)
      - 35% Moderate Flow: 211s – 360s (3.5 to 6.0 min)
      - 30% Long Break: 361s – 510s (6.0 to 8.5 min)
      
    Pattern 2 (Profile B - Agent's Fluid Wave Drift):
      - Dynamic undulating rhythm across the playlist with micro-jitter
      - Early momentum: 110s – 230s (~1.8 - 3.8 min)
      - Mid-run review: 240s – 440s (~4.0 - 7.3 min)
      - Closing pace: 150s – 310s (~2.5 - 5.1 min)
    """
    if custom_min != 120 or custom_max != 480:
        base = random.randint(max(30, custom_min), max(custom_min + 10, custom_max))
        tag = "Custom Bound Pacing"
    elif profile_type == "PATTERN_1_BURST_BREAK":
        roll = random.random()
        if roll < 0.35:
            base = random.randint(120, 210)
            tag = "Quick Follow-up (2.0m-3.5m)"
        elif roll < 0.70:
            base = random.randint(211, 360)
            tag = "Standard Pacing (3.5m-6.0m)"
        else:
            base = random.randint(361, 510)
            tag = "Coffee/Call Break (6.0m-8.5m)"
    else:  # PATTERN_2_FLUID_WAVE
        progress = (page_index + 1) / max(1, total_pages)
        if progress < 0.35:
            base = random.randint(110, 230)
            tag = "Fresh Momentum (1.8m-3.8m)"
        elif progress < 0.75:
            base = random.randint(240, 440)
            tag = "Mid-Batch Inspection (4.0m-7.3m)"
        else:
            base = random.randint(150, 310)
            tag = "Closing Pace (2.5m-5.1m)"

    # Add random odd seconds (e.g. -13, -7, 5, 11, 17, 23) to break any round number pattern
    odd_jitter = random.choice([-13, -9, -5, 3, 7, 11, 17, 23])
    final_delay = max(90, min(540, base + odd_jitter))
    return final_delay, tag


def main():
    parser = argparse.ArgumentParser(description="Google Drive to Facebook Pages Automation Pipeline")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--page", help="Run automation for a single specific Page name")
    parser.add_argument("--dry-run", action="store_true", help="Simulate upload without publishing to Facebook")
    parser.add_argument("--require-uk", action="store_true", help="Hard Kill-Switch: Strictly abort if IP is not United Kingdom (GB)")
    parser.add_argument("--require-us", action="store_true", help="Hard Kill-Switch: Strictly abort if IP is not United States (US)")
    parser.add_argument("--delay-pattern", choices=["auto", "pattern_1", "pattern_2"], default=os.environ.get("DELAY_PATTERN", "auto"), help="Stealth human behavior profile: auto, pattern_1, or pattern_2")
    parser.add_argument("--delay-min", type=int, default=int(os.environ.get("POST_PAGE_DELAY_MIN", "120")), help="Min human delay seconds between page uploads")
    parser.add_argument("--delay-max", type=int, default=int(os.environ.get("POST_PAGE_DELAY_MAX", "480")), help="Max human delay seconds between page uploads")
    args = parser.parse_args()

    logger = setup_logging()
    logger.info("==================================================================")
    logger.info("   GOOGLE DRIVE TO FACEBOOK PAGES AUTOMATION ENGINE")
    logger.info(f"   Time: {datetime.now(timezone.utc).isoformat()} UTC")
    logger.info(f"   Config: {args.config} | Dry-Run: {args.dry_run}")
    logger.info("==================================================================")

    telemetry = probe_runner_telemetry()
    if telemetry.get("ip"):
        loc = ", ".join(filter(None, [telemetry.get("city"), telemetry.get("region"), telemetry.get("country")]))
        logger.info(f"Runner Cloud IP: {telemetry.get('ip')} | Location: {loc} | Org: {telemetry.get('org', 'Unknown')}")

    # HARD FAIL-SAFE KILL-SWITCH: Enforce UK Egress if requested
    require_uk = args.require_uk or os.environ.get("REQUIRE_UK_IP", "").lower() in ["true", "1", "yes"]
    if require_uk:
        detected_country = (telemetry.get("country") or "").strip().upper()
        if detected_country not in ["GB", "UK"]:
            logger.critical("==================================================================")
            logger.critical("🚨 HARD KILL-SWITCH ACTIVATED: IP IS NOT IN THE UNITED KINGDOM!")
            logger.critical(f"   Detected Country: '{detected_country}' | IP: {telemetry.get('ip')}")
            logger.critical("   ABORTING ENTIRE PIPELINE TO PREVENT NON-UK UPLOADS.")
            logger.critical("==================================================================")
            sys.exit(1)
        else:
            logger.info(f"🛡️ UK VERIFICATION CONFIRMED: Egress IP {telemetry.get('ip')} is located in United Kingdom ({telemetry.get('city')}, {detected_country}). Safe to upload!")

    # HARD FAIL-SAFE KILL-SWITCH: Enforce US Egress if requested
    require_us = args.require_us or os.environ.get("REQUIRE_US_IP", "").lower() in ["true", "1", "yes"]
    if require_us:
        detected_country = (telemetry.get("country") or "").strip().upper()
        if detected_country not in ["US", "USA"]:
            logger.critical("==================================================================")
            logger.critical("🚨 HARD KILL-SWITCH ACTIVATED: IP IS NOT IN THE UNITED STATES!")
            logger.critical(f"   Detected Country: '{detected_country}' | IP: {telemetry.get('ip')}")
            logger.critical("   ABORTING ENTIRE PIPELINE TO PREVENT NON-US UPLOADS.")
            logger.critical("==================================================================")
            sys.exit(1)
        else:
            logger.info(f"🛡️ US VERIFICATION CONFIRMED: Egress IP {telemetry.get('ip')} is located in United States ({telemetry.get('city')}, {detected_country}). Safe to upload!")

    try:
        config = load_config(args.config)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)

    # Resolve Drive Service Account Credentials
    service_account_data = (
        os.environ.get("GDRIVE_SERVICE_ACCOUNT_JSON") or
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or
        "service_account.json"
    )

    drive_client = None
    if os.path.exists(service_account_data) or (service_account_data and "{" in service_account_data):
        try:
            drive_client = DriveClient(service_account_data)
            logger.info("Google Drive service account client initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing Google Drive client: {e}")
    else:
        logger.warning("No Google Drive service account credentials provided (set GDRIVE_SERVICE_ACCOUNT_JSON env var).")

    db = DatabaseManager(config.database_path)
    notifier = DiscordNotifier(
        webhook_url=config.notifications.discord_webhook_url,
        enabled=config.notifications.discord_enabled
    )

    runner = PageRunner(
        config=config,
        db=db,
        drive_client=drive_client,
        notifier=notifier,
        dry_run=args.dry_run,
        runner_telemetry=telemetry
    )

    pages_to_run = config.pages
    if args.page:
        raw_items = [x.strip(' "\'').strip() for x in args.page.split(",") if x.strip(' "\'').strip()]
        selected = []
        for item in raw_items:
            p = config.get_page_by_name(item) or config.get_page_by_id(item)
            if not p:
                for cand in config.pages:
                    if item.lower() in [cand.name.lower(), cand.page_id.lower()]:
                        p = cand
                        break
            if p and p not in selected:
                selected.append(p)
            elif not p:
                logger.warning(f"Requested page '{item}' not found in configuration.")
        if not selected:
            logger.error(f"None of the specified pages '{args.page}' were found in configuration.")
            sys.exit(1)
        pages_to_run = selected

    logger.info(f"Loaded {len(pages_to_run)} Facebook Pages to evaluate in this run.")

    # Rotating Dual-Pattern Stealth Behavioral Engine
    now_utc = datetime.now(timezone.utc)
    day_num = now_utc.timetuple().tm_yday
    hour_slot = now_utc.hour

    if args.delay_pattern == "pattern_1":
        active_profile = "PATTERN_1_BURST_BREAK"
        pattern_name = "Pattern 1: Creative Burst & Break (2.0m – 8.5m)"
    elif args.delay_pattern == "pattern_2":
        active_profile = "PATTERN_2_FLUID_WAVE"
        pattern_name = "Pattern 2: Fluid Natural Wave (1.5m – 7.5m)"
    else:
        # Dynamic daily & slot-based auto-rotation: alternates naturally across days/slots
        profile_seed = (day_num * 17 + hour_slot * 31 + random.randint(1, 100)) % 2
        if profile_seed == 0:
            active_profile = "PATTERN_1_BURST_BREAK"
            pattern_name = "Pattern 1: Creative Burst & Break (2.0m – 8.5m)"
        else:
            active_profile = "PATTERN_2_FLUID_WAVE"
            pattern_name = "Pattern 2: Fluid Natural Wave (1.5m – 7.5m)"

    logger.info("🎭 ==================================================================")
    logger.info("🎭 STEALTH DUAL-PATTERN HUMAN BEHAVIORAL ENGINE ACTIVE")
    logger.info(f"🎭 Current Rotation Profile: {pattern_name}")
    logger.info("🎭 Anti-Detection: Dynamic Interval Rotation & Micro-Jitter Enforced")
    logger.info("🎭 ==================================================================")

    results = []
    total_pages = len(pages_to_run)
    for idx, page in enumerate(pages_to_run):
        try:
            res = runner.run_page(page)
            # Enrich result with human-friendly metadata
            res["page_id"] = page.page_id
            res["page_config_name"] = page.name
            res["display_name"] = getattr(page, "display_name", page.name)
            results.append(res)
        except Exception as err:
            logger.error(f"Unhandled exception while processing Page '{page.name}': {err}", exc_info=True)
            results.append({
                "status": "error",
                "page": page.name,
                "page_id": page.page_id,
                "error": str(err)
            })

        # Smart Anti-Detect Human Delay between pages to prevent Meta bot/burst-spam flagging
        # Only sleep if there is a next page to process and this is not a dry-run
        if idx < total_pages - 1 and not args.dry_run:
            last_status = results[-1].get("status")
            if last_status in ["success", "dry_run_success"]:
                jitter_s, pattern_tag = calculate_organic_human_delay(
                    active_profile, idx, total_pages, args.delay_min, args.delay_max
                )
                delay_mins = jitter_s // 60
                delay_secs = jitter_s % 60
                logger.info(f"🛡️ [Anti-Detect Protection] Post successful. Organic human pause [{pattern_tag}]: Sleeping {jitter_s}s (~{delay_mins}m {delay_secs}s) before next page ({idx + 2}/{total_pages})...")
                time.sleep(jitter_s)
            elif last_status in ["failed", "error"]:
                logger.info(f"🛡️ [Anti-Detect Protection] Cooldown pause: Sleeping 15s before next page ({idx + 2}/{total_pages})...")
                time.sleep(15)
            else:
                time.sleep(3)

    logger.info("======================= RUN SUMMARY =======================")
    for r in results:
        p_name = r.get("page", "Unknown")
        status = r.get("status", "unknown")
        detail = r.get("filename") or r.get("reason") or r.get("error") or ""
        logger.info(f"Page: {p_name:<15} | Status: {status.upper():<12} | {detail}")
    logger.info("===========================================================")

    # Export structured run summary for immediate dashboard display & auto-sync
    summary_data = {
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "run_number": os.environ.get("GITHUB_RUN_NUMBER", "1"),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "runner_telemetry": telemetry,
        "dry_run": args.dry_run,
        "results": results,
        "stats": {
            "total": len(results),
            "success": sum(1 for r in results if r.get("status") in ["success", "dry_run_success"]),
            "skipped": sum(1 for r in results if r.get("status") in ["skipped", "no_content"]),
            "failed": sum(1 for r in results if r.get("status") in ["failed", "error"])
        }
    }
    # Export structured run summary for immediate dashboard display & auto-sync (skip if local dry-run)
    if not args.dry_run or os.environ.get("GITHUB_RUN_ID"):
        for folder in ["data", "docs/data", "web/data"]:
            try:
                os.makedirs(folder, exist_ok=True)
                summary_file = os.path.join(folder, "latest_run_summary.json")
                with open(summary_file, "w", encoding="utf-8") as sf:
                    json.dump(summary_data, sf, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.warning(f"Could not write run summary to {folder}: {e}")


if __name__ == "__main__":
    main()
