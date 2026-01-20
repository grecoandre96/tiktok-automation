---
description: Initialize the TikTok Automation environment
---

// turbo-all
1. Create virtual environment:
   ```powershell
   python -m venv venv
   ```
2. Install Python dependencies:
   ```powershell
   .\venv\Scripts\pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```powershell
   .\venv\Scripts\playwright install chromium
   ```
4. Install FFmpeg (system dependency):
   ```powershell
   winget install -e --id Gyan.FFmpeg
   ```
