import streamlit as st
import os
import subprocess
import sys
import json
from ai_engine import AIEngine
from editor import VideoEditor
from downloader import download_tiktok_video
from dotenv import load_dotenv
import asyncio

# Add FFmpeg to PATH (Critical for Windows users who installed via winget)
ffmpeg_path = r"C:\Users\utente\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
if os.path.exists(ffmpeg_path):
    os.environ["PATH"] += os.pathsep + ffmpeg_path

load_dotenv()

st.set_page_config(page_title="TikTok Auto-Remixer", layout="wide")

# Initialize engines
if 'ai_engine' not in st.session_state:
    st.session_state.ai_engine = AIEngine()
if 'editor' not in st.session_state:
    st.session_state.editor = VideoEditor()

# Session state for workflow
if 'current_video' not in st.session_state:
    st.session_state.current_video = None
if 'video_path' not in st.session_state:
    st.session_state.video_path = None
if 'remixed_path' not in st.session_state:
    st.session_state.remixed_path = None

st.title("🤖 TikTok Viral Remixer")
st.markdown("### Process one video at a time: Find -> Download -> Remix")

# Sidebar for controls
with st.sidebar:
    st.header("1. Target Niche")
    query = st.text_input("Search Query", "Life Hacks")
    min_views = st.number_input("Min Views", value=30000, step=1000)
    max_views = st.number_input("Max Views", value=100000, step=1000)
    
    st.divider()
    
    if st.button("🔎 Find Next Viral Video"):
        with st.spinner("Launching Scraper... check your taskbar for a new window!"):
            # Clear previous state
            st.session_state.current_video = None
            st.session_state.video_path = None
            st.session_state.remixed_path = None
            
            # Use subprocess to run the scraper standalone
            try:
                # We use sys.executable to use the current venv's python
                cmd = [
                    sys.executable, 
                    "src/standalone_scraper.py", 
                    query, 
                    str(min_views), 
                    str(max_views)
                ]
                # Run the command and capture output
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                # The script should print JSON to stdout
                output = result.stdout.strip()
                if output and output != "null":
                    # Find the last line in case there are debug prints
                    json_str = output.splitlines()[-1]
                    video_data = json.loads(json_str)
                    st.session_state.current_video = video_data
                    st.success(f"Found: {video_data['url']}")
                else:
                    st.warning("No video found or scraper was closed.")
            except Exception as e:
                st.error(f"Scraper error: {e}")

# Main Area
col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 Step 2: Download & Preview")
    if st.session_state.current_video:
        v_data = st.session_state.current_video
        st.info(f"**Found Video:** {v_data['url']} \n\n **Views:** {v_data['views']}")
        
        if st.button("⬇️ Download This Video"):
            with st.spinner("Downloading video (Attempting bypass)..."):
                path = os.path.join("assets/downloaded", v_data['filename'])
                success = download_tiktok_video(v_data['url'], path)
                if success:
                    st.session_state.video_path = path
                    st.success("Download complete!")
                else:
                    st.error("Download failed. TikTok is blocking all automated methods for this video.")
        
        if st.session_state.video_path and os.path.exists(st.session_state.video_path):
            st.video(st.session_state.video_path)
            
            if st.button("✨ START REMIX PROCESS"):
                st.session_state.processing = True
    else:
        st.info("Use the sidebar to fetch a video first.")

with col2:
    st.subheader("📤 Step 3: AI Remix & Result")
    if 'processing' in st.session_state and st.session_state.processing:
        try:
            with st.status("Executing AI Workflow...", expanded=True) as status:
                video_path = st.session_state.video_path
                base_name = os.path.basename(video_path).split('.')[0]
                temp_audio = f"assets/temp/{base_name}_orig.mp3"
                temp_voice = f"assets/temp/{base_name}_new_voice.mp3"
                final_filename = f"remix_{base_name}.mp4"

                st.write("🎵 Extracting original audio...")
                st.session_state.editor.extract_audio(video_path, temp_audio)
                
                st.write("📝 Transcribing with Whisper...")
                original_text = st.session_state.ai_engine.transcribe(temp_audio)
                st.text_area("Original Script:", original_text, height=100)
                
                st.write("🤖 Rewriting script with GPT-4o...")
                new_script = st.session_state.ai_engine.rewrite_script(original_text)
                st.text_area("New AI Script:", new_script, height=100)
                
                st.write("🎙️ Generating AI Voiceover...")
                asyncio.run(st.session_state.ai_engine.generate_voiceover(new_script, temp_voice))
                
                st.write("🎬 Reassembling final video...")
                final_path = st.session_state.editor.remix_video(video_path, temp_voice, final_filename)
                
                st.session_state.remixed_path = final_path
                status.update(label="Remix Complete!", state="complete", expanded=False)
            
            st.balloons()
        except Exception as e:
            st.error(f"Error during remix: {e}")
        finally:
            st.session_state.processing = False

    if st.session_state.remixed_path and os.path.exists(st.session_state.remixed_path):
        st.success("Final Remixed Video:")
        st.video(st.session_state.remixed_path)
        with open(st.session_state.remixed_path, "rb") as f:
            st.download_button("💾 Download Final Video", f, file_name=os.path.basename(st.session_state.remixed_path))
    else:
        st.info("The remixed video will appear here.")

st.markdown("---")
st.caption("Workflow: Find One -> Download -> Remix -> Done.")
