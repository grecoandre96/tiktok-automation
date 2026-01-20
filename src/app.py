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

# Add FFmpeg to PATH
ffmpeg_path = r"C:\Users\utente\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
if os.path.exists(ffmpeg_path):
    os.environ["PATH"] += os.pathsep + ffmpeg_path

load_dotenv()

st.set_page_config(page_title="TikTok Auto-Remixer", layout="wide")

# Initialize or Refresh engines
if 'ai_engine' not in st.session_state or st.sidebar.button("♻️ Force AI Reset"):
    st.session_state.ai_engine = AIEngine()
    st.session_state.editor = VideoEditor()
    # If the user pushed the button, stay on the page
    if 'processing' in st.session_state: del st.session_state.processing

# Session state for workflow
if 'video_list' not in st.session_state:
    st.session_state.video_list = []
if 'current_video' not in st.session_state:
    st.session_state.current_video = None
if 'video_path' not in st.session_state:
    st.session_state.video_path = None
if 'remixed_path' not in st.session_state:
    st.session_state.remixed_path = None
if 'ai_script' not in st.session_state:
    st.session_state.ai_script = ""
if 'voiceover_ready' not in st.session_state:
    st.session_state.voiceover_ready = False

st.title("🤖 TikTok Viral Remixer")
st.markdown("### Process one video at a time: Find -> Download -> Remix")

# Sidebar for controls
with st.sidebar:
    st.header("1. Target Niche")
    query = st.text_input("Search Query", "Life Hacks")
    min_views = st.number_input("Min Views", value=30000, step=1000)
    max_views = st.number_input("Max Views", value=100000, step=1000)
    
    st.divider()
    st.header("2. AI Settings")
    script_style = st.selectbox("Script Style", ["Virale", "Educativo", "Misterioso", "Emozionale"])
    voice_name = st.selectbox("Voice", [
        "it-IT-ElsaNeural (Female)", 
        "it-IT-IsabellaNeural (Female)", 
        "it-IT-DiegoNeural (Male)", 
        "it-IT-GiuseppeMultilingualNeural (Male)"
    ])
    voice_id = voice_name.split(" ")[0]
    
    st.divider()
    
    if st.button("🔎 Search Viral Videos"):
        with st.spinner("Searching TikTok for top matches..."):
            st.session_state.video_list = []
            st.session_state.current_video = None
            st.session_state.video_path = None
            st.session_state.remixed_path = None
            
            try:
                cmd = [sys.executable, "src/standalone_scraper.py", query, str(min_views), str(max_views)]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                output = result.stdout.strip()
                if output:
                    json_str = output.splitlines()[-1]
                    videos = json.loads(json_str)
                    if videos:
                        st.session_state.video_list = videos
                        st.success(f"Found {len(videos)} potential viral videos!")
                    else:
                        st.warning("No videos found matching your criteria.")
            except Exception as e:
                st.error(f"Search error: {e}")

# Main Area
col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 Step 2: Choose & Download")
    
    if st.session_state.video_list:
        st.write("Select a video to process:")
        for idx, v in enumerate(st.session_state.video_list):
            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(f"**Video {idx+1}:** {v['url']} \n\n (Views: {v['views']:,})")
            with cols[1]:
                if st.button(f"Select #{idx+1}", key=f"sel_{idx}"):
                    st.session_state.current_video = v
                    st.session_state.video_path = None # Reset download path for new selection
        
        st.divider()
        
    if st.session_state.current_video:
        v_data = st.session_state.current_video
        st.info(f"**Selected:** {v_data['url']}")
        
        if st.button("⬇️ Download Selected Video"):
            with st.spinner("Downloading video..."):
                path = os.path.join("assets/downloaded", v_data['filename'])
                if download_tiktok_video(v_data['url'], path):
                    st.session_state.video_path = path
                    st.success("Download complete!")
                else:
                    st.error("Download failed.")
        
        if st.session_state.video_path and os.path.exists(st.session_state.video_path):
            st.video(st.session_state.video_path)
            if st.button("✨ START REMIX PROCESS"):
                st.session_state.processing = True
    elif not st.session_state.video_list:
        st.info("Use the sidebar to search for videos.")

with col2:
    st.subheader("📤 Step 3: AI Remix & Iteration")
    
    if st.session_state.video_path and os.path.exists(st.session_state.video_path):
        video_path = st.session_state.video_path
        base_name = os.path.basename(video_path).split('.')[0]
        temp_audio = f"assets/temp/{base_name}_orig.mp3"
        temp_voice = f"assets/temp/{base_name}_new_voice.mp3"
        
        # Default filename based on video ID and style
        default_name = f"remix_{base_name}_{script_style}.mp4"

        # 1. GENERATE / REWRITE SCRIPT
        st.markdown("#### 1. Script Generation")
        if st.button("📝 Generate/Rewrite Script"):
            with st.spinner("AI is thinking..."):
                if not os.path.exists(temp_audio):
                    st.session_state.editor.extract_audio(video_path, temp_audio)
                original_text = st.session_state.ai_engine.transcribe(temp_audio)
                st.session_state.ai_script = st.session_state.ai_engine.rewrite_script(original_text, style=script_style)
                st.session_state.voiceover_ready = False # Reset voice if script changes
        
        if st.session_state.ai_script:
            # Allow manual editing of the script before voiceover
            st.session_state.ai_script = st.text_area("Edit AI Script:", st.session_state.ai_script, height=150)
            
            # 2. GENERATE VOICEOVER
            st.markdown("#### 2. Voiceover")
            if st.button("🎙️ Generate Voiceover"):
                with st.spinner(f"Generating voice with {voice_id}..."):
                    asyncio.run(st.session_state.ai_engine.generate_voiceover(st.session_state.ai_script, temp_voice, voice=voice_id))
                    st.session_state.voiceover_ready = True
                    st.success("Voiceover ready!")
            
            if st.session_state.voiceover_ready:
                st.audio(temp_voice)
                
                # 3. FINAL REMIX
                st.markdown("#### 3. Final Assembly")
                final_filename = st.text_input("Final Output Filename:", value=default_name)
                
                # Ensure the filename ends with .mp4
                if not final_filename.endswith(".mp4"):
                    final_filename += ".mp4"

                if st.button("🎬 Create Final Video"):
                    with st.spinner(f"Assembling video as {final_filename}..."):
                        final_path = st.session_state.editor.remix_video(video_path, temp_voice, final_filename)
                        st.session_state.remixed_path = final_path
                        st.balloons()

        if st.session_state.remixed_path and os.path.exists(st.session_state.remixed_path):
            st.divider()
            st.success("Target Achieved! Final Remix:")
            st.video(st.session_state.remixed_path)
            with open(st.session_state.remixed_path, "rb") as f:
                st.download_button("💾 Download Final Video", f, file_name=os.path.basename(st.session_state.remixed_path))
    else:
        st.info("Download a video first to start the AI Remix process.")

st.markdown("---")
st.caption("Workflow: Search -> Choose -> Download -> Remix.")
