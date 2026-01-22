import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import sys
import json
import re
import os

async def search_tiktok(query, min_views, max_views, max_results=10):
    user_data_dir = os.path.abspath(os.path.join(os.getcwd(), "tiktok_session"))
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)

    async with async_playwright() as p:
        try:
            browser_context = await p.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,
                args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
                viewport=None,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()
            await Stealth().apply_stealth_async(page)
            
            search_url = f"https://www.tiktok.com/search/video?q={query.replace(' ', '%20')}"
            await page.goto(search_url, wait_until="load", timeout=90000)
            await page.bring_to_front()
            
            # Wait for results or captcha
            try:
                # Try multiple selectors for video items
                await page.wait_for_selector('[data-e2e="search_video-item"], .css-1s9j1be-DivVideoItemContainer, .video-feed-item', timeout=30000)
            except:
                print("DEBUG: Timeout waiting for initial results. Waiting for manual interaction...", file=sys.stderr)
                await asyncio.sleep(20)
            
            results = []
            
            def parse_views(view_text):
                if not view_text: return 0
                view_text = view_text.upper().replace('VIEWS', '').replace(' ', '').replace(',', '').strip()
                try:
                    if 'K' in view_text: return int(float(view_text.replace('K', '')) * 1000)
                    if 'M' in view_text: return int(float(view_text.replace('M', '')) * 1000000)
                    return int(re.sub(r'[^\d]', '', view_text))
                except: return 0

            # Scroll a bit to load more content if needed
            for _ in range(3):
                await page.mouse.wheel(0, 1500)
                await asyncio.sleep(1)

            # Query for all potential video items
            videos = await page.query_selector_all('[data-e2e="search_video-item"], .css-1s9j1be-DivVideoItemContainer, .video-feed-item')
            
            for v in videos:
                if len(results) >= max_results:
                    break
                    
                try:
                    view_elem = await v.query_selector('[data-e2e="search-card-like-container"]')
                    if not view_elem: view_elem = await v.query_selector('strong, .video-count')
                    
                    if view_elem:
                        view_text = await view_elem.inner_text()
                        views = parse_views(view_text)
                        
                        if min_views <= views <= max_views:
                            link_elem = await v.query_selector('a')
                            video_url = await link_elem.get_attribute('href')
                            if video_url and video_url.startswith('/'):
                                video_url = f"https://www.tiktok.com{video_url}"
                            
                            v_id = video_url.split('/')[-1].split('?')[0]
                            
                            # Avoid duplicates
                            if not any(r['id'] == v_id for r in results):
                                results.append({
                                    "id": v_id,
                                    "url": video_url,
                                    "views": views,
                                    "filename": f"{v_id}.mp4"
                                })
                except:
                    continue
            
            await browser_context.close()
            return results
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return []

if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(1)
    
    q = sys.argv[1]
    min_v = int(sys.argv[2])
    max_v = int(sys.argv[3])
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    try:
        result = asyncio.run(search_tiktok(q, min_v, max_v))
        if result:
            print(json.dumps(result))
        else:
            print("[]")
    except Exception as e:
        # Log to stderr but output empty JSON to stdout so app.py doesn't crash
        print(f"CRITICAL ERROR: {e}", file=sys.stderr)
        print("[]")
        sys.exit(0)
    except KeyboardInterrupt:
        print("[]")
        sys.exit(0)
