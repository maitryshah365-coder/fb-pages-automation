import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 900})

        print("Navigating to dashboard...", flush=True)
        await page.goto("http://127.0.0.1:8888", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        # 1. Test Portfolio Live Meta Insights
        print("Clicking Live Meta Insights tab for Portfolio...", flush=True)
        await page.click(".demo-tab-btn[data-tab='discovery']")
        await page.wait_for_timeout(1000)
        demo_elem = page.locator("#countryDemographicsContainer")
        await demo_elem.scroll_into_view_if_needed()
        await page.screenshot(path="scratch/live_meta_insights_portfolio.png")
        print("Saved scratch/live_meta_insights_portfolio.png", flush=True)

        # 2. Select Crafty Champions
        print("Selecting Crafty Champions...", flush=True)
        await page.evaluate("selectPage('640019675857269')")
        await page.wait_for_timeout(1000)

        # Click Live Meta Insights for Crafty Champions
        await page.click(".demo-tab-btn[data-tab='discovery']")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="scratch/live_meta_insights_crafty.png")
        print("Saved scratch/live_meta_insights_crafty.png", flush=True)

        await browser.close()
        print("Done testing live meta insights!", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
