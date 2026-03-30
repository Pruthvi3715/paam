from TTS.api import TTS
import tempfile
import os
from pathlib import Path


class CoquiTTS:
    """Local TTS using Coqui (Bark/VITS models)"""

    def __init__(self, model_name: str = "tts_models/en/multispeaker/fast_pitch"):
        self.model_name = model_name
        self.tts = TTS(model_path=None, config_path=None, model_name=model_name)
        self.output_dir = Path("./data/tts_output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def speak(self, text: str, voice: str = "male", output_file: str = None) -> str:
        """Generate speech from text"""
        if output_file is None:
            output_file = f"tts_{hash(text)}.wav"

        output_path = self.output_dir / output_file

        self.tts.tts_to_file(
            text=text,
            file_path=str(output_path),
            speaker_wav=None if voice == "male" else None,
            language="en",
        )

        return str(output_path)

    def list_models(self):
        """List available TTS models"""
        return TTS.list_models()


tts_engine = CoquiTTS()
