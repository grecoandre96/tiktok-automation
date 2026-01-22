import requests
import os

def download_tiktok_video(url, output_path):
    """
    Attempts to download a TikTok video using multiple strategies.
    1. Try with TikWM API (Fast, No Watermark)
    2. Try with yt-dlp (Fallback)
    """
    print(f"DEBUG: Attempting to download {url}")
    
    # Strategy 1: TikWM API
    try:
        print("DEBUG: Trying TikWM API...")
        api_url = "https://www.tikwm.com/api/"
        response = requests.post(api_url, data={'url': url}).json()
        
        if response.get('code') == 0:
            video_url = response['data']['play']
            # Download file
            r = requests.get(video_url, stream=True)
            with open(output_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
            print(f"DEBUG: Download successful via TikWM API -> {output_path}")
            return True
    except Exception as e:
        print(f"DEBUG: TikWM API failed: {e}")

    # Strategy 2: yt-dlp fallback
    try:
        print("DEBUG: Trying yt-dlp fallback...")
        import subprocess
        import sys
        cmd = [
            sys.executable, "-m", "yt_dlp", 
            "--no-playlist", 
            "--cookies-from-browser", "chrome",
            "--user-agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "--force-ipv4",
            "--recode-video", "mp4",
            "-o", output_path, 
            url
        ]
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        print(f"DEBUG: yt-dlp fallback failed: {e}")
    
    return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python downloader.py <url> <output_path>")
    else:
        success = download_tiktok_video(sys.argv[1], sys.argv[2])
        if success:
            print("SUCCESS")
        else:
            print("FAILED")
