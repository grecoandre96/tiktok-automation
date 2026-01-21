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

    def rewrite_script(self, original_text, style="Virale"):
        print(f"Rewriting script with AI (Style: {style})...")
        
        styles = {
            "Virale": "Rendilo energico, con un hook fortissimo e un ritmo veloce. Usa un linguaggio moderno e colloquiale.",
            "Educativo": "Mantieni un tono autoritario ma chiaro e utile. Spiega il 'perché' dietro le cose in modo semplice ma professionale.",
            "Misterioso": "Crea curiosità, usa pause drammatiche nel testo e non svelare tutto subito. Inizia con una domanda intrigante.",
            "Emozionale": "Punta sui sentimenti, usa un tono più calmo, ispirazionale e riflessivo."
        }
        
        selected_style = styles.get(style, styles["Virale"])
        
        prompt = f"""
        Sei un esperto manager di contenuti per TikTok Italia. 
        Riscrivi questo script usando lo stile: {style}.
        
        LINEE GUIDA PER LO STILE:
        {selected_style}
        
        REGOLE FONDAMENTALI:
        1. Rispondi ESCLUSIVAMENTE in lingua ITALIANA.
        2. NON usare emoticon o caratteri speciali.
        3. Usa solo testo che suoni naturale quando letto a voce.
        
        Testo originale: {original_text}
        """
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    async def generate_voiceover(self, text, output_path, voice="it-IT-ElsaNeural", provider="Edge"):
        print(f"Generating voiceover via {provider} ({voice}) to {output_path}...")
        
        if provider == "OpenAI":
            # Better quality, more human-like (uses your existing OpenAI Key)
            response = self.client.audio.speech.create(
                model="tts-1-hd", # HD for maximum realism
                voice=voice.split(" ")[0].lower(), # e.g., 'onyx', 'nova'
                input=text
            )
            response.stream_to_file(output_path)
            
        elif provider == "ElevenLabs":
            # The absolute best for emotions (requires API Key)
            api_key = os.getenv("ELEVENLABS_API_KEY")
            if not api_key:
                raise Exception("ElevenLabs API Key missing in .env")
            
            import requests
            # Mapping or default voice ID for ElevenLabs
            voice_id = "pNInz6obpgDQGcFmaJgB" # Example 'Adam' or use dynamic
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.5, "use_speaker_boost": True}
            }
            res = requests.post(url, json=data, headers=headers)
            if res.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(res.content)
            else:
                raise Exception(f"ElevenLabs error: {res.text}")

        else:
            # Standard free version (Edge TTS)
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)

if __name__ == "__main__":
    # Test logic
    engine = AIEngine()
    # test_text = "Check out this amazing kitchen gadget that saves time."
    # asyncio.run(engine.generate_voiceover(test_text, "assets/temp/test_voice.mp3"))
