"""
Video processor for editing and remixing videos.
Handles audio extraction, video effects, and final assembly.
"""
from pathlib import Path
from typing import Optional
import logging

from moviepy import VideoFileClip, AudioFileClip
from moviepy.video.fx import MirrorX, MultiplySpeed, MultiplyColor
from moviepy.audio.fx import MultiplyVolume

from src.models import VideoFile, VoiceOver, ProcessedVideo
from src.utils import generate_unique_id
from config.settings import (
    TEMP_DIR, 
    PROCESSED_DIR,
    OUTPUT_VIDEO_CODEC,
    OUTPUT_AUDIO_CODEC,
    OUTPUT_FPS
)

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Handles video processing and editing operations."""
    
    def __init__(self):
        """Initialize the video processor."""
        self.temp_dir = TEMP_DIR
        self.output_dir = PROCESSED_DIR
    
    def extract_audio(self, video_path: Path) -> Optional[Path]:
        """
        Extract audio from a video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Path to extracted audio file or None if failed
        """
        try:
            logger.info(f"Extracting audio from: {video_path}")
            
            video = VideoFileClip(str(video_path))
            
            if video.audio is None:
                logger.warning("Video has no audio track")
                video.close()
                return None
            
            audio_filename = f"{video_path.stem}_audio.mp3"
            audio_path = self.temp_dir / audio_filename
            
            video.audio.write_audiofile(str(audio_path), logger=None)
            video.close()
            
            logger.info(f"Audio extracted: {audio_filename}")
            return audio_path
            
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            return None
    
    def process_video(
        self,
        video: VideoFile,
        voiceover: Optional[VoiceOver] = None,
        apply_anti_detection: bool = False,
        flip_horizontal: bool = False,
        speed_factor: float = 1.0,
        output_filename: Optional[str] = None
    ) -> Optional[ProcessedVideo]:
        """
        Process video with optional voice-over and effects.
        
        Args:
            video: VideoFile object
            voiceover: Optional VoiceOver object
            apply_anti_detection: Apply subtle anti-detection effects
            flip_horizontal: Mirror video horizontally
            speed_factor: Speed multiplier (0.95-1.05 recommended)
            output_filename: Optional custom output filename
            
        Returns:
            ProcessedVideo object or None if failed
        """
        try:
            logger.info(f"Processing video: {video.filename}")
            
            # Load video
            clip = VideoFileClip(str(video.path))
            
            # Apply effects
            effects = []
            
            if flip_horizontal:
                effects.append(MirrorX())
                logger.info("Applied horizontal flip")
            
            if speed_factor != 1.0:
                effects.append(MultiplySpeed(factor=speed_factor))
                logger.info(f"Applied speed factor: {speed_factor}")
            
            if apply_anti_detection:
                # Subtle rotation and zoom to change video hash
                clip = clip.rotated(1.5)
                w, h = clip.size
                clip = clip.cropped(
                    x_center=w/2, 
                    y_center=h/2, 
                    width=w/1.15, 
                    height=h/1.15
                )
                clip = clip.resized(height=1920)
                
                # Subtle color adjustment
                effects.append(MultiplyColor(1.03))
                logger.info("Applied anti-detection effects")
            
            if effects:
                clip = clip.with_effects(effects)
            
            # Normalize FPS
            clip = clip.with_fps(OUTPUT_FPS)
            
            # Handle audio
            has_audio = True
            if voiceover:
                # Replace audio with voice-over
                clip = clip.without_audio()
                audio_clip = AudioFileClip(str(voiceover.path))
                
                # Subtle volume adjustment for anti-detection
                if apply_anti_detection:
                    audio_clip = audio_clip.with_effects([MultiplyVolume(0.98)])
                
                # Sync duration
                if audio_clip.duration > clip.duration:
                    audio_clip = audio_clip.with_duration(clip.duration)
                
                clip = clip.with_audio(audio_clip)
                logger.info("Added voice-over audio")
            elif voiceover is None and not apply_anti_detection:
                # Silent mode - remove audio
                clip = clip.without_audio()
                has_audio = False
                logger.info("Removed audio (silent mode)")
            
            # Generate output filename
            if not output_filename:
                output_filename = f"{generate_unique_id('processed')}.mp4"
            
            output_path = self.output_dir / output_filename
            
            # Render video
            logger.info(f"Rendering video: {output_filename}")
            clip.write_videofile(
                str(output_path),
                codec=OUTPUT_VIDEO_CODEC,
                audio_codec=OUTPUT_AUDIO_CODEC if has_audio else None,
                temp_audiofile=str(self.temp_dir / "temp_audio.m4a"),
                remove_temp=True,
                logger=None
            )
            
            clip.close()
            if voiceover:
                audio_clip.close()
            
            logger.info(f"Video processing complete: {output_filename}")
            
            return ProcessedVideo(
                path=output_path,
                original_video=video,
                voiceover=voiceover,
                has_audio=has_audio,
                anti_detection_applied=apply_anti_detection
            )
            
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            return None
