"""
Patches web/index.html, docs/index.html, web/js/gold_app.js, and docs/js/gold_app.js
to register Sejal Soni (USA Account 5 - Google Pixel 9 Pro).
"""

import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def patch_html(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Drive stock strip stat: add Sejal Stock after Rohini Stock
    if "driveHeroA5Count" not in html:
        old_stat = """          <div class="strip-stat">
            <span class="stat-label"><img src="icons/us.png" alt="US" class="app-flag-icon"> Rohini Stock</span>
            <span class="stat-num" id="driveHeroA4Count" style="color: #38bdf8;">3,779 Videos</span>
          </div>"""
        new_stat = """          <div class="strip-stat">
            <span class="stat-label"><img src="icons/us.png" alt="US" class="app-flag-icon"> Rohini Stock</span>
            <span class="stat-num" id="driveHeroA4Count" style="color: #38bdf8;">3,779 Videos</span>
          </div>
          <div class="strip-stat">
            <span class="stat-label"><img src="icons/us.png" alt="US" class="app-flag-icon"> Sejal Stock</span>
            <span class="stat-num" id="driveHeroA5Count" style="color: #a78bfa;">1,376 Videos</span>
          </div>"""
        html = html.replace(old_stat, new_stat)

    # 2. Update ready folders count
    html = re.sub(r'141 / 141 Ready', '156 / 156 Ready', html)

    # 3. Add Sejal Soni filter pill in driveAccountFilters
    if "btnDriveFilterA5" not in html:
        old_pill = '<button type="button" class="timeframe-pill" data-filter="a4" id="btnDriveFilterA4"><img src="icons/us.png" alt="US" class="app-flag-icon"> Rohini Dutt (15)</button>'
        new_pill = old_pill + '\n              <button type="button" class="timeframe-pill" data-filter="a5" id="btnDriveFilterA5"><img src="icons/us.png" alt="US" class="app-flag-icon"> Sejal Soni (15)</button>'
        html = html.replace(old_pill, new_pill)
        html = html.replace('id="btnDriveFilterAll">All (141)</button>', 'id="btnDriveFilterAll">All (156)</button>')

    # 4. Meta Tools Hub header: 12 Accounts • 158 Pages
    html = html.replace("11 PROFILE ACCOUNTS • 143 PAGES", "12 PROFILE ACCOUNTS • 158 PAGES")
    html = html.replace('id="metaKpiAllPagesVal" style="color: #f1f5f9;">143 Pages</div>', 'id="metaKpiAllPagesVal" style="color: #f1f5f9;">158 Pages</div>')
    html = html.replace('<span>All 11 Accounts & Slots</span>', '<span>All 12 Accounts & Slots</span>')
    html = html.replace('id="metaKpiCleanVal" style="color: #34d399;">143 Clean (100%)</div>', 'id="metaKpiCleanVal" style="color: #34d399;">158 Clean (100%)</div>')
    html = html.replace('Showing: All 11 Accounts • All 143 Pages', 'Showing: All 12 Accounts • All 158 Pages')
    html = html.replace('<div class="meta-slot-name">All 11 Accounts</div>', '<div class="meta-slot-name">All 12 Accounts</div>')
    html = html.replace('<span>All 11 Accounts</span>', '<span>All 12 Accounts</span>')
    html = html.replace('<span class="meta-slot-badge">143 Pages</span>', '<span class="meta-slot-badge">158 Pages</span>')
    html = html.replace('Fleet Multi-Account Vault (11 Accounts)', 'Fleet Multi-Account Vault (12 Accounts)')

    # 5. Add Meta Slot Card for Sejal Soni
    if "slotCard_google_pixel9_newyork" not in html:
        old_slot = """          <!-- Slot 4: USA #4 Rohini Dutt (Samsung S25) -->
          <div class="meta-slot-card" id="slotCard_samsung_s25_newyork" onclick="filterMetaToolsByAccount('samsung_s25_newyork')">
            <div class="meta-slot-top">
              <span><img src="icons/us.png" alt="US" class="app-flag-icon"> #4 USA</span>
              <span class="meta-slot-badge">15 Pages</span>
            </div>
            <div class="meta-slot-name">Rohini Dutt</div>
            <div class="meta-slot-bottom">
              <span>⏰ 05:30 AM IST</span>
              <span>● Slot 4</span>
            </div>
          </div>"""

        new_slot = old_slot + """\n
          <!-- Slot 5: USA #5 Sejal Soni (Google Pixel 9 Pro) -->
          <div class="meta-slot-card" id="slotCard_google_pixel9_newyork" onclick="filterMetaToolsByAccount('google_pixel9_newyork')">
            <div class="meta-slot-top">
              <span><img src="icons/us.png" alt="US" class="app-flag-icon"> #5 USA</span>
              <span class="meta-slot-badge">15 Pages</span>
            </div>
            <div class="meta-slot-name">Sejal Soni</div>
            <div class="meta-slot-bottom">
              <span>⏰ 10:30 AM IST</span>
              <span>● Slot 4</span>
            </div>
          </div>"""
        html = html.replace(old_slot, new_slot)

    # 6. Add Radar Card for Sejal Soni
    if "radarCard_a5" not in html:
        old_radar = """          <div class="radar-timeline-card" id="radarCard_a4">
            <div class="radar-card-top"><span><img src="icons/us.png" alt="US" class="app-flag-icon"> #4</span><span>15 Pages</span></div>
            <div class="radar-card-name">Rohini Dutt</div>
            <div class="radar-card-time">05:30 AM IST (Slot 4)</div>
            <div class="radar-card-slots" id="radarSlots_a4">0 / 60 Slots</div>
          </div>"""

        new_radar = old_radar + """\n
          <div class="radar-timeline-card" id="radarCard_a5">
            <div class="radar-card-top"><span><img src="icons/us.png" alt="US" class="app-flag-icon"> #5</span><span>15 Pages</span></div>
            <div class="radar-card-name">Sejal Soni</div>
            <div class="radar-card-time">10:30 AM IST (Slot 4)</div>
            <div class="radar-card-slots" id="radarSlots_a5">0 / 60 Slots</div>
          </div>"""
        html = html.replace(old_radar, new_radar)

    # 7. Update other 143 counters in sidebar / headers to 158
    html = html.replace("All 143 Pages Portfolio", "All 158 Pages Portfolio")
    html = html.replace("143 Facebook Pages", "158 Facebook Pages")
    html = html.replace('>143 Pages</span>', '>158 Pages</span>')
    html = html.replace("across all 143 Facebook Pages", "across all 158 Facebook Pages")
    html = html.replace("143 Pages Monitored", "158 Pages Monitored")
    html = html.replace("143 Active Facebook Pages (572 Daily Slots)", "158 Active Facebook Pages (632 Daily Slots)")
    html = html.replace("across all 11 Accounts", "across all 12 Accounts")
    html = html.replace("11 Accounts Audit", "12 Accounts Audit")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Patched HTML: {filepath}")


def patch_js(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        js = f.read()

    # 1. Add FLEET_USA_05_IDS and FLEET_USA_05_SET
    if "FLEET_USA_05_IDS" not in js:
        target = """const FLEET_USA_04_SET = new Set(FLEET_USA_04_IDS);"""
        replacement = """const FLEET_USA_04_SET = new Set(FLEET_USA_04_IDS);

const FLEET_USA_05_IDS = [
  "534342423102401",  // The Daily Spark
  "564341273430022",  // The Chill Spot
  "497636683426759",  // Tag The
  "877069835495630",  // Stellar Vibes
  "615554031639811",  // Sovereign Collective
  "1033250263200686", // Silent Grove
  "614891248372171",  // Royal Vanguard
  "686470024541027",  // Royal Frontier
  "424138757454796",  // Rajat Gupta
  "976706512196056",  // Mouth The Hang
  "473290599201289",  // Mojo Day
  "340559612467800",  // Fly Happy
  "472703539265672",  // Flute Tomography Nature
  "502777659582958",  // Faro Fact
  "855725930966508"   // Cosmic Mirage
];

const FLEET_USA_05_SET = new Set(FLEET_USA_05_IDS);"""
        js = js.replace(target, replacement)

    # 2. Update enforceStrictFleetSorting
    if "const usa5 = [];" not in js:
        js = js.replace("const usa4 = [];", "const usa4 = [];\n  const usa5 = [];")
        
        target_sort = """  FLEET_USA_04_IDS.forEach((id, i) => {
    const p = map.get(id);
    if (p) {
      p.index = 126 + i + 1;
      p.account = "Rohini Dutt";
      p.account_owner = "Rohini Dutt";
      p.account_tag = "Rohini Dutt";
      p.account_badge = "US";
      p.box_group = "Rohini Dutt";
      p.region = "US";
      p.country = "US";
      p.flag = "icons/us.png";
      usa4.push(p);
    }
  });"""
        
        replacement_sort = target_sort + """\n
  FLEET_USA_05_IDS.forEach((id, i) => {
    const p = map.get(id);
    if (p) {
      p.index = 141 + i + 1;
      p.account = "Sejal Soni";
      p.account_owner = "Sejal Soni";
      p.account_tag = "Sejal Soni";
      p.account_badge = "US";
      p.box_group = "Sejal Soni";
      p.region = "US";
      p.country = "US";
      p.flag = "icons/us.png";
      usa5.push(p);
    }
  });"""
        js = js.replace(target_sort, replacement_sort)

        js = js.replace(
            "...FLEET_USA_04_IDS,",
            "...FLEET_USA_04_IDS, ...FLEET_USA_05_IDS,"
        )
        js = js.replace(
            "return [...usa1, ...usa2, ...usa3, ...usa4, ...uk1,",
            "return [...usa1, ...usa2, ...usa3, ...usa4, ...usa5, ...uk1,"
        )

    # 3. Update FLEET_SCHEDULE_SLOTS & radar tick
    if '{ fleetId: "a5",' not in js:
        target_radar = """  // Rohini Dutt - 15 Pages (Samsung S25 Anti-Detect Profile - Staggered Slot)
  { fleetId: "a4", name: "Rohini", flagSrc: "icons/us.png", h: 3, m: 0, label: "Slot 1" },
  { fleetId: "a4", name: "Rohini", flagSrc: "icons/us.png", h: 15, m: 0, label: "Slot 2" },
  { fleetId: "a4", name: "Rohini", flagSrc: "icons/us.png", h: 20, m: 0, label: "Slot 3" },
  { fleetId: "a4", name: "Rohini", flagSrc: "icons/us.png", h: 0, m: 0, label: "Slot 4" },"""

        replacement_radar = target_radar + """\n
  // Sejal Soni - 15 Pages (Google Pixel 9 Pro Anti-Detect Profile - Staggered Slot)
  { fleetId: "a5", name: "Sejal", flagSrc: "icons/us.png", h: 16, m: 30, label: "Slot 1" },
  { fleetId: "a5", name: "Sejal", flagSrc: "icons/us.png", h: 21, m: 30, label: "Slot 2" },
  { fleetId: "a5", name: "Sejal", flagSrc: "icons/us.png", h: 1, m: 30, label: "Slot 3" },
  { fleetId: "a5", name: "Sejal", flagSrc: "icons/us.png", h: 5, m: 0, label: "Slot 4" },"""
        js = js.replace(target_radar, replacement_radar)

        js = js.replace(
            'const fleetIds = ["a1", "a2", "a3", "a4", "uk1",',
            'const fleetIds = ["a1", "a2", "a3", "a4", "a5", "uk1",'
        )

    # 4. Update drive inventory filter logic
    if 'currentDriveAccountFilter === "a5"' not in js:
        target_f = 'const isUSA4 = (p.account && p.account.includes("Rohini")) || p.account_owner === "Rohini Dutt" || p.box_group === "Rohini Dutt";'
        replacement_f = target_f + '\n    const isUSA5 = (p.account && p.account.includes("Sejal")) || p.account_owner === "Sejal Soni" || p.box_group === "Sejal Soni";'
        js = js.replace(target_f, replacement_f)

        target_f2 = 'if (currentDriveAccountFilter === "a4" && !isUSA4) return false;'
        replacement_f2 = target_f2 + '\n    if (currentDriveAccountFilter === "a5" && !isUSA5) return false;'
        js = js.replace(target_f2, replacement_f2)

    # 5. Update badge detection
    if "isSejalPixel9" not in js:
        target_badge = """  const isRohiniS25 = acc.includes("rohini") || dev.includes("s25") || prof.includes("s25") || rohiniPages.some(rp => pName.includes(rp));
  if (isRohiniS25) {
    return `<span class="badge-device-upload" title="Emulated Mobile Device: Samsung Galaxy S25 (SM-S931U)">📱 Rohini • S25</span>`;
  }"""
        replacement_badge = """  const isRohiniS25 = acc.includes("rohini") || dev.includes("s25") || prof.includes("s25") || rohiniPages.some(rp => pName.includes(rp));
  if (isRohiniS25) {
    return `<span class="badge-device-upload" title="Emulated Mobile Device: Samsung Galaxy S25 (SM-S931U)">📱 Rohini • S25</span>`;
  }
  const sejalPages = [
    "the daily spark", "the chill spot", "tag the", "stellar vibes", 
    "sovereign collective", "silent grove", "royal vanguard", "royal frontier", 
    "rajat gupta", "mouth the hang", "mojo day", "fly happy", 
    "flute tomography nature", "faro fact", "cosmic mirage"
  ];
  const isSejalPixel9 = acc.includes("sejal") || dev.includes("pixel") || prof.includes("pixel9") || sejalPages.some(sp => pName.includes(sp));
  if (isSejalPixel9) {
    return `<span class="badge-device-upload" style="background: rgba(167,139,250,0.18); color: #c4b5fd; border: 1px solid rgba(167,139,250,0.4);" title="Emulated Mobile Device: Google Pixel 9 Pro (Tensor G4)">📱 Sejal • Pixel 9 Pro</span>`;
  }"""
        js = js.replace(target_badge, replacement_badge)

    # 6. Add Pixel 9 profile to antiDetectProfilesData
    if "google_pixel9_newyork" not in js:
        target_profile_end = """      { name: "Drift Valley", stock: 40, drive_id: "1ijqHlmfC4Ndtxlrfe_na8U55YDUUIdm6", folder: "Drift Vally", status: "Healthy" }
    ]
  }"""
        pixel_profile = """,
  {
    id: 2,
    profile_code: "USA-NYC-PIXEL9",
    name: "Google Pixel 9 Pro (US 5G)",
    model: "Pixel 9 Pro (Tensor G4)",
    owner: "Sejal Soni",
    fb_uid: "61560847721711",
    country: "USA",
    country_flag: "🇺🇸",
    region: "New York City, NY",
    timezone: "America/New_York (EDT / UTC-4)",
    dedicated_ip: "207.244.71.84 (NYC Dedicated WireGuard Proxy)",
    cookie_status: "ACTIVE",
    cookie_age_text: "Session Active (Long-Lived Meta Cookie)",
    cookie_health_score: "100%",
    total_pages: 15,
    stock_videos: 1376,
    stock_gb: "18.42 GB",
    missed_uploads: 0,
    daily_quota: 15,
    today_uploaded: 0,
    status_summary: "All 15 Pages In Sync • 0 Uploads Missed",
    fingerprint: {
      os: "Android 15 (VanillaIceCream)",
      build: "AP2A.240905.003",
      browser: "Chrome Mobile 134.0.6998.39",
      screen: "1280 x 2856 (495 dpi, 120Hz)",
      gpu: "Mali-G715-Immortalis (Google Tensor G4)",
      webrtc: "Protected (Disabled / Isolated via WireGuard)",
      canvas: "Anti-Fingerprint Noise Injected (Emulated)"
    },
    pages: [
      { name: "The Daily Spark", stock: 100, drive_id: "16deNYAwBPFU7bcXZffCt2F242_XeRvIP", folder: "The Daily Spark", status: "Healthy" },
      { name: "The Chill Spot", stock: 100, drive_id: "1wlxFyUlGpV6DAxmdFGhwzF-qr5fgpVsZ", folder: "The Chill Spot", status: "Healthy" },
      { name: "Tag The", stock: 100, drive_id: "1sNeSPh3H1oXsUzw_YDmX05785CfSZM7Z", folder: "Tag The", status: "Healthy" },
      { name: "Stellar Vibes", stock: 31, drive_id: "1PMJMCJoEV45xiwmwZAaf2Cgd4rAPWcFl", folder: "Stellar Vibes", status: "Healthy" },
      { name: "Sovereign Collective", stock: 100, drive_id: "1HQ_2ceD-v7Iqtssorncua3uTMcPjnOAt", folder: "Sovereign Collective", status: "Healthy" },
      { name: "Silent Grove", stock: 100, drive_id: "1aqXzEdvtktCUAiVQrr-jxDIjJv0EDOdy", folder: "Silent Grove", status: "Healthy" },
      { name: "Royal Vanguard", stock: 100, drive_id: "1az7G3sOLUye-d0eK5KyBjFD2ui28oPOU", folder: "Royal Vanguard", status: "Healthy" },
      { name: "Royal Frontier", stock: 45, drive_id: "18LJsnXYPZPmPiX922GOyJaahKkIv01_J", folder: "Royal Frontier", status: "Healthy" },
      { name: "Rajat Gupta", stock: 100, drive_id: "1LmV-QtwmaYJqoDr0sQDed5OUquuG8hs0", folder: "Rajat Gupta", status: "Healthy" },
      { name: "Mouth The Hang", stock: 100, drive_id: "1TIerIl5QqwzCd8eqSvlE_s_d2RHVnXJR", folder: "Mouth The hang", status: "Healthy" },
      { name: "Mojo Day", stock: 100, drive_id: "1VDhDcsjoTuDC-cEKX7g2zbObpGoXGWql", folder: "Mojo Day", status: "Healthy" },
      { name: "Fly Happy", stock: 100, drive_id: "1DlktXP7xXLii0FqeKsZpZnlIYQkjbYyH", folder: "Fly Happy", status: "Healthy" },
      { name: "Flute Tomography Nature", stock: 100, drive_id: "1FIoYms_6U3QdS35BHu7Cbblymf-JSZTk", folder: "Flute Tomography Nature", status: "Healthy" },
      { name: "Faro Fact", stock: 100, drive_id: "1SZRdbiRk6ggCzlWOsSrw-e30wr6DUMqM", folder: "Faro Fact", status: "Healthy" },
      { name: "Cosmic Mirage", stock: 100, drive_id: "1lGnNIqIhLiW7xnU0HWKV-OXxwSCMDcN1", folder: "Cosmic Mirage", status: "Healthy" }
    ]
  }"""
        js = js.replace(target_profile_end, target_profile_end + pixel_profile)

    # 7. Update runDeviceDiagnostic to handle deviceId 2 (Pixel 9)
    if "isPixel" not in js:
        target_diag_start = """  showToast("📱 Starting Real-Time S25 Device & Cookie Audit...");
  logDeviceTerminal(deviceId, "=======================================================================", "header");
  logDeviceTerminal(deviceId, "🚀 INITIATING REAL-TIME S25 HARDWARE & COOKIE INTEGRITY AUDIT", "header");
  logDeviceTerminal(deviceId, "=======================================================================", "header");"""
        
        replacement_diag_start = """  const isPixel = (deviceId === 2 || String(deviceId).includes("pixel") || String(deviceId).includes("sejal"));
  const devTitle = isPixel ? "PIXEL 9 PRO (SEJAL SONI)" : "S25 (ROHINI DUTT)";
  showToast(`📱 Starting Real-Time ${devTitle} Device & Cookie Audit...`);
  logDeviceTerminal(deviceId, "=======================================================================", "header");
  logDeviceTerminal(deviceId, `🚀 INITIATING REAL-TIME ${devTitle} HARDWARE & COOKIE INTEGRITY AUDIT`, "header");
  logDeviceTerminal(deviceId, "=======================================================================", "header");"""
        js = js.replace(target_diag_start, replacement_diag_start)

        # Dynamic hardware line
        target_hw = 'logDeviceTerminal(deviceId, "Verifying hardware profile: Samsung Galaxy S25 (SM-S931U • Android 15)...", "step");'
        replacement_hw = 'logDeviceTerminal(deviceId, isPixel ? "Verifying hardware profile: Google Pixel 9 Pro (Tensor G4 • Android 15)..." : "Verifying hardware profile: Samsung Galaxy S25 (SM-S931U • Android 15)...", "step");'
        js = js.replace(target_hw, replacement_hw)

        target_emu = 'logDeviceTerminal(deviceId, "Emulation Verified: Snapdragon 8 Elite • Chrome 134 • Canvas/WebGL Noise Active • WebRTC Isolated", "success");'
        replacement_emu = 'logDeviceTerminal(deviceId, isPixel ? "Emulation Verified: Google Tensor G4 • Mali-G715 • Chrome 134 • Canvas/WebGL Noise Active • WebRTC Isolated" : "Emulation Verified: Snapdragon 8 Elite • Chrome 134 • Canvas/WebGL Noise Active • WebRTC Isolated", "success");'
        js = js.replace(target_emu, replacement_emu)

        target_fetch = """  logDeviceTerminal(deviceId, "Querying live session cookie vault from data/profiles/samsung_s25_newyork/cookies.json...", "step");
  
  let healthData = null;
  try {
    const res = await fetch(`data/s25_device_health.json?v=${Date.now()}`, { cache: "no-store" });
    if (res.ok) {
      healthData = await res.json();
    }
  } catch (err) {
    console.warn("Could not fetch s25_device_health.json directly:", err);
  }"""
        
        replacement_fetch = """  const healthFile = isPixel ? "data/pixel9_device_health.json" : "data/s25_device_health.json";
  const cookiePath = isPixel ? "data/profiles/google_pixel9_newyork/cookies.json" : "data/profiles/samsung_s25_newyork/cookies.json";
  logDeviceTerminal(deviceId, `Querying live session cookie vault from ${cookiePath}...`, "step");
  
  let healthData = null;
  try {
    const res = await fetch(`${healthFile}?v=${Date.now()}`, { cache: "no-store" });
    if (res.ok) {
      healthData = await res.json();
    }
  } catch (err) {
    console.warn(`Could not fetch ${healthFile} directly:`, err);
  }"""
        js = js.replace(target_fetch, replacement_fetch)

        target_cuser = """  // Fallback defaults if healthData fetch failed
  const cUser = healthData?.cookies?.c_user || "61570977560611";"""
        replacement_cuser = """  // Fallback defaults if healthData fetch failed
  const cUser = healthData?.cookies?.c_user || (isPixel ? "61560847721711" : "61570977560611");
  const ownerName = isPixel ? "Sejal Soni" : "Rohini Dutt";"""
        js = js.replace(target_cuser, replacement_cuser)

        js = js.replace(
            'Owner: Rohini Dutt',
            'Owner: ${ownerName}'
        )

    # 8. Add Sejal Soni to multi-account vault in renderMetaToolsHubView
    if 'id: "google_pixel9_newyork"' not in js:
        target_acc_list = """      { id: "samsung_s25_newyork", name: "Samsung S25 (Rohini Dutt)", region: "US", flag: "🇺🇸", pages: 15, status: "LIVE", cookies: "10 Cookies Active", time: "364.9d left" },"""
        replacement_acc_list = target_acc_list + """\n      { id: "google_pixel9_newyork", name: "Pixel 9 Pro (Sejal Soni)", region: "US", flag: "🇺🇸", pages: 15, status: "LIVE", cookies: "10 Cookies Active", time: "364.9d left" },"""
        js = js.replace(target_acc_list, replacement_acc_list)

    # 9. Update fleetConfigs in renderAuditorTerminal
    if 'owner: "Sejal Soni"' not in js:
        target_fcfg = """    { tag: "USA 4", owner: "Rohini Dutt", set: FLEET_USA_04_SET, startIdx: 127, endIdx: 141, flag: "🇺🇸", flagImg: "icons/us.png", isDeviceProfile: true, deviceName: "Samsung Galaxy S25 (SM-S931U)" }"""
        replacement_fcfg = target_fcfg + """,\n    { tag: "USA 5", owner: "Sejal Soni", set: FLEET_USA_05_SET, startIdx: 142, endIdx: 156, flag: "🇺🇸", flagImg: "icons/us.png", isDeviceProfile: true, deviceName: "Google Pixel 9 Pro (Tensor G4)" }"""
        js = js.replace(target_fcfg, replacement_fcfg)

    # 10. Update fleet count string
    js = js.replace("across 11 Fleets...", "across 12 Fleets...")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(js)
    print(f"✅ Patched JS: {filepath}")


def main():
    patch_html(os.path.join(BASE_DIR, "web", "index.html"))
    patch_html(os.path.join(BASE_DIR, "docs", "index.html"))
    patch_js(os.path.join(BASE_DIR, "web", "js", "gold_app.js"))
    patch_js(os.path.join(BASE_DIR, "docs", "js", "gold_app.js"))
    print("\n🎉 ALL FRONTEND FILES SUCCESSFULLY PATCHED FOR SEJAL SONI!")


if __name__ == "__main__":
    main()
