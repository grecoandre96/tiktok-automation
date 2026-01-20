import whisper
import os
from openai import OpenAI
from dotenv import load_dotenv
import edge_tts
import asyncio

load_dotenv()

class AIEngine:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.whisper_model = None

    def load_whisper(self):
        if not self.whisper_model:
            print("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
        return self.whisper_model

    def transcribe(self, audio_path):
        model = self.load_whisper()
        print(f"Transcribing {audio_path}...")
        result = model.transcribe(audio_path)
        return result["text"]

    def rewrite_script(self, original_text):
        print("Rewriting script with AI...")
        prompt = f"""
        You are a viral content manager. Rewrite this TikTok script to catch attention immediately. 
        Keep the core message but change the hook and phrasing to be more energetic. 
        Original: {original_text}
        """
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    async def generate_voiceover(self, text, output_path, voice="en-US-EmmaMultilingualNeural"):
        print(f"Generating voiceover to {output_path}...")
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)

if __name__ == "__main__":
    # Test logic
    engine = AIEngine()
    # test_text = "Check out this amazing kitchen gadget that saves time."
    # asyncio.run(engine.generate_voiceover(test_text, "assets/temp/test_voice.mp3"))
