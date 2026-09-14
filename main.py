import os
import sys
import argparse
import logging
import json
import requests
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


def main():
    parser = argparse.ArgumentParser(description="Google Drive to Facebook Pages Automation Pipeline")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--page", help="Run automation for a single specific Page name")
    parser.add_argument("--dry-run", action="store_true", help="Simulate upload without publishing to Facebook")
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
        raw_items = [x.strip() for x in args.page.split(",") if x.strip()]
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

    results = []
    for page in pages_to_run:
        try:
            res = runner.run_page(page)
            results.append(res)
        except Exception as err:
            logger.error(f"Unhandled exception while processing Page '{page.name}': {err}", exc_info=True)
            results.append({"status": "error", "page": page.name, "error": str(err)})

    logger.info("======================= RUN SUMMARY =======================")
    for r in results:
        p_name = r.get("page", "Unknown")
        status = r.get("status", "unknown")
        detail = r.get("filename") or r.get("reason") or r.get("error") or ""
        logger.info(f"Page: {p_name:<15} | Status: {status.upper():<12} | {detail}")
    logger.info("===========================================================")


if __name__ == "__main__":
    main()
