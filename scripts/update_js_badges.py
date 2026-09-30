import os

files = ["docs/js/gold_app.js", "web/js/gold_app.js"]

for js_path in files:
    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Locate and replace the badge rendering block inside renderMetaToolsHubView
    old_badges = """        // Content Monetization badge
        let contentBadge = `<span class="badge-status-criteria">${p.content_monetization || "N/A"}</span>`;
        if (p.content_monetization && p.content_monetization.toLowerCase().includes("policy")) {
          contentBadge = `<span class="badge-status-policy">⏳ Policy Review</span>`;
        } else if (p.content_monetization && (p.content_monetization.toLowerCase().includes("candidate") || p.content_monetization.includes("Waitlist"))) {
          contentBadge = `<span class="badge-status-waitlist" style="background:rgba(249,115,22,0.15); border:1px solid #f97316; color:#fb923c;">🔥 Invite Candidate</span>`;
        } else if (p.content_monetization && p.content_monetization.toLowerCase().includes("set up")) {
          contentBadge = `<span class="badge-status-setup">🎉 Set Up</span>`;
        }

        // Subscriptions badge
        let subBadge = `<span class="badge-status-criteria">${p.subscriptions || "N/A"}</span>`;
        if (p.subscriptions && (p.subscriptions.toLowerCase().includes("set up") || p.subscriptions.toLowerCase().includes("ready"))) {
          subBadge = `<span class="badge-status-setup" style="background:rgba(168,85,247,0.15); border:1px solid #a855f7; color:#c084fc;">🎉 Set Up Ready</span>`;
        }

        // Stars badge
        let starBadge = `<span class="badge-status-criteria">${p.stars || "N/A"}</span>`;
        if (p.stars && (p.stars.toLowerCase().includes("active") || p.stars.toLowerCase().includes("set up"))) {
          starBadge = `<span class="badge-status-setup" style="background:rgba(234,179,8,0.15); border:1px solid #eab308; color:#fde047; font-weight:800;">⭐ Active</span>`;
        }"""

    new_badges = """        // Content Monetization badge (Exact Meta Business Suite Terms)
        let contentBadge = `<span class="badge-status-criteria">${p.content_monetization || "Criteria Not Met"}</span>`;
        if (p.content_monetization === "Policy Issues" || (p.content_monetization && p.content_monetization.includes("Policy"))) {
          contentBadge = `<span class="badge-status-policy">⏳ Policy Issues</span>`;
        } else if (p.content_monetization && (p.content_monetization.includes("Waitlist") || p.content_monetization.includes("waitlist"))) {
          contentBadge = `<span class="badge-status-waitlist">📋 Waitlist criteria▼</span>`;
        } else if (p.content_monetization && p.content_monetization.toLowerCase().includes("set up")) {
          contentBadge = `<span class="badge-status-setup">🎉 Set Up</span>`;
        } else if (p.content_monetization === "Criteria Not Met") {
          contentBadge = `<span class="badge-status-criteria">Criteria Not Met</span>`;
        }

        // Subscriptions badge (Exact Meta Business Suite Terms)
        let subBadge = `<span class="badge-status-criteria">${p.subscriptions || "Criteria Not Met"}</span>`;
        if (p.subscriptions === "Set Up" || (p.subscriptions && p.subscriptions.toLowerCase().includes("set up"))) {
          subBadge = `<span class="badge-status-setup">🎉 Set Up</span>`;
        } else if (p.subscriptions === "Not Found") {
          subBadge = `<span style="color:#64748b; font-size:11.5px; font-weight:600;">Not Found</span>`;
        } else if (p.subscriptions === "Criteria Not Met") {
          subBadge = `<span class="badge-status-criteria">Criteria Not Met</span>`;
        }

        // Stars badge (Exact Meta Business Suite Terms: Set Up vs Criteria Not Met)
        let starBadge = `<span class="badge-status-criteria">${p.stars || "Criteria Not Met"}</span>`;
        if (p.stars === "Set Up" || (p.stars && p.stars.toLowerCase().includes("set up"))) {
          starBadge = `<span class="badge-status-setup">🎉 Set Up</span>`;
        } else if (p.stars === "Not Found") {
          starBadge = `<span style="color:#64748b; font-size:11.5px; font-weight:600;">Not Found</span>`;
        } else if (p.stars === "Criteria Not Met") {
          starBadge = `<span class="badge-status-criteria">Criteria Not Met</span>`;
        }"""

    # Normalize newlines
    content = content.replace("\r\n", "\n")
    old_badges_norm = old_badges.replace("\r\n", "\n")

    assert old_badges_norm in content, f"old_badges not found in {js_path}"
    content = content.replace(old_badges_norm, new_badges.replace("\r\n", "\n"))

    # Also update KPI card 3 & 4 text
    content = content.replace(
        'if (kpiUnlocked) kpiUnlocked.innerText = `${starsActiveCount} Stars • ${subsReadyCount} Subs`;',
        'if (kpiUnlocked) kpiUnlocked.innerText = `${starsActiveCount + subsReadyCount} Set Up Ready`;'
    )
    content = content.replace(
        'if (kpiContent) kpiContent.innerText = `39 Top Viral Candidates`;',
        'if (kpiContent) kpiContent.innerText = `Policy Review & Waitlist`;'
    )

    with open(js_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated:", js_path)

print("Both JS files updated with exact authentic Meta terms!")
