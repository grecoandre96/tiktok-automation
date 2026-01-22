"""
Configuration settings for Video Remix Studio.
Centralizes all paths, constants, and environment variables.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"
UPLOADS_DIR = ASSETS_DIR / "uploads"
PROCESSED_DIR = ASSETS_DIR / "processed"
TEMP_DIR = ASSETS_DIR / "temp"

# Create directories if they don't exist
for directory in [UPLOADS_DIR, PROCESSED_DIR, TEMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# FFmpeg configuration
FFMPEG_PATH = r"C:\Users\utente\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
if os.path.exists(FFMPEG_PATH) and FFMPEG_PATH not in os.environ.get("PATH", ""):
    os.environ["PATH"] += os.pathsep + FFMPEG_PATH

# Video processing settings
MAX_VIDEO_DURATION = 180  # seconds
SUPPORTED_VIDEO_FORMATS = [".mp4", ".mov", ".avi", ".mkv"]
OUTPUT_VIDEO_CODEC = "libx264"
OUTPUT_AUDIO_CODEC = "aac"
OUTPUT_FPS = 30

# OpenAI TTS voices
OPENAI_VOICES = {
    "Alloy": "alloy",
    "Echo": "echo",
    "Fable": "fable",
    "Onyx": "onyx",
    "Nova": "nova",
    "Shimmer": "shimmer"
}

# Script generation settings
SCRIPT_STYLES = ["Viral", "Educational", "Mysterious", "Emotional"]
