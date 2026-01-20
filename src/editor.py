from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
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

    def remix_video(self, video_path, voiceover_path, output_filename):
        print(f"Remixing video: {video_path}")
        
        # Load video and remove audio
        video = VideoFileClip(video_path).without_audio()
        
        # Load new audio
        audio = AudioFileClip(voiceover_path)
        
        # If audio is longer than video, we might want to loop or trim.
        # For now, let's just match the video duration.
        if audio.duration > video.duration:
            audio = audio.with_duration(video.duration)
        
        # Set audio to video
        final_video = video.with_audio(audio)
        
        output_path = os.path.join(self.output_dir, output_filename)
        # codec libx264 is standard for web
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        
        video.close()
        audio.close()
        
        return output_path

if __name__ == "__main__":
    editor = VideoEditor()
