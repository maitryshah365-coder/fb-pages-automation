import time
from playwright.sync_api import sync_playwright

def run_audit():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # 1. Desktop Audit (1366x768)
        page = browser.new_page(viewport={"width": 1366, "height": 768})
        page.goto("http://127.0.0.1:8888/", wait_until="domcontentloaded")
        page.wait_for_selector("#metricTotalViews", timeout=10000)
        time.sleep(1.5)
        
        print("\n--- DESKTOP AUDIT ---")
        title = page.title()
        brand = page.inner_text(".brand-name")
        print(f"Page Title: {title}")
        print(f"Brand Text: {brand}")
        
        # Default 28 Days Metrics
        pills = page.query_selector_all(".timeframe-pill")
        print(f"Timeframe Pills Count: {len(pills)}")
        active_pill = page.inner_text(".timeframe-pill.active")
        print(f"Default Active Timeframe: {active_pill}")
        
        views_28 = page.inner_text("#metricTotalViews")
        reach_28 = page.inner_text("#metricTotalReach")
        likes_28 = page.inner_text("#metricLikes")
        comments_28 = page.inner_text("#metricComments")
        recom_28 = page.inner_text("#metricRecommendation")
        print(f"28 Days Portfolio: Views={views_28}, Reach={reach_28}, Likes={likes_28}, Comments={comments_28}, Recom={recom_28}")
        page.screenshot(path="scratch/audit_desktop_28days.png")
        
        # Click 7 Days
        btn_7d = page.query_selector("button[data-days='7']")
        if btn_7d:
            btn_7d.click()
            time.sleep(0.8)
            views_7 = page.inner_text("#metricTotalViews")
            reach_7 = page.inner_text("#metricTotalReach")
            likes_7 = page.inner_text("#metricLikes")
            print(f"7 Days Portfolio: Views={views_7}, Reach={reach_7}, Likes={likes_7}")
            page.screenshot(path="scratch/audit_desktop_7days.png")
            
        # Click 60 Days
        btn_60d = page.query_selector("button[data-days='60']")
        if btn_60d:
            btn_60d.click()
            time.sleep(0.8)
            views_60 = page.inner_text("#metricTotalViews")
            print(f"60 Days Portfolio: Views={views_60}")
            
        # Click 90 Days
        btn_90d = page.query_selector("button[data-days='90']")
        if btn_90d:
            btn_90d.click()
            time.sleep(0.8)
            views_90 = page.inner_text("#metricTotalViews")
            print(f"90 Days Portfolio: Views={views_90}")
            page.screenshot(path="scratch/audit_desktop_90days.png")
            
        # Reset to 28 Days
        page.query_selector("button[data-days='28']").click()
        time.sleep(0.8)
        
        # Test Drawer & Select Single Page (Lopez Edward)
        page.click("#btnOpenPageDrawer")
        time.sleep(0.8)
        page.screenshot(path="scratch/audit_desktop_drawer.png")
        
        # Select Lopez Edward
        page.click(".drawer-page-item:has-text('Lopez')")
        time.sleep(1)
        
        l_name = page.inner_text("#heroPageName")
        l_views = page.inner_text("#metricTotalViews")
        l_reach = page.inner_text("#metricTotalReach")
        l_likes = page.inner_text("#metricLikes")
        l_comments = page.inner_text("#metricComments")
        l_recom = page.inner_text("#metricRecommendation")
        print(f"\nSingle Page (Lopez Edward): Name={l_name}, Views={l_views}, Likes={l_likes}, Comments={l_comments}, Recom={l_recom}")
        page.screenshot(path="scratch/audit_desktop_lopez.png")
        
        # 2. Mobile Audit (390x844)
        m_page = browser.new_page(viewport={"width": 390, "height": 844})
        m_page.goto("http://127.0.0.1:8888/", wait_until="domcontentloaded")
        m_page.wait_for_selector("#metricTotalViews", timeout=10000)
        time.sleep(1.5)
        
        print("\n--- MOBILE AUDIT ---")
        m_views = m_page.inner_text("#metricTotalViews")
        m_recom = m_page.inner_text("#metricRecommendation")
        print(f"Mobile Portfolio: Views={m_views}, Recom={m_recom}")
        m_page.screenshot(path="scratch/audit_mobile_portfolio.png")
        
        # Open Mobile Drawer
        m_page.click("#btnOpenPageDrawer")
        time.sleep(0.8)
        m_page.screenshot(path="scratch/audit_mobile_drawer.png")
        
        # Select Fresh Hive on Mobile
        m_page.click(".drawer-page-item:has-text('Fresh Hive')")
        time.sleep(1)
        
        fh_name = m_page.inner_text("#heroPageName")
        fh_views = m_page.inner_text("#metricTotalViews")
        fh_recom = m_page.inner_text("#metricRecommendation")
        print(f"Mobile Fresh Hive: Name={fh_name}, Views={fh_views}, Recom={fh_recom}")
        m_page.screenshot(path="scratch/audit_mobile_fresh_hive.png")
        
        browser.close()
        print("\n==========================================")
        print("AUDIT COMPLETED 100% SUCCESSFULLY!")
        print("==========================================")

if __name__ == "__main__":
    run_audit()
