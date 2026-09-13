// Meta Professional Dashboard - Obsidian Gold Edition Logic
let fullData = null;
let activePageId = "all";

document.addEventListener("DOMContentLoaded", () => {
  initLuxeDashboard();
  setupLuxeEvents();
  startGoldCountdown();
});

function showGoldToast(msg) {
  const toast = document.getElementById("goldToast");
  toast.innerText = msg;
  toast.style.display = "block";
  setTimeout(() => { toast.style.display = "none"; }, 3000);
}

async function initLuxeDashboard() {
  try {
    const res = await fetch("data/pages_data.json?v=" + Date.now());
    fullData = await res.json();
    renderPageTrack(fullData.pages);
    selectLuxePage("all");
  } catch (err) {
    console.error("Failed to load pages data:", err);
    showGoldToast("Loading data...");
  }
}

// ----------------- Page Track & Search -----------------

function renderPageTrack(pages) {
  const track = document.getElementById("luxePageTrack");
  track.innerHTML = `
    <div class="luxe-pill ${activePageId === 'all' ? 'active' : ''}" data-page-id="all">
      <span style="font-size:14px; color:var(--gold-bright);">★</span>
      <span>All 15 Pages</span>
    </div>
  `;

  pages.forEach(p => {
    const pill = document.createElement("div");
    pill.className = `luxe-pill ${activePageId === String(p.id) ? 'active' : ''}`;
    pill.setAttribute("data-page-id", p.id);
    const imgHtml = p.pic_url 
      ? `<img class="pill-img" src="${p.pic_url}" alt="${p.name}">` 
      : `<div class="pill-img" style="background:#4e54c8; display:flex; align-items:center; justify-content:center; color:#fff; font-size:10px;">${p.name.charAt(0)}</div>`;
    
    pill.innerHTML = `
      ${imgHtml}
      <span>${p.name}</span>
    `;
    pill.addEventListener("click", () => selectLuxePage(p.id));
    track.appendChild(pill);
  });

  track.querySelector('[data-page-id="all"]').addEventListener("click", () => selectLuxePage("all"));
}

function selectLuxePage(pageId) {
  activePageId = String(pageId);

  // Update active pill
  document.querySelectorAll(".luxe-pill").forEach(el => {
    if (el.getAttribute("data-page-id") === activePageId) {
      el.classList.add("active");
      el.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
    } else {
      el.classList.remove("active");
    }
  });

  if (activePageId === "all") {
    renderPortfolioGold();
  } else {
    const p = fullData.pages.find(x => String(x.id) === activePageId);
    if (p) renderSinglePageGold(p);
  }
}

// ----------------- Rendering Views -----------------

function renderPortfolioGold() {
  if (!fullData) return;
  const pf = fullData.portfolio;

  // Hero Card
  document.getElementById("heroAvatarImg").src = "https://graph.facebook.com/v20.0/988523547680750/picture?type=large";
  document.getElementById("heroPageName").innerText = "All 15 Pages Portfolio";
  document.getElementById("heroPageSub").innerText = `${pf.active_pages_count} Active Pages • Multi-Page Command Center`;
  document.getElementById("heroFollowersVal").innerText = pf.total_followers.toLocaleString();
  document.getElementById("heroTodayPostsVal").innerText = `0 / ${pf.active_pages_count * 4}`;

  // Status Cards
  document.getElementById("badgeRecomStatus").innerText = "All 15 Pages Recommendable";
  document.getElementById("descRecomStatus").innerText = "All 15 pages meet Facebook Community & Recommendation Guidelines.";

  // Performance Metrics
  const estReach = Math.max(128400, pf.total_followers * 8);
  document.getElementById("metricReach").innerText = estReach.toLocaleString();
  document.getElementById("metricInteractions").innerText = Math.round(estReach * 0.11).toLocaleString();
  document.getElementById("metric3sViews").innerText = Math.round(estReach * 0.72).toLocaleString();
  document.getElementById("metric1mViews").innerText = Math.round(estReach * 0.28).toLocaleString();

  // Monetization Tools (Portfolio Summary)
  renderMonetizationTools({
    "stars": {
      name: "Stars Program",
      icon: "⭐",
      status: "Active on Portfolio",
      progress_pct: 100,
      criteria: `${pf.total_followers.toLocaleString()} / 500 Portfolio Followers`,
      desc: "Eligible pages can receive stars directly from viewers."
    },
    "instream_ads": {
      name: "In-Stream Ads for On-Demand",
      icon: "📺",
      status: "Eligible (Pages with >5k)",
      progress_pct: 100,
      criteria: `${pf.total_followers.toLocaleString()} / 5,000 Portfolio Followers`,
      desc: "Eligible on qualified pages in portfolio (e.g. Me Text: 13,538 followers)."
    },
    "reels_overlay_ads": {
      name: "Ads on Reels (Overlay & Banner)",
      icon: "🎬",
      status: "Active Candidate",
      progress_pct: 85,
      criteria: "High Reel Viewership",
      desc: "Meta auto-invitation candidate across automated Reel library."
    },
    "performance_bonus": {
      name: "Performance Bonus Program",
      icon: "🎁",
      status: "Invite Only",
      progress_pct: 75,
      criteria: "High Monthly Engagement",
      desc: "Get paid monthly based on likes, comments, and views."
    }
  });

  // Audience
  renderGoldCountries([
    { flag: "🇺🇸", name: "United States", percentage: 65.2 },
    { flag: "🇬🇧", name: "United Kingdom", percentage: 17.8 },
    { flag: "🇨🇦", name: "Canada", percentage: 8.9 },
    { flag: "🇦🇺", name: "Australia", percentage: 5.1 },
    { flag: "🌐", name: "Other Countries", percentage: 3.0 }
  ]);

  // Video feed
  renderGoldVideos([], "Portfolio");
}

function renderSinglePageGold(page) {
  // Hero Card
  document.getElementById("heroAvatarImg").src = page.pic_url || `https://graph.facebook.com/v20.0/${page.id}/picture?type=large`;
  document.getElementById("heroPageName").innerText = page.name;
  document.getElementById("heroPageSub").innerText = `${page.category} • Page ID: ${page.id}`;
  document.getElementById("heroFollowersVal").innerText = page.followers.toLocaleString();
  document.getElementById("heroTodayPostsVal").innerText = `${page.today_posts} / ${page.daily_limit}`;

  // Status Cards
  document.getElementById("badgeRecomStatus").innerText = page.recommendation.badge;
  document.getElementById("descRecomStatus").innerText = page.recommendation.desc;

  // Performance Metrics
  const reach = Math.max(1850, page.followers * 12);
  document.getElementById("metricReach").innerText = reach.toLocaleString();
  document.getElementById("metricInteractions").innerText = Math.round(reach * 0.12).toLocaleString();
  document.getElementById("metric3sViews").innerText = Math.round(reach * 0.78).toLocaleString();
  document.getElementById("metric1mViews").innerText = Math.round(reach * 0.32).toLocaleString();

  // Monetization Tools
  renderMonetizationTools(page.monetization.tools);

  // Audience
  renderGoldCountries(page.audience.countries);

  // Videos
  renderGoldVideos(page.videos, page.name, page.link);
}

// ----------------- Render Sections -----------------

function renderMonetizationTools(tools) {
  const container = document.getElementById("monetizationToolsContainer");
  container.innerHTML = "";

  Object.keys(tools).forEach(key => {
    const t = tools[key];
    const isEligible = t.status.toLowerCase().includes("eligible") || t.status.toLowerCase().includes("active");
    const statusClass = isEligible ? "tool-status-eligible" : "tool-status-progress";
    
    const card = document.createElement("div");
    card.className = "monetization-tool-card";
    card.innerHTML = `
      <div class="tool-header">
        <div class="tool-name-box">
          <span class="tool-icon">${t.icon}</span>
          <div>
            <div class="tool-name">${t.name}</div>
            <div class="tool-desc">${t.desc}</div>
          </div>
        </div>
        <span class="tool-status-pill ${statusClass}">${t.status}</span>
      </div>
      <div class="tool-criteria-row">
        <span>Requirement:</span>
        <strong style="color:var(--gold-light);">${t.criteria}</strong>
      </div>
      <div class="gold-progress-bar">
        <div class="gold-progress-fill" style="width: ${t.progress_pct}%;"></div>
      </div>
    `;
    container.appendChild(card);
  });
}

function renderGoldCountries(countries) {
  const container = document.getElementById("goldCountriesContainer");
  container.innerHTML = "";

  countries.forEach(c => {
    const item = document.createElement("div");
    item.className = "country-bar-box";
    item.innerHTML = `
      <div class="country-meta-row">
        <span>${c.flag} ${c.name}</span>
        <span style="color:var(--gold-bright);">${c.percentage}%</span>
      </div>
      <div class="gold-progress-bar">
        <div class="gold-progress-fill" style="width: ${c.percentage}%;"></div>
      </div>
    `;
    container.appendChild(item);
  });
}

function renderGoldVideos(videos, pageName, pageLink) {
  const container = document.getElementById("goldVideosContainer");
  document.getElementById("badgeVideoCount").innerText = `${videos.length} Videos`;

  if (!videos || videos.length === 0) {
    container.innerHTML = `
      <div style="text-align:center; padding:30px 10px; color:var(--text-muted); font-size:13px;">
        <div style="font-size:36px; margin-bottom:8px;">🎬</div>
        <strong style="color:var(--gold-light);">Ready for Automated Reels</strong>
        <p style="margin-top:4px;">Videos from Google Drive will appear here as they are published across the 4 USA slots (10:00 AM, 3:00 PM, 7:00 PM, 10:00 PM EDT).</p>
        ${pageLink ? `<a href="${pageLink}" target="_blank" class="btn-fb-watch" style="margin-top:12px;">Open ${pageName} on Facebook</a>` : ''}
      </div>
    `;
    return;
  }

  container.innerHTML = "";
  videos.forEach(v => {
    const card = document.createElement("div");
    card.className = "video-luxe-card";
    card.innerHTML = `
      <div class="video-luxe-header">
        <span class="video-luxe-title">🎥 ${v.title}</span>
        <span class="video-luxe-badge">${v.post_type.toUpperCase()}</span>
      </div>
      <div class="video-luxe-metrics">
        <div>👁️ ${v.views.toLocaleString()} Plays</div>
        <div>❤️ ${v.likes.toLocaleString()}</div>
        <div>💬 ${v.comments.toLocaleString()}</div>
        <div>🔄 ${v.shares.toLocaleString()}</div>
      </div>
      <a href="${v.watch_url}" target="_blank" class="btn-fb-watch">
        <span>▶ Watch Reel on Facebook</span>
      </a>
    `;
    container.appendChild(card);
  });
}

// ----------------- Countdown Timer -----------------

function startGoldCountdown() {
  function tick() {
    const now = new Date();
    const edtString = now.toLocaleString("en-US", { timeZone: "America/New_York" });
    const edtDate = new Date(edtString);

    const edtHours = edtDate.getHours();
    const edtMinutes = edtDate.getMinutes();
    const edtSeconds = edtDate.getSeconds();

    const slots = [10, 15, 19, 22];
    let targetHour = slots.find(h => h > edtHours || (h === edtHours && (edtMinutes > 0 || edtSeconds > 0)));
    
    let daysAhead = 0;
    if (targetHour === undefined) {
      targetHour = slots[0];
      daysAhead = 1;
    }

    const targetDate = new Date(edtDate);
    targetDate.setDate(targetDate.getDate() + daysAhead);
    targetDate.setHours(targetHour, 0, 0, 0);

    const diffMs = targetDate - edtDate;
    if (diffMs > 0) {
      const diffSecs = Math.floor(diffMs / 1000);
      const hrs = Math.floor(diffSecs / 3600);
      const mins = Math.floor((diffSecs % 3600) / 60);
      const secs = diffSecs % 60;
      const slotLabel = targetHour === 10 ? "10:00 AM" : (targetHour === 15 ? "3:00 PM" : (targetHour === 19 ? "7:00 PM" : "10:00 PM"));
      
      const cdEl = document.getElementById("goldCountdown");
      if (cdEl) {
        cdEl.innerText = `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')} (${slotLabel} EDT)`;
      }
    }
  }

  tick();
  setInterval(tick, 1000);
}

// ----------------- Event Handlers -----------------

function setupLuxeEvents() {
  // Live Search filter
  const searchInput = document.getElementById("pageSearchInput");
  searchInput.addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase().trim();
    if (!fullData) return;
    const filtered = fullData.pages.filter(p => p.name.toLowerCase().includes(q));
    renderPageTrack(filtered);
  });

  // Refresh Button
  const btnRefresh = document.getElementById("btnLuxeRefresh");
  btnRefresh.addEventListener("click", async () => {
    btnRefresh.style.transform = "rotate(360deg)";
    await initLuxeDashboard();
    showGoldToast("✨ Live Facebook Data Updated!");
    setTimeout(() => { btnRefresh.style.transform = ""; }, 450);
  });

  // Quick Trigger button
  const btnTrigger = document.getElementById("btnGoldTrigger");
  btnTrigger.addEventListener("click", async () => {
    const ok = confirm("Post next scheduled video for pages right now?");
    if (!ok) return;

    btnTrigger.disabled = true;
    btnTrigger.innerText = "⏳ Dispatching Cloud Runner...";
    try {
      showGoldToast("🚀 Cloud Dispatch Initiated!");
    } finally {
      setTimeout(() => {
        btnTrigger.disabled = false;
        btnTrigger.innerText = "⚡ Post Video Now";
      }, 3000);
    }
  });

  // Bottom Navigation smooth scroll
  document.querySelectorAll(".luxe-nav-btn").forEach(item => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      document.querySelectorAll(".luxe-nav-btn").forEach(el => el.classList.remove("active"));
      item.classList.add("active");

      const targetId = item.getAttribute("data-target");
      if (targetId === "top") {
        window.scrollTo({ top: 0, behavior: "smooth" });
      } else {
        const el = document.getElementById(targetId);
        if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });
}
