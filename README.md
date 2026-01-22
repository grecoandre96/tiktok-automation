# 🎬 Video Remix Studio

Professional video editing tool for social media content creation. Transform videos with AI-powered scripts and voice-overs.

## ✨ Features

- **📥 Flexible Import**: Upload files or download from YouTube, TikTok, Instagram
- **🤖 AI Script Generation**: Automatic transcription and script rewriting with GPT-4
- **🎙️ Professional Voice-Overs**: OpenAI TTS with multiple voice options
- **🛡️ Anti-Detection**: Optional effects to bypass content detection systems
- **🎬 Clean Export**: High-quality MP4 output ready for social media

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- FFmpeg installed and in PATH
- OpenAI API key

### Installation

1. Clone the repository:
```bash
cd tiktok_automation
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
# Create .env file
OPENAI_API_KEY=your_api_key_here
```

5. Run the application:
```bash
streamlit run app.py
```

## 📖 Usage

### Step 1: Import Video
- **Upload**: Drag and drop MP4/MOV files
- **Download**: Paste URL from YouTube, TikTok, or Instagram

### Step 2: Generate Script
- **AI Voice-Over Mode**:
  - Automatic audio transcription
  - AI-powered script generation
  - Editable script with duration awareness
  - Professional TTS voice-over
- **Silent Mode**: Process video without audio

### Step 3: Process & Export
- Apply optional anti-detection effects
- Export high-quality MP4
- Download ready for upload

## 🏗️ Architecture

```
video_remix_studio/
├── config/
│   └── settings.py          # Centralized configuration
├── src/
│   ├── models.py            # Data models (VideoFile, Script, etc.)
│   ├── video_handler.py     # Upload & download operations
│   ├── ai_service.py        # OpenAI Whisper + GPT + TTS
│   ├── video_processor.py   # MoviePy video editing
│   └── utils.py             # Helper functions
├── app.py                   # Streamlit UI
├── .env                     # Environment variables
└── requirements.txt         # Dependencies
```

## 🔧 Configuration

Edit `config/settings.py` to customize:
- Output video quality
- Supported formats
- Default voice settings
- Anti-detection parameters

## 📝 Best Practices

1. **Video Quality**: Use high-quality source videos (1080p recommended)
2. **Script Length**: Keep scripts concise for better engagement
3. **Voice Selection**: Choose voices that match your content style
4. **Anti-Detection**: Use sparingly and test results

## 🐛 Troubleshooting

**Download fails from YouTube:**
- Ensure Chrome is installed (for cookie extraction)
- Try uploading the file manually instead

**Video processing is slow:**
- Processing time depends on video length and effects
- Disable anti-detection for faster processing

**Audio transcription fails:**
- Ensure video has clear audio
- Check that FFmpeg is properly installed

## 📄 License

This project is for educational purposes. Respect platform terms of service when using.

## 🤝 Contributing

This is a personal project. Feel free to fork and customize for your needs.

## ⚠️ Disclaimer

Use responsibly and in accordance with platform guidelines. The anti-detection features are for educational purposes only.
