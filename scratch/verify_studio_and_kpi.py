import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # 1. Desktop Viewport (1440x900)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://localhost:8888", wait_until="networkidle")
        await asyncio.sleep(2)
        
        # Capture Top Portfolio View with KPI Grid (including Recommendation Card)
        await page.screenshot(path="C:/Users/Win/.gemini/antigravity-ide/brain/313a3f26-ac39-434f-8050-53be5bd48383/verify_desktop_kpi_recommendation.png")
        print("Desktop KPI & Recommendation captured")
        
        # Scroll down to YouTube Studio Content Table
        await page.evaluate("window.scrollTo(0, 750)")
        await asyncio.sleep(1)
        await page.screenshot(path="C:/Users/Win/.gemini/antigravity-ide/brain/313a3f26-ac39-434f-8050-53be5bd48383/verify_desktop_studio_table.png")
        print("Desktop Studio Table captured")
        
        # Click 90 Days timeframe button
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)
        await page.click("#btnTf90")
        await asyncio.sleep(1.5)
        await page.screenshot(path="C:/Users/Win/.gemini/antigravity-ide/brain/313a3f26-ac39-434f-8050-53be5bd48383/verify_desktop_90days_view.png")
        print("Desktop 90 Days View captured")
        
        # Open Drawer and select Lopez Edward (150 videos)
        await page.click("#btnOpenPageDrawer")
        await asyncio.sleep(1)
        items = await page.query_selector_all(".drawer-page-item")
        if len(items) >= 7:
            await items[6].click()
            await asyncio.sleep(1.5)
            # Scroll to table
            await page.evaluate("window.scrollTo(0, 750)")
            await asyncio.sleep(1)
            await page.screenshot(path="C:/Users/Win/.gemini/antigravity-ide/brain/313a3f26-ac39-434f-8050-53be5bd48383/verify_desktop_lopez_table.png")
            print("Desktop Lopez Edward Studio Table captured")
        
        # 2. Mobile Viewport (390x844)
        page_mobile = await browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True)
        await page_mobile.goto("http://localhost:8888", wait_until="networkidle")
        await asyncio.sleep(2)
        
        # Mobile Top View with KPI grid and Recommendation box
        await page_mobile.screenshot(path="C:/Users/Win/.gemini/antigravity-ide/brain/313a3f26-ac39-434f-8050-53be5bd48383/verify_mobile_kpi.png")
        print("Mobile KPI captured")
        
        # Mobile Studio Table
        await page_mobile.evaluate("window.scrollTo(0, 680)")
        await asyncio.sleep(1)
        await page_mobile.screenshot(path="C:/Users/Win/.gemini/antigravity-ide/brain/313a3f26-ac39-434f-8050-53be5bd48383/verify_mobile_studio_table.png")
        print("Mobile Studio Table captured")
        
        await browser.close()
        print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run())
