#!/usr/bin/env python3
"""
UK Fleet Execution Dispatcher
Handles single page, multiple comma-separated pages, or account-level runs
for UK 01 (Binjal), UK 02 (Chanda), and UK 03 (Mahi).
"""

import sys
import subprocess
import yaml
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_uk_pages.py <req_pages> [--dry-run]")
        sys.exit(1)
        
    req = sys.argv[1].strip()
    is_dry = "--dry-run" in sys.argv
    dry_flag = ["--dry-run"] if is_dry else []
    
    configs = [
        ("config_uk_account1.yaml", "UK Account 1 (Binjal Mehra)"),
        ("config_uk_account2.yaml", "UK Account 2 (Chanda Nai)"),
        ("config_uk_account3.yaml", "UK Account 3 (Mahi Patel)"),
        ("config_uk_account4.yaml", "UK Account 4 (Nidhi Desai)")
    ]

    # Whole account shorthand
    if req in ["uk_account_1", "uk1"]:
        print("🚀 [UK RUNNER] Running full UK Account 1 (12 Pages)...")
        subprocess.run([sys.executable, "main.py", "--config", "config_uk_account1.yaml", "--require-uk"] + dry_flag, check=False)
        return
    elif req in ["uk_account_2", "uk2"]:
        print("🚀 [UK RUNNER] Running full UK Account 2 (12 Pages)...")
        subprocess.run([sys.executable, "main.py", "--config", "config_uk_account2.yaml", "--require-uk"] + dry_flag, check=False)
        return
    elif req in ["uk_account_3", "uk3"]:
        print("🚀 [UK RUNNER] Running full UK Account 3 (12 Pages)...")
        subprocess.run([sys.executable, "main.py", "--config", "config_uk_account3.yaml", "--require-uk"] + dry_flag, check=False)
        return
    elif req in ["uk_account_4", "uk4"]:
        print("🚀 [UK RUNNER] Running full UK Account 4 (12 Pages)...")
        subprocess.run([sys.executable, "main.py", "--config", "config_uk_account4.yaml", "--require-uk"] + dry_flag, check=False)
        return

    # Comma-separated list of pages
    items = [x.strip() for x in req.split(",") if x.strip()]
    ran_any = False

    for cfg_file, name in configs:
        if not Path(cfg_file).exists():
            continue
        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                cdata = yaml.safe_load(f) or {}
            cfg_page_ids = set()
            for p in cdata.get("pages", []):
                cfg_page_ids.add(str(p.get("id", "")).strip())
                cfg_page_ids.add(str(p.get("name", "")).strip().lower())
                cfg_page_ids.add(str(p.get("display_name", "")).strip().lower())

            matched = []
            for itm in items:
                itm_clean = itm.strip()
                if (itm_clean in cfg_page_ids or 
                    itm_clean.lower() in cfg_page_ids or 
                    any(itm_clean.lower() == str(x).lower() for x in cfg_page_ids)):
                    matched.append(itm_clean)

            if matched:
                ran_any = True
                print(f"🚀 [UK RUNNER] Dispatching {name} for {len(matched)} pages: {matched}")
                cmd = [sys.executable, "main.py", "--config", cfg_file, "--page", ",".join(matched), "--require-uk"] + dry_flag
                subprocess.run(cmd, check=False)
        except Exception as e:
            print(f"Error processing {cfg_file}: {e}")

    if not ran_any:
        print(f"⚠️ No direct page matches found, executing fallback with direct page arg: {req}")
        if "uk4" in req.lower():
            subprocess.run([sys.executable, "main.py", "--config", "config_uk_account4.yaml", "--page", req, "--require-uk"] + dry_flag, check=False)
        elif "uk3" in req.lower():
            subprocess.run([sys.executable, "main.py", "--config", "config_uk_account3.yaml", "--page", req, "--require-uk"] + dry_flag, check=False)
        elif "uk2" in req.lower():
            subprocess.run([sys.executable, "main.py", "--config", "config_uk_account2.yaml", "--page", req, "--require-uk"] + dry_flag, check=False)
        else:
            subprocess.run([sys.executable, "main.py", "--config", "config_uk_account1.yaml", "--page", req, "--require-uk"] + dry_flag, check=False)

if __name__ == "__main__":
    main()
