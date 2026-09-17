import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 900})

        print("Navigating to http://127.0.0.1:8888 ...", flush=True)
        await page.goto("http://127.0.0.1:8888", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # 1. Screenshot Portfolio 12 KPI cards
        kpi_sec = page.locator(".content-box").first
        await kpi_sec.scroll_into_view_if_needed()
        await page.wait_for_timeout(1000)
        await page.screenshot(path="scratch/kpi_12_portfolio.png")
        print("Saved scratch/kpi_12_portfolio.png", flush=True)

        # 2. Select Family Fancy (from user's screenshot)
        print("Selecting Family Fancy...", flush=True)
        await page.evaluate("selectPage('503358542855153')")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="scratch/kpi_12_family_fancy.png")
        print("Saved scratch/kpi_12_family_fancy.png", flush=True)

        # 3. Select Crafty Champions
        print("Selecting Crafty Champions...", flush=True)
        await page.evaluate("selectPage('640019675857269')")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="scratch/kpi_12_crafty_champions.png")
        print("Saved scratch/kpi_12_crafty_champions.png", flush=True)

        await browser.close()
        print("Completed testing 12 KPI cards!", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
