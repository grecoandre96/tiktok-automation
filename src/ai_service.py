"""
AI Service for script generation and text-to-speech.
Handles OpenAI Whisper transcription, GPT script generation, and TTS.
"""
import asyncio
from pathlib import Path
from typing import Optional
import logging

from openai import OpenAI
import whisper

from src.models import Script, VoiceOver
from src.utils import generate_unique_id
from config.settings import OPENAI_API_KEY, TEMP_DIR, OPENAI_VOICES

logger = logging.getLogger(__name__)


class AIService:
    """Handles all AI-related operations."""
    
    def __init__(self):
        """Initialize the AI service."""
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.whisper_model = None
        
    def _load_whisper_model(self):
        """Lazy load Whisper model."""
        if self.whisper_model is None:
            logger.info("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
        return self.whisper_model
    
    def transcribe_audio(self, audio_path: Path) -> Optional[str]:
        """
        Transcribe audio using OpenAI Whisper.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            model = self._load_whisper_model()
            logger.info(f"Transcribing audio: {audio_path}")
            
            result = model.transcribe(str(audio_path))
            text = result["text"].strip()
            
            logger.info(f"Transcription complete: {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    def generate_script(
        self, 
        original_text: str, 
        style: str = "Viral",
        target_duration: Optional[float] = None
    ) -> Optional[Script]:
        """
        Generate a rewritten script using GPT-4.
        
        Args:
            original_text: Original transcribed text
            style: Script style (Viral, Educational, etc.)
            target_duration: Target duration in seconds for the script
            
        Returns:
            Script object or None if failed
        """
        try:
            # Calculate target word count based on duration
            target_words = None
            if target_duration:
                # ~150 words per minute
                target_words = int((target_duration / 60) * 150)
            
            # Build prompt
            prompt = f"""Riscrivi questo testo in italiano per un video TikTok/YouTube Shorts.

Stile richiesto: {style}
Testo originale: {original_text}
"""
            
            if target_words:
                prompt += f"\nLunghezza target: circa {target_words} parole (per {target_duration:.0f} secondi di video)"
            
            prompt += """

Regole:
- Mantieni il messaggio principale
- Usa un linguaggio coinvolgente e diretto
- Aggiungi hook iniziale forte
- Mantieni la lunghezza appropriata per il video
- Scrivi in italiano naturale"""

            logger.info(f"Generating script with style: {style}")
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sei un esperto copywriter per contenuti virali social."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500
            )
            
            script_text = response.choices[0].message.content.strip()
            
            logger.info(f"Script generated: {len(script_text)} characters")
            
            return Script(text=script_text, style=style)
            
        except Exception as e:
            logger.error(f"Error generating script: {e}")
            return None
    
    async def generate_voiceover(
        self,
        text: str,
        voice: str = "alloy",
        output_filename: Optional[str] = None
    ) -> Optional[VoiceOver]:
        """
        Generate voice-over using OpenAI TTS.
        
        Args:
            text: Text to convert to speech
            voice: Voice ID (alloy, echo, fable, onyx, nova, shimmer)
            output_filename: Optional custom filename
            
        Returns:
            VoiceOver object or None if failed
        """
        try:
            if not output_filename:
                output_filename = f"{generate_unique_id('voice')}.mp3"
            
            output_path = TEMP_DIR / output_filename
            
            logger.info(f"Generating voice-over with voice: {voice}")
            
            response = self.client.audio.speech.create(
                model="tts-1-hd",
                voice=voice,
                input=text
            )
            
            # Save audio file
            response.stream_to_file(str(output_path))
            
            logger.info(f"Voice-over generated: {output_filename}")
            
            return VoiceOver(
                path=output_path,
                voice_id=voice,
                provider="openai"
            )
            
        except Exception as e:
            logger.error(f"Error generating voice-over: {e}")
            return None
