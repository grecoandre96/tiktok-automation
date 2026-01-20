import asyncio
from playwright.async_api import async_playwright
import sys

async def test_playwright():
    print("DEBUG: Starting standalone Playwright test...")
    try:
        async with async_playwright() as p:
            print("DEBUG: Launching browser...")
            browser = await p.chromium.launch(headless=False)
            print("DEBUG: Creating context...")
            page = await browser.new_page()
            print("DEBUG: Navigating to Google...")
            await page.goto("https://www.google.com")
            print(f"DEBUG: Success! Title: {await page.title()}")
            await asyncio.sleep(5)
            await browser.close()
    except Exception as e:
        print(f"DEBUG: Standalone test FAILED: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(test_playwright())
