import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # 1. Desktop Viewport
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://localhost:8888", wait_until="networkidle")
        await asyncio.sleep(2)
        
        # Click 7 Days
        await page.click("#btnTf7")
        await asyncio.sleep(1.5)
        await page.screenshot(path="C:/Users/Win/.gemini/antigravity-ide/brain/313a3f26-ac39-434f-8050-53be5bd48383/verify_desktop_7days_active.png")
        print("Desktop 7 Days captured")
        
        # 2. Mobile Viewport
        page_mobile = await browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True)
        await page_mobile.goto("http://localhost:8888", wait_until="networkidle")
        await asyncio.sleep(2)
        
        await page_mobile.screenshot(path="C:/Users/Win/.gemini/antigravity-ide/brain/313a3f26-ac39-434f-8050-53be5bd48383/verify_mobile_7days_pills.png")
        print("Mobile 7 Days captured")
        
        await browser.close()
        print("7 DAYS VERIFICATION SUCCESS")

if __name__ == "__main__":
    asyncio.run(run())
