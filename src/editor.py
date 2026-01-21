from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip
from moviepy.video.fx import MirrorX, MultiplySpeed, MultiplyColor
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
        
        # --- ANTI-DETECTION: CORE FILTERS ---
        effects = []
        if flip:
            effects.append(MirrorX())
        if speed != 1.0:
            effects.append(MultiplySpeed(factor=speed))
        
        # 3. EXTRA ANTI-DETECTION: Subtle Zoom/Crop (removes edge pixels/watermarks)
        w, h = video.size
        video = video.cropped(x_center=w/2, y_center=h/2, width=w/1.1, height=h/1.1)
        video = video.resized(width=w, height=h) 

        # 4. EXTRA ANTI-DETECTION: Subtle Color Adjustment (Change hash)
        effects.append(MultiplyColor(1.02))
            
        if effects:
            video = video.with_effects(effects)

        # Handle Audio
        if remove_audio_only:
            # Output silent video for TikTok songs
            final_video = video.without_audio()
        else:
            # Load new AI audio
            video = video.without_audio()
            audio = AudioFileClip(voiceover_path)
            
            # Sync duration
            if audio.duration > video.duration:
                audio = audio.with_duration(video.duration)
            
            final_video = video.with_audio(audio)
        
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
            audio.close()
        
        return output_path

if __name__ == "__main__":
    editor = VideoEditor()
