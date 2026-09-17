import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # 1. Desktop Viewport
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://localhost:8888", wait_until="networkidle")
        await asyncio.sleep(2)
        
        # Open Drawer
        await page.click("#btnOpenPageDrawer")
        await asyncio.sleep(1)
        await page.screenshot(path="C:/Users/Win/.gemini/antigravity-ide/brain/313a3f26-ac39-434f-8050-53be5bd48383/audit_desktop_drawer.png")
        print("Desktop drawer captured")
        
        # Click 7th page (Lopez Edward)
        items = await page.query_selector_all(".drawer-page-item")
        if len(items) >= 7:
            await items[6].click()
            await asyncio.sleep(1.5)
            await page.screenshot(path="C:/Users/Win/.gemini/antigravity-ide/brain/313a3f26-ac39-434f-8050-53be5bd48383/audit_desktop_single_page.png")
            print("Desktop single page captured")
        
        # 2. Mobile Viewport
        page_mobile = await browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True)
        await page_mobile.goto("http://localhost:8888", wait_until="networkidle")
        await asyncio.sleep(2)
        
        await page_mobile.screenshot(path="C:/Users/Win/.gemini/antigravity-ide/brain/313a3f26-ac39-434f-8050-53be5bd48383/audit_mobile_portfolio.png")
        print("Mobile portfolio captured")
        
        # Open drawer on mobile
        await page_mobile.click("#btnOpenPageDrawer")
        await asyncio.sleep(1)
        await page_mobile.screenshot(path="C:/Users/Win/.gemini/antigravity-ide/brain/313a3f26-ac39-434f-8050-53be5bd48383/audit_mobile_drawer.png")
        print("Mobile drawer captured")
        
        # Select first page
        m_items = await page_mobile.query_selector_all(".drawer-page-item")
        if len(m_items) >= 1:
            await m_items[0].click()
            await asyncio.sleep(1.5)
            await page_mobile.screenshot(path="C:/Users/Win/.gemini/antigravity-ide/brain/313a3f26-ac39-434f-8050-53be5bd48383/audit_mobile_single_page.png")
            print("Mobile single page captured")
        
        await browser.close()
        print("ALL AUDIT COMPLETE SUCCESS")

if __name__ == "__main__":
    asyncio.run(run())
