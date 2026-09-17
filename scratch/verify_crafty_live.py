import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 900})
        page = await context.new_page()

        print("Navigating to http://127.0.0.1:8888 ...", flush=True)
        await page.goto("http://127.0.0.1:8888", wait_until="domcontentloaded")
        await page.wait_for_timeout(2500)

        # Directly invoke selectPage for Crafty Champions
        print("Invoking selectPage('640019675857269')...", flush=True)
        await page.evaluate("selectPage('640019675857269')")
        await page.wait_for_timeout(2000)

        os.makedirs("scratch", exist_ok=True)
        # Capture full page
        await page.screenshot(path="scratch/crafty_verified_dashboard.png")
        print("Saved scratch/crafty_verified_dashboard.png", flush=True)

        # Scroll to Audience Demographics container
        demo_elem = page.locator("#countryDemographicsContainer")
        await demo_elem.scroll_into_view_if_needed()
        await page.wait_for_timeout(1000)
        await page.screenshot(path="scratch/crafty_demographics_countries.png")
        print("Saved scratch/crafty_demographics_countries.png", flush=True)

        # Click Age & Gender tab
        print("Clicking age & gender tab...", flush=True)
        await page.evaluate("document.querySelector('.demo-tab-btn[data-tab=\"age_gender\"]').click()")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="scratch/crafty_demographics_age.png")
        print("Saved scratch/crafty_demographics_age.png", flush=True)

        await browser.close()
        print("ALL VERIFICATION SCREENSHOTS SAVED SUCCESSFULLY!", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
