from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip
from moviepy.video.fx import MirrorX, MultiplySpeed, MultiplyColor
from moviepy.audio.fx import MultiplyVolume
import os

class VideoEditor:
    def __init__(self, temp_dir="assets/temp", output_dir="assets/processed"):
        self.temp_dir = temp_dir
        self.output_dir = output_dir
        if not os.path.exists(temp_dir): os.makedirs(temp_dir)
        if not os.path.exists(output_dir): os.makedirs(output_dir)

    def extract_audio(self, video_path, audio_output_path):
        print(f"Extracting audio from {video_path}...")
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_output_path)
        video.close()
        return audio_output_path

    def remix_video(self, video_path, voiceover_path, output_filename, 
                   flip=False, speed=1.0, remove_audio_only=False):
        print(f"Remixing video: {video_path} (Anti-Detection: Flip={flip}, Speed={speed})")
        
        # Load video
        video = VideoFileClip(video_path)
        
        # 1. CORE EFFECTS (Mirror & Speed)
        effects = []
        if flip:
            effects.append(MirrorX())
        if speed != 1.0:
            effects.append(MultiplySpeed(factor=speed))
        
        # 2. ULTRA ANTI-DETECTION: Smart Zoom & Aggressive Rotation
        # 2.0 degrees rotation forces a massive recalculation
        video = video.rotated(2.0) 
        
        # Zoom in 20% to hide rotation edges and kill QR codes/watermarks
        w, h = video.size
        video = video.cropped(x_center=w/2, y_center=h/2, width=w/1.2, height=h/1.2)
        
        # Force Upscale to 1080p
        video = video.resized(height=1920) 
        
        # 3. COLOR & CONTRAST (Bypass Visual Hashing)
        # Subtle changes to the color profile
        effects.append(MultiplyColor(1.05)) # Brightness boost
        
        if effects:
            video = video.with_effects(effects)
        
        # Set a standard framerate to normalize output
        video = video.with_fps(30)

        # Handle Audio
        if remove_audio_only:
            # Output silent video for TikTok songs
            final_video = video.without_audio()
        else:
            # Load new AI audio
            video = video.without_audio()
            audio_clip = AudioFileClip(voiceover_path)
            
            # 5. AUDIO ANTI-DETECTION: Background Noise Injection
            # We add a very subtle lo-fi or ambiance track to break 'Audio Hashing'
            # For now, we simulate this by adjusting the volume/panning or 
            # if we had a library of noises, we would overlay one.
            # Simplified: Use a slightly different volume/envelope to change signature
            audio_effects = [MultiplyVolume(0.98)]
            audio_clip = audio_clip.with_effects(audio_effects)
            
            # Sync duration
            if audio_clip.duration > video.duration:
                audio_clip = audio_clip.with_duration(video.duration)
            
            final_video = video.with_audio(audio_clip)
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Rendering with high quality presets
        final_video.write_videofile(
            output_path, 
            codec="libx264", 
            audio_codec="aac" if not remove_audio_only else None,
            temp_audiofile=os.path.join(self.temp_dir, "temp-audio.m4a"),
            remove_temp=True
        )
        
        video.close()
        if not remove_audio_only:
            audio_clip.close()
        
        return output_path

if __name__ == "__main__":
    editor = VideoEditor()
