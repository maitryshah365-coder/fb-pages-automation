# Google Drive to Facebook Pages Automation

Fully automated pipeline that takes AI-generated videos from Google Drive folders (synced from PC) and automatically posts them to Facebook Pages on schedule via GitHub Actions and Meta Graph API.

---

## Architecture Overview

```text
[PC Video Folder] ──(Google Drive Desktop Sync)──> [Google Drive Folder]
                                                          │ (Viewer Service Account)
                                                          ▼
[cron-job.org / Dispatch] ───────────► [GitHub Actions Cloud Runner]
                                                          │
                                     1. Checks SQLite duplicate guard & daily limits
                                     2. Downloads next unposted video (FIFO)
                                     3. Measures duration & aspect ratio:
                                        - 3–90s & 9:16  ──► Facebook Reels API (/<PAGE_ID>/video_reels)
                                        - >90s (5–7m)   ──► Classic Video API (/<PAGE_ID>/videos)
                                     4. Records success in SQLite (posted_videos.db)
                                     5. Auto-commits database back to repository
```

---

## Project Structure

```text
├── .github/workflows/post.yml     # GitHub Actions workflow (dispatch, cron, state commit)
├── config.yaml                    # 6 Facebook Pages configuration
├── data/
│   └── posted_videos.db          # SQLite persistent state (WAL mode, duplicate protection)
├── scripts/
│   ├── exchange_tokens.py         # Helper to convert user token to permanent page tokens
│   └── validate_config.py         # Pre-flight YAML configuration validator
├── src/
│   ├── config.py                  # Pydantic/dataclass config loader
│   ├── db.py                      # SQLite database manager
│   ├── drive_client.py            # Google Drive Service Account client
│   ├── facebook_client.py         # Meta Graph API client (Reels + Classic Video)
│   ├── notifier.py                # Discord execution alerts
│   ├── page_runner.py             # Page coordinator with failure isolation
│   ├── retry.py                   # Exponential backoff and error classification
│   └── video_utils.py             # Video duration/dimension probing & route detection
├── tests/                         # 12 automated unit tests (DB, routing, isolation)
├── main.py                        # CLI entry point
├── requirements.txt               # Dependencies
└── .gitignore                     # Git rules (prevents secret leaks)
```

---

## Setup & Onboarding Guide

### 1. Google Cloud Service Account
1. Create a dedicated Service Account in Google Cloud Console.
2. Enable the **Google Drive API**.
3. Create and download a JSON key.
4. Add the JSON key content into GitHub Secret: `GDRIVE_SERVICE_ACCOUNT_JSON`.
5. Share each Facebook Page's Google Drive folder with the Service Account email (`Viewer` role).

### 2. Meta App & Facebook Tokens
1. In Meta for Developers, create an App (Use Case: Other / Business).
2. Request permissions: `pages_show_list`, `pages_manage_posts`, `pages_read_engagement`.
3. Obtain a short-lived User Access Token from Graph API Explorer.
4. Run the helper to generate permanent Page Access Tokens:
   ```bash
   python scripts/exchange_tokens.py --app-id <META_APP_ID> --app-secret <META_APP_SECRET> --user-token <USER_TOKEN>
   ```
5. Add the generated Page Tokens into GitHub Secrets:
   - `FB_TOKEN_PAGE_1`
   - `FB_TOKEN_PAGE_2`
   - `FB_TOKEN_PAGE_3`
   - `FB_TOKEN_PAGE_4`
   - `FB_TOKEN_PAGE_5`
   - `FB_TOKEN_PAGE_6`

### 3. Running Locally / Dry Run
```bash
# Test configuration
python scripts/validate_config.py config.yaml

# Run dry-run (no Facebook post made)
python main.py --dry-run

# Run automated test suite
python -m pytest tests/ -v
```
