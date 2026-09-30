import os

# Update HTML files
html_files = ["docs/index.html", "web/index.html"]

for h_path in html_files:
    with open(h_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Update hero defaults
    html = html.replace(
        '<div id="heroPageSub" class="hero-meta">126 Active Facebook Pages (504 Daily Slots) • 24/7 Automated Upload Engine</div>',
        '<div id="heroPageSub" class="hero-meta">143 Active Facebook Pages (572 Daily Slots) • 24/7 Automated Upload Engine</div>'
    )
    html = html.replace(
        '<span class="stat-num" id="metricHeroFollowers">23,100</span>',
        '<span class="stat-num" id="metricHeroFollowers">120,657</span>'
    )
    html = html.replace(
        '<span class="stat-num gold-text" id="metricHeroViews">17,905,097</span>',
        '<span class="stat-num gold-text" id="metricHeroViews">49,342,057</span>'
    )
    html = html.replace(
        '<span class="stat-num" id="metricHeroReels">5,559</span>',
        '<span class="stat-num" id="metricHeroReels">15,266</span>'
    )

    # 2. Update Monetization Hub defaults
    html = html.replace(
        '<div id="metaKpiAuditedPages" style="font-size: 26px; font-weight: 900; color: #fff; margin-top: 8px;">15 / 141</div>\n          <div style="font-size: 11.5px; color: #38bdf8; margin-top: 4px; font-weight: 600;">Rohini Dutt (15 Live) • 10 Accounts Queued</div>',
        '<div id="metaKpiAuditedPages" style="font-size: 26px; font-weight: 900; color: #fff; margin-top: 8px;">143 / 143</div>\n          <div style="font-size: 11.5px; color: #38bdf8; margin-top: 4px; font-weight: 600;">All 11 Accounts & 143 Pages Live</div>'
    )
    html = html.replace(
        '<div id="metaKpiPolicyHealth" style="font-size: 26px; font-weight: 900; color: #34d399; margin-top: 8px;">15 / 15 Clean</div>\n          <div style="font-size: 11.5px; color: #94a3b8; margin-top: 4px;">0 Monetization Violations (100% Clean)</div>',
        '<div id="metaKpiPolicyHealth" style="font-size: 26px; font-weight: 900; color: #34d399; margin-top: 8px;">143 / 143 Clean</div>\n          <div style="font-size: 11.5px; color: #94a3b8; margin-top: 4px;">0 Monetization Violations (100% Clean)</div>'
    )
    html = html.replace(
        '<div id="metaKpiUnlockedPrograms" style="font-size: 26px; font-weight: 900; color: #fbbf24; margin-top: 8px;">1 Ready to Set Up</div>\n          <div style="font-size: 11.5px; color: #facc15; margin-top: 4px; font-weight: 600;">Apex House: Subscriptions Unlocked</div>',
        '<div id="metaKpiUnlockedPrograms" style="font-size: 26px; font-weight: 900; color: #fbbf24; margin-top: 8px;">36 Stars • 3 Subs</div>\n          <div style="font-size: 11.5px; color: #facc15; margin-top: 4px; font-weight: 600;">36 Stars Active • 3 Subscriptions Ready</div>'
    )
    html = html.replace(
        '<div id="metaKpiContentMonetization" style="font-size: 26px; font-weight: 900; color: #c084fc; margin-top: 8px;">12 In Review</div>\n          <div style="font-size: 11.5px; color: #94a3b8; margin-top: 4px;">Standard 30-Day Presence Check</div>',
        '<div id="metaKpiContentMonetization" style="font-size: 26px; font-weight: 900; color: #c084fc; margin-top: 8px;">39 Top Viral</div>\n          <div style="font-size: 11.5px; color: #94a3b8; margin-top: 4px;">High-Priority Watch Mins Candidates</div>'
    )

    with open(h_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("Updated HTML:", h_path)

print("HTML files updated successfully!")
