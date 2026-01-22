"""
Video handler for uploading and downloading videos.
Handles both direct file uploads and URL-based downloads.
"""
import subprocess
import sys
from pathlib import Path
from typing import Optional
import logging

from src.models import VideoFile
from src.utils import generate_unique_id, sanitize_filename, get_file_size
from config.settings import UPLOADS_DIR

logger = logging.getLogger(__name__)


class VideoHandler:
    """Handles video upload and download operations."""
    
    def __init__(self):
        """Initialize the video handler."""
        self.uploads_dir = UPLOADS_DIR
        
    def save_uploaded_file(self, uploaded_file, filename: Optional[str] = None) -> Optional[VideoFile]:
        """
        Save an uploaded file to the uploads directory.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            filename: Optional custom filename
            
        Returns:
            VideoFile object or None if save failed
        """
        try:
            # Generate filename
            if not filename:
                original_name = sanitize_filename(uploaded_file.name)
                file_id = generate_unique_id("upload")
                filename = f"{file_id}_{original_name}"
            
            # Save file
            file_path = self.uploads_dir / filename
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            logger.info(f"Saved uploaded file: {filename}")
            
            # Create VideoFile object
            return VideoFile(
                id=generate_unique_id("upload"),
                path=file_path,
                filename=filename,
                source="upload",
                size_bytes=get_file_size(file_path)
            )
            
        except Exception as e:
            logger.error(f"Error saving uploaded file: {e}")
            return None
    
    def download_from_url(self, url: str, filename: Optional[str] = None) -> Optional[VideoFile]:
        """
        Download a video from a URL using yt-dlp.
        
        Args:
            url: Video URL (YouTube, TikTok, Instagram, etc.)
            filename: Optional custom filename
            
        Returns:
            VideoFile object or None if download failed
        """
        try:
            # Generate filename
            if not filename:
                file_id = generate_unique_id("download")
                filename = f"{file_id}.mp4"
            
            file_path = self.uploads_dir / filename
            
            # yt-dlp command
            cmd = [
                sys.executable, "-m", "yt_dlp",
                "--no-playlist",
                "--cookies-from-browser", "chrome",
                "--user-agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
                "--force-ipv4",
                "--recode-video", "mp4",
                "-o", str(file_path),
                url
            ]
            
            logger.info(f"Downloading video from: {url}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and file_path.exists():
                logger.info(f"Successfully downloaded: {filename}")
                
                return VideoFile(
                    id=generate_unique_id("download"),
                    path=file_path,
                    filename=filename,
                    source="download",
                    source_url=url,
                    size_bytes=get_file_size(file_path)
                )
            else:
                logger.error(f"Download failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Download timeout exceeded (120s)")
            return None
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return None
    
    def get_video_duration(self, video_path: Path) -> Optional[float]:
        """
        Get video duration using ffprobe.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Duration in seconds or None if failed
        """
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return float(result.stdout.strip())
                
        except Exception as e:
            logger.error(f"Error getting video duration: {e}")
        
        return None
