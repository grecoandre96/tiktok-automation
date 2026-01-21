import streamlit as st
import os
import subprocess
import sys
import json
import asyncio
import time
from dotenv import load_dotenv
from ai_engine import AIEngine
from editor import VideoEditor
from downloader import download_tiktok_video

# --- CONFIGURATION & PATHS ---
load_dotenv()

# Add FFmpeg to PATH for Windows (installed via winget)
ffmpeg_path = r"C:\Users\utente\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
if os.path.exists(ffmpeg_path):
    os.environ["PATH"] += os.pathsep + ffmpeg_path

# --- PAGE SETUP ---
st.set_page_config(page_title="TikTok Auto-Remixer", layout="wide", page_icon="🤖")

# Initialize or Refresh Engines
if 'ai_engine' not in st.session_state or st.sidebar.button("♻️ Force AI/Editor Reset"):
    st.session_state.ai_engine = AIEngine()
    st.session_state.editor = VideoEditor()
    # Reset internal processing state if forced
    if 'processing' in st.session_state: del st.session_state.processing

# Initialize Session State Variables
state_defaults = {
    'video_list': [],
    'current_video': None,
    'video_path': None,
    'remixed_path': None,
    'ai_script': "",
    'voiceover_ready': False
}
for key, value in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.title("🤖 TikTok Viral Remixer")
st.markdown("### Search -> Choose -> Download -> Custom Remix")

# --- SIDEBAR: CONTROLS & SETTINGS ---
with st.sidebar:
    st.header("1. Search Criteria")
    query = st.text_input("Niche / Search Query", "Life Hacks")
    min_views = st.number_input("Min Views", value=30000, step=5000)
    max_views = st.number_input("Max Views", value=100000, step=10000)
    
    st.divider()
    
    st.header("2. AI Customization")
    script_style = st.selectbox("Tone & Style", ["Virale", "Educativo", "Misterioso", "Emozionale"])
    
    voice_provider = st.radio("Voice Provider", ["Edge (Free)", "OpenAI HD (Premium)", "ElevenLabs (Pro)"], horizontal=True)
    
    if "Edge" in voice_provider:
        voice_options = [
            "it-IT-ElsaNeural (Female)", 
            "it-IT-IsabellaNeural (Female)", 
            "it-IT-DiegoNeural (Male)", 
            "it-IT-GiuseppeMultilingualNeural (Male)"
        ]
        provider_key = "Edge"
    elif "OpenAI" in voice_provider:
        voice_options = [
            "Onyx (Male - Deep & Warm)",
            "Nova (Female - Energetic)",
            "Shimmer (Female - Soft)",
            "Alloy (Neutral - Balanced)",
            "Echo (Male - Calm)",
            "Fable (Neutral - Narrative)"
        ]
        provider_key = "OpenAI"
    else:
        voice_options = ["Standard ElevenLabs Voice"] # Expandable
        provider_key = "ElevenLabs"

    voice_name = st.selectbox("Select Voice", voice_options)
    voice_id = voice_name.split(" ")[0]
    
    st.divider()
    
    st.header("3. Anti-Detection (Viral)")
    do_flip = st.checkbox("Flip Horizontally (Mirror)", value=True, help="Changes pixel data, very effective.")
    speed_mod = st.slider("Subtle Speed Change", 0.95, 1.05, 1.01, 0.01, help="Speeds up/slows down subtly to bypass finger-printing.")
    
    st.divider()
    
    if st.button("🔎 Search TikTok", use_container_width=True):
        with st.spinner("Finding viral matches..."):
            # Reset state for new search
            st.session_state.video_list = []
            st.session_state.current_video = None
            st.session_state.video_path = None
            st.session_state.remixed_path = None
            st.session_state.ai_script = ""
            
            try:
                # Call standalone scraper via subprocess to avoid IO blocks
                cmd = [sys.executable, "src/standalone_scraper.py", query, str(min_views), str(max_views)]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                output = result.stdout.strip()
                if output:
                    json_str = output.splitlines()[-1]
                    videos = json.loads(json_str)
                    if videos:
                        st.session_state.video_list = videos
                        st.success(f"Found {len(videos)} videos!")
                    else:
                        st.warning("No videos found. Try lower view counts.")
            except Exception as e:
                st.error(f"Scraper error: {e}")

    st.divider()
    st.header("🔗 Magic Import (Any URL)")
    manual_url = st.text_input("Paste URL (YouTube, Pinterest, etc.)", placeholder="https://...")
    if st.button("🚀 Import Video", use_container_width=True) and manual_url:
        with st.spinner("Downloading from external source..."):
            video_id = f"manual_{int(time.time())}"
            filename = f"{video_id}.mp4"
            output_path = f"assets/downloaded/{filename}"
            if download_tiktok_video(manual_url, output_path):
                st.session_state.video_path = output_path
                st.session_state.current_video = {"id": video_id, "url": manual_url, "filename": filename}
                st.success("Video imported successfully!")
                st.rerun()
            else:
                st.error("Import failed. Check the URL.")

# --- MAIN INTERFACE ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 Step 2: Selection & Download")
    
    # Video List Management
    if st.session_state.video_list:
        st.write("Click 'Select' to preview and download:")
        for idx, v in enumerate(st.session_state.video_list):
            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(f"**#{idx+1}** ({v['views']:,} views) - [Link]({v['url']})")
            with cols[1]:
                if st.button(f"Select", key=f"sel_{idx}"):
                    st.session_state.current_video = v
                    st.session_state.video_path = None
        st.divider()
        
    # Selected Video Preview & Download
    if st.session_state.current_video:
        v_data = st.session_state.current_video
        st.info(f"**Processing:** {v_data['url']}")
        
        if st.session_state.video_path is None:
            if st.button("⬇️ Download This Video", use_container_width=True):
                with st.spinner("Downloading (No Watermark)..."):
                    path = os.path.join("assets/downloaded", v_data.get('filename', f"{v_data['id']}.mp4"))
                    if download_tiktok_video(v_data['url'], path):
                        st.session_state.video_path = path
                        st.success("Downloaded!")
                        st.rerun()
                    else:
                        st.error("Download failed. TikTok might be blocking.")
        else:
            st.success("✅ Video file ready!")
        
        if st.session_state.video_path and os.path.exists(st.session_state.video_path):
            st.video(st.session_state.video_path)
    elif not st.session_state.video_list:
        st.info("Start by searching for videos in the sidebar.")

with col2:
    st.subheader("📤 Step 3: AI Remixing")
    
    if st.session_state.video_path and os.path.exists(st.session_state.video_path):
        video_path = st.session_state.video_path
        base_name = os.path.basename(video_path).split('.')[0]
        temp_audio = f"assets/temp/{base_name}_orig.mp3"
        temp_voice = f"assets/temp/{base_name}_new_voice.mp3"
        
        # 0. CHOOSE AUDIO STRATEGY
        st.markdown("#### 0. Audio Strategy")
        audio_choice = st.radio("Strategy", ["Use AI Voiceover", "Silent Mode (Add song on TikTok)"], horizontal=True)
        is_silent = "Silent" in audio_choice

        if not is_silent:
            # 1. SCRIPT GENERATION
            st.markdown("#### 1. Generate Script")
            if st.button("📝 Create AI Script", use_container_width=True):
                with st.spinner("Analyzing audio and rewriting..."):
                    if not os.path.exists(temp_audio):
                        st.session_state.editor.extract_audio(video_path, temp_audio)
                    original_text = st.session_state.ai_engine.transcribe(temp_audio)
                    st.session_state.ai_script = st.session_state.ai_engine.rewrite_script(original_text, style=script_style)
                    st.session_state.voiceover_ready = False
            
            if st.session_state.ai_script:
                st.session_state.ai_script = st.text_area("Review/Edit Script:", st.session_state.ai_script, height=150)
                
                # 2. VOICEOVER GENERATION
                st.markdown("#### 2. AI Voiceover")
                if st.button("🎙️ Generate Voiceover", use_container_width=True):
                    with st.spinner(f"Generating voice via {provider_key}: {voice_id}..."):
                        asyncio.run(st.session_state.ai_engine.generate_voiceover(
                            st.session_state.ai_script, 
                            temp_voice, 
                            voice=voice_id, 
                            provider=provider_key
                        ))
                        st.session_state.voiceover_ready = True
                
                if st.session_state.voiceover_ready:
                    st.audio(temp_voice)
        
        # 3. FINAL ASSEMBLY (Common for both strategies)
        if is_silent or st.session_state.voiceover_ready:
            st.markdown("#### 3. Render Final Video")
            suffix = "silent" if is_silent else script_style
            default_name = f"remix_{base_name}_{suffix}.mp4"
            final_filename = st.text_input("Save as:", value=default_name)
            
            if not final_filename.endswith(".mp4"): final_filename += ".mp4"

            if st.button("🎬 Assemble & Render", use_container_width=True):
                with st.spinner(f"Rendering with Anti-Detection (Flip={do_flip}, Speed={speed_mod})..."):
                    final_path = st.session_state.editor.remix_video(
                        video_path, 
                        temp_voice if not is_silent else None, 
                        final_filename,
                        flip=do_flip,
                        speed=speed_mod,
                        remove_audio_only=is_silent
                    )
                    st.session_state.remixed_path = final_path
                    st.balloons()

        # Final Result Display
        if st.session_state.remixed_path and os.path.exists(st.session_state.remixed_path):
            st.divider()
            st.success("✅ Video Ready!")
            st.video(st.session_state.remixed_path)
            with open(st.session_state.remixed_path, "rb") as f:
                st.download_button("💾 Download Results", f, file_name=os.path.basename(st.session_state.remixed_path), use_container_width=True)
    else:
        st.info("Download a video on the left to unlock AI tools.")

st.markdown("---")
st.caption("TikTok Automation Tool v1.0 | Workflow: Search -> Select -> Download -> AI Script -> AI Voice -> Render")
