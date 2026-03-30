from elevenlabs.client import ElevenLabs
import os
from pathlib import Path


class ElevenLabsTTS:
    """Cloud TTS using ElevenLabs API"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.client = ElevenLabs(api_key=self.api_key)
        self.output_dir = Path("./data/tts_output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.voice_id = "pNInz6obpgDQGcFmaJgB"

    def speak(self, text: str, voice_id: str = None, output_file: str = None) -> str:
        """Generate speech from text"""
        if output_file is None:
            output_file = f"tts_{hash(text)}.mp3"

        output_path = self.output_dir / output_file
        voice = voice_id or self.voice_id

        audio = self.client.generate(
            text=text, voice=voice, model="eleven_multilingual_v2"
        )

        with open(output_path, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)

        return str(output_path)

    def list_voices(self):
        """List available voices"""
        return self.client.voices.get_all()
