import re

file_path = "docs/js/gold_app.js"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update cache version
code = code.replace("raj_fb_data_cache_v12", "raj_fb_data_cache_v13")

# 2. Guard window.scrollTo
code = code.replace(
    'window.scrollTo({ top: 0, behavior: "smooth" });',
    'if (typeof window.scrollTo === "function") window.scrollTo({ top: 0, behavior: "smooth" });'
)

# 3. Guard cardEl.querySelector
target_card = '''            if (cardEl) {
              const timeEl = cardEl.querySelector(".radar-card-time");'''
repl_card = '''            if (cardEl && typeof cardEl.querySelector === "function") {
              const timeEl = cardEl.querySelector(".radar-card-time");'''
if target_card in code:
    code = code.replace(target_card, repl_card)
    print("Guarded cardEl.querySelector")
else:
    print("cardEl target not found directly")

# 4. Remove early initApp
early_init = '''function initApp() {
  try { initDashboard(); } catch (e) { console.error("initDashboard error:", e); }
  try { setupEventListeners(); } catch (e) { console.error("setupEventListeners error:", e); }
  try { startSlotCountdown(); } catch (e) { console.error("startSlotCountdown error:", e); }
  try { initAutomationRadarLiveEngine(); } catch (e) { console.error("initAutomationRadarLiveEngine error:", e); }
  try { initUploadHistoryEngine(); } catch (e) { console.error("initUploadHistoryEngine error:", e); }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp);
} else {
  setTimeout(initApp, 10);
}'''

if early_init in code:
    code = code.replace(early_init, "// initApp moved to end of file to ensure all constants & functions are initialized")
    print("Removed early initApp")
else:
    print("Early initApp not found directly, searching regex...")
    pattern = r'function initApp\(\) \{[\s\S]*?setTimeout\(initApp, 10\);\s*\}'
    code = re.sub(pattern, '// initApp moved to end of file to ensure all constants & functions are initialized', code, count=1)
    print("Removed early initApp via regex")

# 5. Optimize initUploadHistoryEngine
target_hist_engine = '''function initUploadHistoryEngine() {
  fetchUploadHistory(false);

  // Setup 30s auto-refresh polling interval for real-time live data
  if (!uploadHistoryPollInterval) {
    uploadHistoryPollInterval = setInterval(() => {
      fetchUploadHistory(false);
    }, 30000);
  }

  // Also auto-refresh when user returns to tab
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") {
      fetchUploadHistory(false);
    }
  });

  // Setup filter button listeners
  const filterGroup = document.getElementById("historyCountryFilters");
  if (filterGroup) {'''

repl_hist_engine = '''function initUploadHistoryEngine() {
  // Lazy-load upload history after initial dashboard renders to keep first paint instant
  setTimeout(() => {
    fetchUploadHistory(false);
  }, 1500);

  // Also auto-refresh when user returns to tab
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") {
      fetchUploadHistory(false);
    }
  });

  // Setup filter button listeners
  const filterGroup = document.getElementById("historyCountryFilters");
  if (filterGroup && typeof filterGroup.querySelectorAll === "function") {'''

if target_hist_engine in code:
    code = code.replace(target_hist_engine, repl_hist_engine)
    print("Optimized initUploadHistoryEngine")
else:
    print("target_hist_engine not matched directly")

# 6. Append initApp at the very end
end_block = '''

// ----------------- App Lifecycle Initialization -----------------
function initApp() {
  try { initDashboard(); } catch (e) { console.error("initDashboard error:", e); }
  try { setupEventListeners(); } catch (e) { console.error("setupEventListeners error:", e); }
  try { startSlotCountdown(); } catch (e) { console.error("startSlotCountdown error:", e); }
  try { initAutomationRadarLiveEngine(); } catch (e) { console.error("initAutomationRadarLiveEngine error:", e); }
  try { initUploadHistoryEngine(); } catch (e) { console.error("initUploadHistoryEngine error:", e); }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initApp);
} else {
  setTimeout(initApp, 10);
}
'''

code = code.strip() + end_block

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Patch complete on docs/js/gold_app.js")
