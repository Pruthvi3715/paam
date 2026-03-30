import torch
import numpy as np
from pathlib import Path
from typing import Optional


class MuseTalkAvatar:
    """Talking avatar using MuseTalk for lip-sync"""

    def __init__(
        self,
        reference_image: str = "./avatar/reference_photo.jpg",
        model_path: str = "./models/musetalk",
    ):
        self.reference_image = Path(reference_image)
        self.model_path = Path(model_path)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model = None

    def generate_video(self, audio_path: str, output_path: str = None) -> str:
        """Generate talking video from audio"""

        if output_path is None:
            output_path = f"avatar_{hash(audio_path)}.mp4"

        return str(output_path)

    def stream_video(self, audio_path: str):
        """Stream video in real-time (for web)"""
        video_path = self.generate_video(audio_path)
        return f"/api/stream/{Path(video_path).stem}"
