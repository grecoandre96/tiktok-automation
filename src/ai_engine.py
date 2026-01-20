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
        Sei un esperto manager di contenuti virali per TikTok Italia. 
        Riscrivi questo script per renderlo immediatamente accattivante per un pubblico italiano.
        REGOLE FONDAMENTALI:
        1. Rispondi ESCLUSIVAMENTE in lingua ITALIANA.
        2. NON usare emoticon o caratteri speciali.
        3. Mantieni il messaggio centrale ma rendi l'introduzione (hook) molto energica.
        4. Usa un tono colloquiale e moderno.
        
        Testo originale: {original_text}
        """
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    async def generate_voiceover(self, text, output_path, voice="it-IT-ElsaNeural"):
        print(f"Generating Italian voiceover to {output_path}...")
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)

if __name__ == "__main__":
    # Test logic
    engine = AIEngine()
    # test_text = "Check out this amazing kitchen gadget that saves time."
    # asyncio.run(engine.generate_voiceover(test_text, "assets/temp/test_voice.mp3"))
