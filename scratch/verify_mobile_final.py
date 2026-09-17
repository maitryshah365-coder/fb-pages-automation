import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page_mobile = await browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True)
        await page_mobile.goto("http://localhost:8888", wait_until="networkidle")
        await asyncio.sleep(2)
        
        # 1. Top with recommendation card spanning 2 columns
        await page_mobile.screenshot(path="C:/Users/Win/.gemini/antigravity-ide/brain/313a3f26-ac39-434f-8050-53be5bd48383/mobile_balanced_kpi.png")
        
        # 2. Scroll directly to table
        await page_mobile.evaluate("window.scrollTo(0, 1150)")
        await asyncio.sleep(1)
        await page_mobile.screenshot(path="C:/Users/Win/.gemini/antigravity-ide/brain/313a3f26-ac39-434f-8050-53be5bd48383/mobile_table_verified.png")
        
        await browser.close()
        print("Mobile final captured")

if __name__ == "__main__":
    asyncio.run(run())
