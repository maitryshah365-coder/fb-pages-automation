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

2. **Top Header Toggle -> Switch to "Live" Mode:**
   - **WHY THIS IS CRITICAL:** If an app stays in "In development" mode, Meta suppresses Reels from public recommendation (Explore/FYP feed), resulting in 0 views for all uploaded videos.
   - **Assistant Responsibility:** Proactively provide the direct dashboard link, copy-paste inputs, and verify that the toggle is flipped to **"Live"** immediately before any first video upload.

3. **No Guessing / Verification:**
   - Always verify token permissions and app live status via Graph API before scheduling bulk posts.
