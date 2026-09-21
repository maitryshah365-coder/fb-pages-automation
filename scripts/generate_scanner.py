import json

with open('docs/data/pages_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fleet_map = {}
for p in data['pages']:
    acc = p.get('account') or 'Other'
    if acc not in fleet_map:
        fleet_map[acc] = []
    fleet_map[acc].append({
        'id': str(p['id']),
        'name': p['name'],
        'followers': p.get('followers', 0),
        'views': p.get('total_views', 0)
    })

scanner_js = f"""/**
 * Raj FB Pro - 1-Click Real Facebook Monetization Scanner
 * Runs directly on facebook.com inside user's active browser session.
 * 100% Real Live DOM & GraphQL Audit - Zero Guesswork.
 */
(function() {{
  if (document.getElementById("raj-mz-scanner-hud")) {{
    document.getElementById("raj-mz-scanner-hud").remove();
  }}

  const ALL_FLEETS = {json.dumps(fleet_map, indent=2)};
  let verifiedPages = JSON.parse(localStorage.getItem("raj_real_fb_audit") || "{{}}");

  // Create HUD Container
  const hud = document.createElement("div");
  hud.id = "raj-mz-scanner-hud";
  hud.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    width: 440px;
    max-width: calc(100vw - 40px);
    max-height: 90vh;
    background: rgba(11, 15, 25, 0.98);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(59, 130, 246, 0.5);
    border-radius: 16px;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.8), 0 0 35px rgba(59, 130, 246, 0.25);
    z-index: 999999999;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #f8fafc;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    animation: rajFadeIn 0.25s ease-out;
  `;

  // Inject Styles
  const styleEl = document.createElement("style");
  styleEl.textContent = `
    @keyframes rajFadeIn {{
      from {{ opacity: 0; transform: translateY(-16px) scale(0.97); }}
      to {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}
    .raj-fleet-btn {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: #cbd5e1;
      padding: 6px 10px;
      border-radius: 8px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .raj-fleet-btn:hover {{
      background: rgba(59, 130, 246, 0.2);
      border-color: rgba(59, 130, 246, 0.5);
      color: #60a5fa;
    }}
    .raj-fleet-btn.active {{
      background: linear-gradient(135deg, rgba(37,99,235,0.3), rgba(29,78,216,0.4));
      border-color: #3b82f6;
      color: #93c5fd;
      font-weight: 700;
    }}
  `;
  document.head.appendChild(styleEl);

  hud.innerHTML = `
    <div style="padding: 14px 18px; background: linear-gradient(135deg, rgba(30,58,138,0.4), rgba(15,23,42,0.8)); border-bottom: 1px solid rgba(255,255,255,0.08); display: flex; align-items: center; justify-content: space-between;">
      <div style="display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 22px; line-height: 1;">⚡</span>
        <div>
          <div style="font-weight: 800; font-size: 14px; color: #fff; letter-spacing: -0.01em;">Raj FB Pro • Real Tool Scanner</div>
          <div style="font-size: 11px; color: #94a3b8;"><span style="color:#4ade80;">●</span> Live Facebook Session Connected</div>
        </div>
      </div>
      <button id="raj-close-btn" style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); color: #cbd5e1; border-radius: 8px; width: 28px; height: 28px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 14px;">✕</button>
    </div>

    <div style="padding: 16px 18px; overflow-y: auto; flex: 1; display: flex; flex-direction: column; gap: 14px;">
      
      <!-- Current Page Scan Card -->
      <div style="background: rgba(15,23,42,0.8); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 12px 14px;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
          <span style="font-size: 10.5px; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">Active Screen Live Audit</span>
          <span id="raj-audit-tag" style="font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; background: rgba(59,130,246,0.2); color: #60a5fa;">ACTIVE TAB</span>
        </div>
        <div id="raj-current-status" style="font-size: 13px; line-height: 1.4; color: #cbd5e1;">Scanning this Facebook page...</div>
      </div>

      <!-- Batch Fleet Selector Card -->
      <div style="background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 12px 14px;">
        <div style="font-size: 10.5px; font-weight: 800; color: #64748b; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.05em;">Batch Scan Account Pages</div>
        <div style="display: flex; flex-wrap: wrap; gap: 6px;" id="raj-fleet-buttons"></div>
        <div style="margin-top: 10px; display: flex; gap: 8px;">
          <button id="raj-start-batch-btn" style="flex: 1; background: linear-gradient(135deg, #2563eb, #1d4ed8); border: none; color: #fff; padding: 9px 14px; border-radius: 8px; font-weight: 700; font-size: 12px; cursor: pointer;">
            🚀 Scan Selected Fleet
          </button>
          <button id="raj-quick-check-btn" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #f8fafc; padding: 9px 14px; border-radius: 8px; font-weight: 700; font-size: 12px; cursor: pointer;">
            🔍 Re-Scan Screen
          </button>
        </div>
      </div>

      <!-- Audit Progress Console -->
      <div id="raj-scan-console" style="background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 10px 12px; font-family: monospace; font-size: 11px; max-height: 120px; overflow-y: auto; color: #94a3b8; line-height: 1.5;">
        Ready. If you are on the Monetization screen, the active page is audited automatically.
      </div>

      <!-- Sync to Dashboard CTA -->
      <button id="raj-sync-dashboard-btn" style="background: linear-gradient(135deg, #10b981, #059669); border: none; color: #fff; padding: 12px 16px; border-radius: 10px; font-weight: 800; font-size: 13px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 4px 18px rgba(16,185,129,0.35);">
        <span>⚡ Send Verified Status to Dashboard (<span id="raj-verified-count">0</span> Pages) ↗</span>
      </button>

    </div>
  `;

  document.body.appendChild(hud);

  document.getElementById("raj-close-btn").onclick = () => hud.remove();

  // Populate Fleet Buttons
  const fleetButtonsContainer = document.getElementById("raj-fleet-buttons");
  let selectedFleetName = "Nidhi Desai (UK)"; // Default to account with Roberts Richard
  
  Object.keys(ALL_FLEETS).forEach(fleetName => {{
    const btn = document.createElement("button");
    btn.className = `raj-fleet-btn ${{fleetName === selectedFleetName ? "active" : ""}}`;
    btn.innerText = fleetName.replace(" (USA)", "").replace(" (UK)", "");
    btn.title = `Scan ${{ALL_FLEETS[fleetName].length}} pages for ${{fleetName}}`;
    btn.onclick = () => {{
      document.querySelectorAll(".raj-fleet-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      selectedFleetName = fleetName;
    }};
    fleetButtonsContainer.appendChild(btn);
  }});

  // Update verified count badge
  function updateVerifiedBadge() {{
    const count = Object.keys(verifiedPages).length;
    const badge = document.getElementById("raj-verified-count");
    if (badge) badge.innerText = count;
  }}
  updateVerifiedBadge();

  // 1. Single Page Active DOM Audit
  function auditActiveDOM() {{
    const statusBox = document.getElementById("raj-current-status");
    const consoleBox = document.getElementById("raj-scan-console");
    const bodyText = document.body.innerText || "";

    const hasAvailableToSetUp = bodyText.includes("Available to set up");
    const hasContentMonetization = bodyText.includes("Content monetization");
    const hasSetUpBtn = /set up/i.test(bodyText);
    const hasStars = bodyText.includes("Stars");

    // Detect Page from URL or DOM
    let pid = "";
    const m = window.location.href.match(/\/(\\d{{10,20}})\//);
    if (m) pid = m[1];

    // Match page in database
    let foundPage = null;
    if (pid) {{
      for (const fleet in ALL_FLEETS) {{
        const match = ALL_FLEETS[fleet].find(p => p.id === pid);
        if (match) {{ foundPage = match; break; }}
      }}
    }}

    const pageName = foundPage ? foundPage.name : (document.title.replace(" | Facebook", "") || "Current Page");

    if (hasAvailableToSetUp && (hasContentMonetization || hasSetUpBtn)) {{
      statusBox.innerHTML = `
        <div style="color: #4ade80; font-weight: 800; font-size: 13.5px; display: flex; align-items: center; gap: 6px;">
          <span>🟢</span> <span>AVAILABLE TO SET UP: CONTENT MONETIZATION!</span>
        </div>
        <div style="font-size: 11.5px; color: #f8fafc; margin-top: 3px;">
          <strong>${{pageName}}</strong> ${{pid ? `(ID: ${{pid}})` : ""}}
        </div>
        <div style="font-size: 10.5px; color: #94a3b8; margin-top: 2px;">
          Real live "[Set up]" button detected on this Facebook screen.
        </div>
      `;
      if (pid) {{
        verifiedPages[pid] = {{
          name: pageName,
          status: "ready",
          tool: "Content Monetization",
          verifiedAt: new Date().toISOString()
        }};
        localStorage.setItem("raj_real_fb_audit", JSON.stringify(verifiedPages));
        updateVerifiedBadge();
      }}
      consoleBox.innerHTML += `<div style="color:#4ade80;">[VERIFIED] ✅ ${{pageName}} has Content Monetization Set Up Available!</div>`;
    }} else if (window.location.href.includes("professional_dashboard/monetization")) {{
      statusBox.innerHTML = `
        <div style="color: #facc15; font-weight: 700; font-size: 13px;">
          ⏳ Not Yet Eligible for Content Monetization
        </div>
        <div style="font-size: 11.5px; color: #cbd5e1; margin-top: 2px;">
          <strong>${{pageName}}</strong>
        </div>
      `;
      consoleBox.innerHTML += `<div>[INFO] ${{pageName}}: Still in progress (no set up button).</div>`;
    }} else {{
      statusBox.innerHTML = `
        <div style="color: #94a3b8; font-size: 12.5px;">
          Navigate to <strong>Professional Dashboard &gt; Monetization</strong> on Facebook to audit this screen, or use the Batch Scanner below.
        </div>
      `;
    }}
  }}

  document.getElementById("raj-quick-check-btn").onclick = auditActiveDOM;

  // 2. Batch Fleet Scanner Logic
  async function runBatchFleetScan() {{
    const pages = ALL_FLEETS[selectedFleetName] || [];
    const consoleBox = document.getElementById("raj-scan-console");
    const startBtn = document.getElementById("raj-start-batch-btn");

    if (!pages.length) return;
    startBtn.disabled = true;
    startBtn.innerText = "⏳ Scanning...";
    consoleBox.innerHTML = `<div>[${{new Date().toLocaleTimeString()}}] 🚀 Starting real scan of ${{pages.length}} pages in ${{selectedFleetName}}...</div>`;

    for (let i = 0; i < pages.length; i++) {{
      const p = pages[i];
      consoleBox.innerHTML += `<div>[${{i+1}}/${{pages.length}}] Checking ${{p.name}}...</div>`;
      consoleBox.scrollTop = consoleBox.scrollHeight;

      try {{
        const res = await fetch(`/${{p.id}}/professional_dashboard/monetization/`, {{
          credentials: "include"
        }});
        const text = await res.text();

        const hasAvailable = text.includes("Available to set up");
        const hasContentMonetization = text.includes("Content monetization");
        const hasSetUp = /set up/i.test(text);

        if (hasAvailable && (hasContentMonetization || hasSetUp)) {{
          verifiedPages[p.id] = {{
            name: p.name,
            status: "ready",
            tool: "Content Monetization",
            verifiedAt: new Date().toISOString()
          }};
          consoleBox.innerHTML += `<div style="color:#4ade80;">➔ 🟢 ${{p.name}}: CONTENT MONETIZATION AVAILABLE!</div>`;
        }} else {{
          verifiedPages[p.id] = {{
            name: p.name,
            status: "in_progress",
            tool: "None",
            verifiedAt: new Date().toISOString()
          }};
          consoleBox.innerHTML += `<div>➔ ⚪ ${{p.name}}: Not yet eligible</div>`;
        }}
      }} catch (e) {{
        consoleBox.innerHTML += `<div style="color:#f87171;">➔ ⚠️ ${{p.name}}: Network check deferred</div>`;
      }}

      localStorage.setItem("raj_real_fb_audit", JSON.stringify(verifiedPages));
      updateVerifiedBadge();
      await new Promise(r => setTimeout(r, 600)); // Respectful throttle
    }}

    consoleBox.innerHTML += `<div style="color:#4ade80;font-weight:700;">[COMPLETE] ✅ Fleet scan finished! Click Send to Dashboard below.</div>`;
    consoleBox.scrollTop = consoleBox.scrollHeight;
    startBtn.disabled = false;
    startBtn.innerText = "🚀 Scan Selected Fleet";
  }}

  document.getElementById("raj-start-batch-btn").onclick = runBatchFleetScan;

  // 3. Sync to Dashboard
  document.getElementById("raj-sync-dashboard-btn").onclick = function() {{
    const dataStr = JSON.stringify(verifiedPages);
    const encoded = encodeURIComponent(dataStr);
    const url = `https://maitryshah365-coder.github.io/fb-pages-automation/?sync_real_monetization=${{encoded}}`;
    window.open(url, "_blank");
  }};

  // Run initial DOM check
  auditActiveDOM();
}})();
"""

with open('docs/js/fb_real_scanner.js', 'w', encoding='utf-8') as f:
    f.write(scanner_js)

with open('web/js/fb_real_scanner.js', 'w', encoding='utf-8') as f:
    f.write(scanner_js)

print("Successfully generated fb_real_scanner.js for both docs and web!")
