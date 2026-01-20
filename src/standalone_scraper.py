import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import sys
import json
import re
import os

async def search_tiktok(query, min_views, max_views):
    # Path per la sessione persistente
    user_data_dir = os.path.abspath(os.path.join(os.getcwd(), "tiktok_session"))
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)

    async with async_playwright() as p:
        try:
            # Utilizziamo un contesto persistente per salvare i login
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
            print(f"DEBUG: Navigating to {search_url}", file=sys.stderr)
            
            await page.goto(search_url, wait_until="load", timeout=90000)
            await page.bring_to_front()
            
            # Aspettiamo i risultati (diamo tempo all'utente di fare login se serve)
            try:
                await page.wait_for_selector('[data-e2e="search_video-item"]', timeout=60000)
            except:
                # Se non li trova, forse serve il login o captcha. Aspettiamo altri 20 secondi manuali.
                print("DEBUG: Risultati non trovati, attendo interazione manuale...", file=sys.stderr)
                await asyncio.sleep(20)
                # Riprova a vedere se dopo l'interazione sono apparsi
                if not await page.query_selector('[data-e2e="search_video-item"]'):
                    await browser_context.close()
                    return None
            
            videos = await page.query_selector_all('[data-e2e="search_video-item"]')
            
            def parse_views(view_text):
                if not view_text: return 0
                view_text = view_text.upper().replace('VIEWS', '').replace(' ', '').replace(',', '').strip()
                try:
                    if 'K' in view_text: return int(float(view_text.replace('K', '')) * 1000)
                    if 'M' in view_text: return int(float(view_text.replace('M', '')) * 1000000)
                    return int(re.sub(r'[^\d]', '', view_text))
                except: return 0

            found_res = None
            for v in videos:
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
                        found_res = {
                            "id": v_id,
                            "url": video_url,
                            "views": views,
                            "filename": f"{v_id}.mp4"
                        }
                        break
            
            await browser_context.close()
            return found_res
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return None

if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(1)
    
    q = sys.argv[1]
    min_v = int(sys.argv[2])
    max_v = int(sys.argv[3])
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    result = asyncio.run(search_tiktok(q, min_v, max_v))
    if result:
        print(json.dumps(result))
    else:
        print("null")
