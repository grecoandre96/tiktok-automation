"""Video Remix Studio - Professional video editing tool for social media content."""

__version__ = "2.0.0"
__author__ = "Video Remix Studio"

from src.models import VideoFile, Script, VoiceOver, ProcessedVideo
from src.video_handler import VideoHandler
from src.ai_service import AIService
from src.video_processor import VideoProcessor

__all__ = [
    "VideoFile",
    "Script",
    "VoiceOver",
    "ProcessedVideo",
    "VideoHandler",
    "AIService",
    "VideoProcessor",
]
