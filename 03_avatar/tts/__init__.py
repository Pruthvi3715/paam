try:
    from .coqui_tts import CoquiTTS, tts_engine as local_tts

    COQUI_AVAILABLE = True
except ImportError:
    COQUI_AVAILABLE = False
    local_tts = None

try:
    from .elevenlabs import ElevenLabsTTS

    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    ElevenLabsTTS = None


def get_tts_engine(prefer_local: bool = True):
    """Get appropriate TTS engine based on preference"""
    if prefer_local and COQUI_AVAILABLE:
        return local_tts
    elif ELEVENLABS_AVAILABLE:
        return ElevenLabsTTS()
    else:
        raise ImportError("No TTS engine available. Install TTS or elevenlabs.")
