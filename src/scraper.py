import asyncio
from playwright.async_api import async_playwright
import os
import re
import subprocess
import sys

class TikTokScraper:
    def __init__(self, download_dir="assets/downloaded"):
        self.download_dir = download_dir
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def parse_views(self, view_text):
        if not view_text: return 0
        view_text = view_text.upper().replace('VIEWS', '').replace(' ', '').replace(',', '').strip()
        try:
            if 'K' in view_text:
                return int(float(view_text.replace('K', '')) * 1000)
            if 'M' in view_text:
                return int(float(view_text.replace('M', '')) * 1000000)
            return int(re.sub(r'[^\d]', '', view_text))
        except:
            return 0

    async def search_one_video(self, query, min_views=30000, max_views=100000):
        print(f"DEBUG: Tentativo di apertura browser per {query}")
        
        async with async_playwright() as p:
            # Lancio ultra-semplice per forzare la visibilità
            browser = await p.chromium.launch(
                headless=False,
                args=["--start-maximized"]
            )
            context = await browser.new_context(
                viewport=None, # Lascia che il sistema decida la dimensione
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            
            # Script minimo per non essere bloccati subito
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            search_url = f"https://www.tiktok.com/search/video?q={query.replace(' ', '%20')}"
            print(f"DEBUG: Navigo su {search_url}")
            
            try:
                # Navigazione
                await page.goto(search_url, wait_until="load", timeout=90000)
                await page.bring_to_front() # Forza la finestra in primo piano
                
                print("DEBUG: Pagina caricata. GUARDA ORA IL TUO SCHERMO!")
                
                # Aspettiamo i video - questo dà tempo all'utente di vedere la pagina
                await page.wait_for_selector('[data-e2e="search_video-item"]', timeout=30000)
                
                videos = await page.query_selector_all('[data-e2e="search_video-item"]')
                found_meta = None
                for v in videos:
                    try:
                        view_elem = await v.query_selector('[data-e2e="search-card-like-container"]')
                        if not view_elem: view_elem = await v.query_selector('strong, .video-count')
                        
                        if view_elem:
                            view_text = await view_elem.inner_text()
                            views = self.parse_views(view_text)
                            if min_views <= views <= max_views:
                                link_elem = await v.query_selector('a')
                                video_url = await link_elem.get_attribute('href')
                                if video_url and video_url.startswith('/'):
                                    video_url = f"https://www.tiktok.com{video_url}"
                                v_id = video_url.split('/')[-1].split('?')[0]
                                found_meta = {"id": v_id, "url": video_url, "views": views, "filename": f"{v_id}.mp4"}
                                break
                    except: continue
                
                await browser.close()
                return found_meta

            except Exception as e:
                print(f"DEBUG: Errore durante la sessione: {e}")
                # Teniamo aperto un attimo così puoi vedere cosa è successo
                await asyncio.sleep(10)
                await browser.close()
                return None

    def download_video(self, video_data):
        if not video_data: return None
        path = os.path.join(self.download_dir, video_data['filename'])
        try:
            cmd = [sys.executable, "-m", "yt_dlp", "--no-playlist", "-o", path, video_data['url']]
            subprocess.run(cmd, check=True)
            return path
        except Exception as e:
            print(f"DEBUG: Download fallito: {e}")
            return None
