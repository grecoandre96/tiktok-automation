"""
Data models for Video Remix Studio.
Uses dataclasses for clean, type-safe data structures.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from datetime import datetime


@dataclass
class VideoFile:
    """Represents a video file in the system."""
    
    id: str
    path: Path
    filename: str
    source: str  # "upload" or "download"
    source_url: Optional[str] = None
    duration: Optional[float] = None
    size_bytes: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def exists(self) -> bool:
        """Check if the video file exists on disk."""
        return self.path.exists()
    
    @property
    def size_mb(self) -> float:
        """Get file size in megabytes."""
        if self.size_bytes:
            return self.size_bytes / (1024 * 1024)
        return 0.0


@dataclass
class Script:
    """Represents a generated or edited script."""
    
    text: str
    style: str
    word_count: int = 0
    estimated_duration: float = 0.0  # seconds
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Calculate word count and estimated duration."""
        self.word_count = len(self.text.split())
        # Average speaking rate: ~150 words per minute
        self.estimated_duration = (self.word_count / 150) * 60


@dataclass
class VoiceOver:
    """Represents a generated voice-over."""
    
    path: Path
    voice_id: str
    provider: str  # "openai" or "elevenlabs"
    duration: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def exists(self) -> bool:
        """Check if the voice-over file exists."""
        return self.path.exists()


@dataclass
class ProcessedVideo:
    """Represents a final processed video."""
    
    path: Path
    original_video: VideoFile
    script: Optional[Script] = None
    voiceover: Optional[VoiceOver] = None
    has_audio: bool = True
    anti_detection_applied: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def exists(self) -> bool:
        """Check if the processed video exists."""
        return self.path.exists()
