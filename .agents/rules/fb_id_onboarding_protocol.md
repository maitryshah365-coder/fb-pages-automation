# Complete Facebook ID Onboarding & Lifetime Token Protocol (Master Standard)

Whenever onboarding any Facebook ID (for UK London or USA setups), ALWAYS follow this exact 5-step plan in order. All URLs must be inside standalone ```text ``` copy-code blocks.

---

### Step 1: Create Meta App
- **Link:**
  ```text
  https://developers.facebook.com/apps/create/
  ```
- Select **"Other"** -> Click **Next**
- Select **"Business"** -> Click **Next**
- **App Name:** Must be EXACTLY the Facebook ID / Account Name (e.g. `Binjal Mehra`)
- Click **"Create app"** (Enter Facebook password)

---

### Step 2: App Basic Settings & MANDATORY "Live Mode" (1000% Compulsory for Views)
> **CRITICAL RULE:** Jab tak App "Live" nahi hoti, Meta Graph API se post hone wali Reels ko "Development Mode" me lock rakhta hai aur external public discovery feed me 0 views aate hain. Har nayi ID/App par ye step 1000% proactively complete karwana compulsory hai!

- **Settings Link:**
  ```text
  https://developers.facebook.com/apps/<APP_ID>/settings/basic/
  ```
- **App domains:**
  ```text
  maitryshah365-coder.github.io
  ```
- **Privacy policy URL:**
  ```text
  https://maitryshah365-coder.github.io/fb-pages-automation/privacy.html
  ```
- **User data deletion:** (Dropdown: "Data deletion instructions URL")
  ```text
  https://maitryshah365-coder.github.io/fb-pages-automation/data-deletion.html
  ```
- **Category:** Select `"Business and Pages"`
- **App icon:** Mandatory square icon (Drag & drop or upload from `docs/icons/icon-512.png` or any 512x512 square logo).
- **Add Platform:** Niche scroll karke `+ Add platform` -> `Website` select karo -> Site URL me:
  ```text
  https://maitryshah365-coder.github.io/fb-pages-automation/
  ```
- Click **"Save changes"** at the bottom right.
- **Top Header Toggle:** Top bar par **"App Mode: In development"** toggle switch par click karke **"Live"** chuno aur popup me confirm karo. Verify app is now **LIVE**.

---

### Step 3: Graph API Explorer Token
- **Link:**
  ```text
  https://developers.facebook.com/tools/explorer/
  ```
- Select the created App from the dropdown.
- "User or Page" -> "Get User Access Token".
- Add Permissions: `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`.
- Click **"Generate Access Token"** -> Popup me **"Continue"** karke saare 12 pages select karo.
- Access Token box se token (`EAA...`) copy karo.

---

### Step 4: Token Ko Life-Time (Permanent) Karna (Access Token Debugger)
- **Link:**
  ```text
  https://developers.facebook.com/tools/debug/accesstoken/
  ```
- Token paste karke **"Debug"** dabao.
- Neeche scroll karo aur **"Extend Access Token"** button par click karo.
- Lifetime extended token copy karo.

---

### Step 5: Backend Token Exchange & State Persistence
- Get **App Secret** from Basic Settings.
- Assistant runs python exchange script to generate permanent Page Access Tokens (`Expires At: 0`).
- Saves verified pages with permanent tokens to `data/` directory.
