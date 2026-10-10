# Project Master Guidelines & Permanent Memory (Facebook Reels Automation)

## 🚨 1000% MANDATORY RULE: Facebook App "Live Mode" & Compliance Setup

Whenever a new Facebook ID or Meta Developer App is created, the assistant MUST proactively guide and ensure that all of the following steps are **1000% completed without asking the user to remember**:

1. **Meta App Basic Settings (`/settings/basic/`):**
   - **App domains:** `maitryshah365-coder.github.io`
   - **Privacy Policy URL:** `https://maitryshah365-coder.github.io/fb-pages-automation/privacy.html`
   - **User data deletion:** Dropdown "Data deletion instructions URL" with value: `https://maitryshah365-coder.github.io/fb-pages-automation/data-deletion.html`
   - **Category:** `"Business and Pages"`
   - **App icon:** Upload square 512x512 icon (located at `docs/icons/icon-512.png` or project assets).
   - **Add Platform:** `+ Add platform` -> `Website` -> Site URL: `https://maitryshah365-coder.github.io/fb-pages-automation/`
   - **Save changes:** Must click Save Changes button.

2. **Top Header Toggle -> Switch to "Live" Mode & Automated Verification:**
   - **WHY THIS IS CRITICAL:** If an app stays in "In development" mode, Meta suppresses Reels from public recommendation (Explore/FYP feed), resulting in 0 views for all uploaded videos.
   - **Assistant Responsibility (1000% Enforced):** The assistant is DIRECTLY RESPONSIBLE for verifying whether every Meta App is published/live. When setup is done or when auditing, the assistant MUST run an automated check to verify that:
     1. App is in Live Mode (not in Development).
     2. Privacy policy URL is set (`privacy.html`).
     3. User data deletion URL is set (`data-deletion.html`).
     4. App domain is set (`maitryshah365-coder.github.io`).
     5. App icon and Website platform are configured.
   - The assistant MUST NEVER ask the user to remember this; it must be checked and reported proactively in every verification report.

3. **No Guessing / Verification Checklist:**
   - Always verify token permissions, app publish/live status, and view metrics via Graph API before scheduling bulk posts.

## 🛑 ABSOLUTE PERMANENT RULE: ZERO ANTI-DETECT / ZERO DEVICE PROFILES
- **NEVER MENTION OR REFER TO:** "Anti-detect", "device profile", "Pixel 9", "Samsung S25", "mobile emulation", "WireGuard proxy", or "phone hardware mock" in ANY current or future chat!
- **Pure Server-to-Server Meta Graph API (v20.0):** All accounts (USA 1-5, UK 1-7, including Sejal Soni and Rohini Dutt) use standard Facebook Page Access Tokens (`pages_show_list`, `pages_read_engagement`, `pages_manage_posts`) with direct Graph API posting (`main.py`, `src/facebook_client.py`) and Google Drive API (`src/drive_client.py`).
- Any assistant working on this project MUST NEVER mention, suggest, or output device profile logs or anti-detect systems under any circumstance.

---

## 📋 MANDATORY PRODUCTION AUDIT CHECKLIST & PROTOCOL (100% Autonomous)

Whenever the user says **"Audit"**, **"audit karo"**, **"check karo"**, **"sab check kiya jaye"**, or **"koi gap to nahi"**, the assistant MUST autonomously execute this full verification battery without waiting for the user to list individual items. If any gap or discrepancy is found, it must be fixed immediately.

### 1. Data Accuracy & Ground Truth Enforcement ("Hawa Me Data Nahi")
- **Zero Arbitrary Multipliers:** Absolutely NO hardcoded scaling fractions (`* 0.35`, `* 0.76`, `* 0.88`, `* (days / 30)`) anywhere in UI or backend.
- **Strict Timeframe Fidelity:**
  - Supported timeframes: `Today (1D)`, `7 Days (7D)`, `15 Days (15D)`, `28 Days (28D)`, `30 Days (30D)`, `60 Days (60D)`, `90 Days (90D)`, `All Time / Life`.
  - For any numeric timeframe ($N$ days): Count ONLY reels published within that exact date window via `getReelsForDays(videos, N)`. The views metric must equal the exact sum of views of those reels.
  - For `All Time` / `Life`: Use verified lifetime page views `Math.max(total_views, reelsSum)`.
- **Zero-Views Authenticity:** If a page or reel has 0 views in the chosen timeframe, it MUST display `0` (or `🔴 0 VIEWS`). Never fallback to lifetime views or percentage estimates.

### 2. Underperformers & 0-Views Directory Audit (Mode 2)
- **Filter-Before-Slice Rule:** Always filter the COMPLETE fleet pool (all pages) by `currentLowFilter` (`zero`, `under500`, `gap`) BEFORE slicing to 50. Never slice to 50 first, which falsely hides matching channels.
- **KPI Accuracy:** Ensure `🔴 Strictly 0 Views`, `🟡 Low Velocity (< 500 Views)`, and `⏳ Upload Gap (> 3 Days)` badges and counts strictly reflect live data for the selected timeframe.
- **Action Links:** Ensure each underperformer row provides direct links (`🎬 FB ↗` and `🚀 Post Reel` launcher).

### 3. Top Performers Viral Leaderboard Audit (Mode 1)
- **Rank Integrity:** Top 50 channels must be sorted strictly by actual timeframe views descending, with proper ties broken by engagement and followers.
- **Champion Podium:** Podium (#1 Gold, #2 Silver, #3 Bronze) must show 100% real numbers, correct viral reel thumbnails, and true timeframe engagement.

### 4. Fleet & Channel Identity Integrity
- **Human-Readable Names:** Every page must display its resolved title (e.g. `Crafty Champions`, `Apex House`), never raw numeric IDs or corrupt labels like `Page 142`.
- **Avatar Fallback:** Ensure all image tags have valid Graph API fallbacks: `https://graph.facebook.com/v20.0/{pid}/picture?type=large`.
- **Fleet Tagging:** Verify all accounts (USA 1 to 5, UK 1 to 7) are mapped to their respective account managers.

### 5. Deployment & Codebase Mirroring
- **`web/` vs `docs/` Synchronization:** Both directories must be identical. Any edit in `docs/` must be immediately mirrored to `web/` (and vice-versa).
- **Automated Test Battery:** Run and verify 100% pass on:
  1. `node tests/test_audit_timeframes_and_0view.js`
  2. `node tests/test_gold_app_execution.js`
  3. `node tests/test_page_name_display.js`
  4. `python -m pytest tests/test_config.py tests/test_db.py tests/test_video_routing.py tests/test_page_isolation.py`


