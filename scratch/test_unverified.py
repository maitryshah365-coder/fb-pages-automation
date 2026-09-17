import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page(viewport={'width': 1280, 'height': 900})
        await page.goto('http://127.0.0.1:8888', wait_until='domcontentloaded')
        await page.wait_for_timeout(2000)
        # Select Crown
        await page.evaluate("selectPage('637367679454577')")
        await page.wait_for_timeout(1000)
        demo_elem = page.locator('#countryDemographicsContainer')
        await demo_elem.scroll_into_view_if_needed()
        await page.screenshot(path='scratch/unverified_page_demographics.png')
        await b.close()
        print('Verified pending page screenshot saved!')

if __name__ == '__main__':
    asyncio.run(run())
