# PERMANENT MANDATORY RULE: BAN ON ANTI-DETECT & DEVICE EMULATION

## Strict Directive
1. **NEVER mention, propose, or discuss:**
   - "Anti-detect"
   - "Device profiles" / "Phone profiles"
   - "Google Pixel 9" / "Samsung S25" emulation
   - "Mobile hardware mock" / "Canvas noise" / "WireGuard proxy"
   
2. **Current System Architecture:**
   - The system is **100% direct Server-to-Server Meta Graph API (v20.0)**.
   - All Facebook pages across all fleets (USA 1 to 5, UK 1 to 7) operate strictly via standard **Facebook Page Access Tokens** (`pages_show_list`, `pages_read_engagement`, `pages_manage_posts`).
   - All video sourcing is strictly via standard **Google Drive API** service account / OAuth.
   - All publishing executes directly via python scripts (`main.py`, `src/facebook_client.py`).

3. **Behavioral Requirement:**
   - Never reference any anti-detect profiles or device mockups in any conversation, analysis, report, or log.
   - If a page has no working token, report it simply as: **"Facebook Page Access Token missing / expired"**.
