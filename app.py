"""
Video Remix Studio - Main Streamlit Application
Professional video editing tool for social media content creation.
"""
import streamlit as st
import asyncio
from pathlib import Path

from src.video_handler import VideoHandler
from src.ai_service import AIService
from src.video_processor import VideoProcessor
from src.utils import format_duration, validate_video_file
from config.settings import OPENAI_VOICES, SCRIPT_STYLES

# Page configuration
st.set_page_config(
    page_title="Video Remix Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .step-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'video_handler' not in st.session_state:
    st.session_state.video_handler = VideoHandler()
if 'ai_service' not in st.session_state:
    st.session_state.ai_service = AIService()
if 'video_processor' not in st.session_state:
    st.session_state.video_processor = VideoProcessor()
if 'current_video' not in st.session_state:
    st.session_state.current_video = None
if 'current_script' not in st.session_state:
    st.session_state.current_script = None
if 'current_voiceover' not in st.session_state:
    st.session_state.current_voiceover = None
if 'processed_video' not in st.session_state:
    st.session_state.processed_video = None

# Header
st.markdown('<h1 class="main-header">🎬 Video Remix Studio</h1>', unsafe_allow_html=True)
st.markdown("**Professional video editing for social media content**")

# Sidebar - Settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    st.subheader("🎨 Script Style")
    script_style = st.selectbox(
        "Choose style",
        SCRIPT_STYLES,
        help="Style for AI-generated scripts"
    )
    
    st.subheader("🎙️ Voice Settings")
    voice_name = st.selectbox(
        "OpenAI Voice",
        list(OPENAI_VOICES.keys()),
        help="Voice for text-to-speech"
    )
    voice_id = OPENAI_VOICES[voice_name]
    
    st.subheader("🛡️ Anti-Detection")
    apply_anti_detection = st.checkbox(
        "Apply anti-detection effects",
        value=False,
        help="Subtle effects to bypass content detection"
    )
    
    if apply_anti_detection:
        flip_horizontal = st.checkbox("Flip horizontally", value=True)
        speed_factor = st.slider(
            "Speed adjustment",
            0.95, 1.05, 1.01, 0.01,
            help="Subtle speed change"
        )
    else:
        flip_horizontal = False
        speed_factor = 1.0
    
    st.divider()
    
    if st.button("🔄 Reset All", use_container_width=True):
        for key in ['current_video', 'current_script', 'current_voiceover', 'processed_video']:
            st.session_state[key] = None
        st.rerun()

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="step-header"><h3>📥 Step 1: Import Video</h3></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📤 Upload File", "🔗 Download from URL"])
    
    with tab1:
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=["mp4", "mov", "avi", "mkv"],
            help="Upload MP4, MOV, AVI, or MKV files"
        )
        
        if uploaded_file and st.session_state.current_video is None:
            with st.spinner("Saving video..."):
                video = st.session_state.video_handler.save_uploaded_file(uploaded_file)
                if video:
                    # Get duration
                    video.duration = st.session_state.video_handler.get_video_duration(video.path)
                    st.session_state.current_video = video
                    st.success(f"✅ Video uploaded: {video.filename}")
                    st.rerun()
                else:
                    st.error("❌ Failed to save video")
    
    with tab2:
        video_url = st.text_input(
            "Video URL",
            placeholder="https://youtube.com/shorts/...",
            help="Paste URL from YouTube, TikTok, Instagram, etc."
        )
        
        if st.button("⬇️ Download Video", use_container_width=True) and video_url:
            with st.spinner("Downloading video... This may take a minute."):
                try:
                    video = st.session_state.video_handler.download_from_url(video_url)
                    if video:
                        # Get duration
                        video.duration = st.session_state.video_handler.get_video_duration(video.path)
                        st.session_state.current_video = video
                        st.success(f"✅ Video downloaded: {video.filename}")
                        st.rerun()
                    else:
                        st.error("❌ Download failed. yt-dlp couldn't process the URL. Try another link or check the logs.")
                except Exception as e:
                    st.error(f"❌ Internal Error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
    
    # Display current video
    if st.session_state.current_video:
        st.divider()
        video = st.session_state.current_video
        st.video(str(video.path))
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Duration", format_duration(video.duration) if video.duration else "Unknown")
        with col_b:
            st.metric("Size", f"{video.size_mb:.1f} MB")

with col2:
    st.markdown('<div class="step-header"><h3>✍️ Step 2: Generate Script</h3></div>', unsafe_allow_html=True)
    
    if not st.session_state.current_video:
        st.info("👈 Upload or download a video first")
    else:
        video = st.session_state.current_video
        
        # Audio mode selection
        audio_mode = st.radio(
            "Audio Strategy",
            ["🎙️ AI Voice-Over", "🔇 Silent (No Audio)"],
            horizontal=True
        )
        
        if audio_mode == "🎙️ AI Voice-Over":
            if st.button("📝 Generate Script", use_container_width=True):
                with st.spinner("Extracting and transcribing audio..."):
                    # Extract audio
                    audio_path = st.session_state.video_processor.extract_audio(video.path)
                    
                    if audio_path:
                        # Transcribe
                        original_text = st.session_state.ai_service.transcribe_audio(audio_path)
                        
                        if original_text:
                            # Generate script
                            with st.spinner("Generating AI script..."):
                                script = st.session_state.ai_service.generate_script(
                                    original_text,
                                    style=script_style,
                                    target_duration=video.duration
                                )
                                
                                if script:
                                    st.session_state.current_script = script
                                    st.success("✅ Script generated!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to generate script")
                        else:
                            st.error("❌ Failed to transcribe audio")
                    else:
                        st.error("❌ Failed to extract audio. Video may not have audio track.")
            
            # Display and edit script
            if st.session_state.current_script:
                st.divider()
                script = st.session_state.current_script
                
                st.caption(f"📊 {script.word_count} words • ~{format_duration(script.estimated_duration)} duration")
                
                edited_text = st.text_area(
                    "Edit script",
                    value=script.text,
                    height=200,
                    help="Edit the generated script as needed"
                )
                
                if edited_text != script.text:
                    script.text = edited_text
                    script.__post_init__()  # Recalculate stats
                
                # Generate voice-over
                st.markdown("#### 🎙️ Generate Voice-Over")
                if st.button("🎵 Create Voice-Over", use_container_width=True):
                    with st.spinner(f"Generating voice-over with {voice_name}..."):
                        voiceover = asyncio.run(
                            st.session_state.ai_service.generate_voiceover(
                                script.text,
                                voice=voice_id
                            )
                        )
                        
                        if voiceover:
                            st.session_state.current_voiceover = voiceover
                            st.success("✅ Voice-over generated!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to generate voice-over")
                
                if st.session_state.current_voiceover:
                    st.audio(str(st.session_state.current_voiceover.path))
        
        else:  # Silent mode
            st.info("Silent mode selected. Video will be processed without audio.")
            st.session_state.current_script = None
            st.session_state.current_voiceover = None

# Step 3: Process Video
st.markdown('<div class="step-header"><h3>🎬 Step 3: Process & Export</h3></div>', unsafe_allow_html=True)

if not st.session_state.current_video:
    st.info("Complete Steps 1 and 2 first")
else:
    video = st.session_state.current_video
    voiceover = st.session_state.current_voiceover
    
    # Check if ready to process
    audio_mode = st.radio(
        "Confirm audio mode",
        ["🎙️ With Voice-Over", "🔇 Silent"],
        horizontal=True,
        key="final_audio_mode"
    )
    
    can_process = (
        (audio_mode == "🎙️ With Voice-Over" and voiceover is not None) or
        (audio_mode == "🔇 Silent")
    )
    
    if can_process:
        output_filename = st.text_input(
            "Output filename",
            value=f"remix_{video.filename}",
            help="Name for the processed video"
        )
        
        if not output_filename.endswith('.mp4'):
            output_filename += '.mp4'
        
        if st.button("🚀 Process Video", use_container_width=True, type="primary"):
            with st.spinner("Processing video... This may take a few minutes."):
                processed = st.session_state.video_processor.process_video(
                    video=video,
                    voiceover=voiceover if audio_mode == "🎙️ With Voice-Over" else None,
                    apply_anti_detection=apply_anti_detection,
                    flip_horizontal=flip_horizontal,
                    speed_factor=speed_factor,
                    output_filename=output_filename
                )
                
                if processed:
                    st.session_state.processed_video = processed
                    st.success("✅ Video processed successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Failed to process video")
    else:
        if audio_mode == "🎙️ With Voice-Over":
            st.warning("⚠️ Generate a voice-over first (Step 2)")

# Display processed video
if st.session_state.processed_video:
    st.divider()
    processed = st.session_state.processed_video
    
    st.success("🎉 Your video is ready!")
    st.video(str(processed.path))
    
    with open(processed.path, "rb") as f:
        st.download_button(
            label="💾 Download Video",
            data=f,
            file_name=processed.path.name,
            mime="video/mp4",
            use_container_width=True
        )
