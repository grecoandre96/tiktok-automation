---
name: TikTok Automation Factory
description: Instructions for building a local app to scrape, remix, and repurpose TikTok videos using Python, Playwright, and AI.
---

# TikTok Automation Factory: Master Plan

## 1. Project Overview
**Goal**: Create a local application that automates the lifecycle of viral content repurposing:
1.  **Find**: Search TikTok for niche content (e.g., "gadget tech") with 30k-100k views (viral but not saturated).
2.  **Download**: Save video locally.
3.  **Remix**:
    -   **Transcribe** audio.
    -   **Rewrite** script using LLM (to keep meaning but change phrasing).
    -   **Voiceover** using TTS (Text-to-Speech) to generate a natural voice.
    -   **Edit** video to overlay new subtitles/hooks and replace audio.

**Stack**:
-   **Backend**: Python
-   **Scraping**: Playwright (Resilient browser automation)
-   **Editing**: MoviePy (Programmatic video editing)
-   **AI/ML**:
    -   *Transcription*: OpenAI Whisper (Local or API)
    -   *Text Gen*: OpenAI GPT-4o / Claude (API)
    -   *Voice*: Edge-TTS (Free, High Quality) or ElevenLabs (Paid, Ultra-realistic)
-   **Frontend**: Streamlit (Fast UI for Python tools)

---

## 2. Directory Structure
```
tiktok_automation/
├── assets/
│   ├── downloaded/      # Raw videos from TikTok
│   ├── processed/       # Final edited videos
│   └── temp/            # Intermediate files (audio, frames)
├── src/
│   ├── scraper.py       # Playwright logic to find & download
│   ├── editor.py        # MoviePy logic for cutting & overlay
│   ├── ai_engine.py     # Whisper + LLM + TTS logic
│   └── app.py           # Streamlit Frontend
├── requirements.txt
└── .env                 # API Keys
```

---

## 3. Implementation Steps

### Phase 1: The Scraper (`src/scraper.py`)
**Objective**: Find videos matching criteria.
-   **Tool**: `playwright` (Python).
-   **Logic**:
    -   Open TikTok Search URL for query.
    -   Scroll to load videos.
    -   Parse HTML to get `View Count`.
    -   Filter: `30,000 <= views <= 100,000`.
    -   **Download**: Extract `src` URL of the video element. Note: TikTok blobs work differently; we might need a third-party downloader service API or a specialized `tiktok-downloader` library if direct blob scraping fails. *Initial approach: existing Py library `TikTokApi` or direct Playwright interception.*

### Phase 2: AI Core (`src/ai_engine.py`)
**Objective**: Understand and Re-imagine the content.
-   **Transcription**:
    ```python
    import whisper
    model = whisper.load_model("base")
    result = model.transcribe("audio.mp3")
    original_text = result["text"]
    ```
-   **Rewriting (LLM)**:
    -   Prompt: "You are a viral content manager. Rewrite this TikTok script to catch attention immediately. Keep the core message but change the hook and phrasing to be more energetic. Original: {text}"
-   **Voiceover (TTS)**:
    -   Use `edge-tts` (Python lib) for free, natural-sounding multilingual voices.

### Phase 3: The Factory (`src/editor.py`)
**Objective**: Assemble the new video.
-   **Tool**: `moviepy`.
-   **Steps**:
    1.  Load VideoFileClip.
    2.  Remove original audio (`video.without_audio()`).
    3.  Generate new AudioFileClip from TTS.
    4.  **Trimming**: If new audio is shorter/longer, adjust video speed or loop specific segments (complex, start simple with static trimming).
    5.  **Overlays**: Add TextClip for the new "Hook" at the start (0-3 seconds).
    6.  Combine and Write file.

### Phase 4: User Interface (`src/app.py`)
**Objective**: Control center.
-   **Tool**: `streamlit`.
-   **Features**:
    -   Input: Search Term (e.g., "Kitchen Gadgets").
    -   Sliders: Min/Max Views.
    -   Button: "Hunt & Gather" (Runs Scraper).
    -   Gallery: Show downloaded videos.
    -   Action: "Remix Selected" -> Triggers AI & Editor.
    -   Result: Show Before/After.

---

## 4. Execution Guide (How to Start)

1.  **Install System Dependencies**:
    -   Install [FFmpeg](https://ffmpeg.org/download.html) (Essential for MoviePy).
    -   Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (Needed for some Python compiler libs).

2.  **Setup Environment**:
    ```powershell
    cd c:\Users\utente\Desktop\test-app\tiktok_automation
    python -m venv venv
    .\venv\Scripts\Activate
    pip install streamlit playwright moviepy openai-whisper openai edge-tts
    playwright install
    ```

3.  **Run the App**:
    ```powershell
    streamlit run src/app.py
    ```
