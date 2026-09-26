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

## 🎯 Keyword Trigger: "ANTI" (Multi-Device Anti-Detect Playwright Engine)
- Whenever the user says the keyword **"ANTI"**, the assistant must immediately recognize that the user wants to initiate the **Multi-Device Anti-Detect Playwright Engine** (Option B documented in `ANTI.md`).
- The assistant MUST NOT start coding blindly; it must first ask for confirmation:
  *"Bhai, kya hum ANTI (Multi-Device Playwright Engine) shuru karein? Kya aapke paas Account 1 ki cookies ready hain?"*
- Once confirmed by the user, proceed with phased setup according to `ANTI.md`.

## 🎯 Keyword Trigger: "WIFI" (Home WiFi Ghost Auto-Wake & Remote Telemetry Engine)
- Whenever the user says the keyword **"WIFI"**, the assistant must immediately recognize that the user wants to initiate the **Home WiFi Ghost Auto-Wake & Telemetry Engine** for Indian pages (documented in `WIFI.md`).
- The assistant MUST NOT start coding blindly; it must first ask for confirmation:
  *"Bhai, kya hum WIFI (Home WiFi Ghost Auto-Wake & Telemetry Engine) shuru karein? Kya naye Indian pages ke IDs aur tokens ready hain?"*
- Once confirmed by the user, proceed with phased setup according to `WIFI.md`.
