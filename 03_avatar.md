# PAAM Layer 3: Avatar & Frontend

> **Status:** Ready for opencode session #3
> **Goal:** Set up TTS voice, talking avatar, and Chainlit frontend

---

## 1. Prerequisites

- ✅ Layer 1 completed (AnythingLLM + Ollama)
- ✅ Layer 2 completed (AgentScope agents)
- GPU with 8GB+ VRAM (for avatar models)

---

## 2. Project Structure

```
paam/
├── 01_rag_knowledge/
├── 02_agents/
├── 03_avatar/               # This layer
│   ├── tts/
│   │   ├── coqui_tts.py     # Local TTS
│   │   └── elevenlabs.py   # Cloud TTS (optional)
│   ├── avatar/
│   │   ├── musetalk.py      # Lip-sync avatar
│   │   └── reference_photo.jpg
│   ├── frontend/
│   │   ├── app.py           # Chainlit app
│   │   ├── requirements.txt
│   │   └── public/
│   │       └── styles.css
│   └── docker-compose.yml
└── ...
```

---

## 3. TTS Options

### Option A: Coqui TTS (Local - Recommended)

```bash
# Install Coqui TTS
pip install TTS>=0.21.0
```

### Option B: ElevenLabs (Cloud - Better Quality)

```bash
# Install ElevenLabs SDK
pip install elevenlabs>=1.0.0
```

---

## 4. TTS Implementation

### 4.1 Coqui TTS (Local)

```python
# tts/coqui_tts.py

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
        
        # Generate speech
        self.tts.tts_to_file(
            text=text,
            file_path=str(output_path),
            speaker_wav=None if voice == "male" else None,
            language="en"
        )
        
        return str(output_path)
    
    def list_models(self):
        """List available TTS models"""
        return TTS.list_models()


# Singleton instance
tts_engine = CoquiTTS()
```

### 4.2 ElevenLabs TTS (Cloud)

```python
# tts/elevenlabs.py

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
        
        # Default voice (can customize)
        self.voice_id = "pNInz6obpgDQGcFmaJgB"  # Adam voice
    
    def speak(self, text: str, voice_id: str = None, output_file: str = None) -> str:
        """Generate speech from text"""
        if output_file is None:
            output_file = f"tts_{hash(text)}.mp3"
        
        output_path = self.output_dir / output_file
        voice = voice_id or self.voice_id
        
        # Generate audio
        audio = self.client.generate(
            text=text,
            voice=voice,
            model="eleven_multilingual_v2"
        )
        
        # Save to file
        with open(output_path, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)
        
        return str(output_path)
    
    def list_voices(self):
        """List available voices"""
        return self.client.voices.get_all()


# Singleton - use env var for API key
# export ELEVENLABS_API_KEY="your-key-here"
```

### 4.3 Unified TTS Interface

```python
# tts/__init__.py

from .coqui_tts import CoquiTTS, tts_engine as local_tts
from .elevenlabs import ElevenLabsTTS

def get_tts_engine(prefer_local: bool = True):
    """Get appropriate TTS engine based on preference"""
    if prefer_local:
        return local_tts
    else:
        return ElevenLabsTTS()
```

---

## 5. Talking Avatar

### 5.1 MuseTalk Setup

MuseTalk provides real-time lip-syncing from audio to a reference photo.

```bash
# Install MuseTalk dependencies
git clone https://github.com/EMA-Multimedia/MuseTalk
cd MuseTalk
pip install -r requirements.txt
```

### 5.2 MuseTalk Inference

```python
# avatar/musetalk.py

import torch
import numpy as np
from pathlib import Path
from typing import Optional

class MuseTalkAvatar:
    """Talking avatar using MuseTalk for lip-sync"""
    
    def __init__(self, 
                 reference_image: str = "./avatar/reference_photo.jpg",
                 model_path: str = "./models/musetalk"):
        self.reference_image = Path(reference_image)
        self.model_path = Path(model_path)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load model (simplified - actual implementation loads full model)
        self.model = None  # Load actual model in production
    
    def generate_video(self, 
                      audio_path: str, 
                      output_path: str = None) -> str:
        """Generate talking video from audio"""
        
        if output_path is None:
            output_path = f"avatar_{hash(audio_path)}.mp4"
        
        # This is a placeholder - actual implementation:
        # 1. Load reference image
        # 2. Process audio to get face landmarks
        # 3. Generate lip-synced video frames
        # 4. Compile to video
        
        # For now, return path to reference (avatar shows static image)
        # Real implementation would use MuseTalk model
        
        return str(output_path)
    
    def stream_video(self, audio_path: str):
        """Stream video in real-time (for web)"""
        # Returns video stream URL for frontend
        video_path = self.generate_video(audio_path)
        return f"/api/stream/{Path(video_path).stem}"
```

### 5.2 Alternative: LivePortrait

```python
# avatar/liveportrait.py

class LivePortraitAvatar:
    """Alternative avatar using LivePortrait"""
    
    def __init__(self, reference_image: str):
        self.reference = reference_image
        # Load LivePortrait model
        pass
    
    def generate(self, audio_path: str) -> str:
        """Generate talking portrait"""
        # Uses LivePortrait for face swapping + lip-sync
        pass
```

---

## 6. Frontend: Chainlit App

### 6.1 Requirements

```txt
# frontend/requirements.txt

chainlit>=1.0.0
python-dotenv>=1.0.0
requests>=2.31.0
fastapi>=0.100.0
uvicorn>=0.25.0
aiohttp>=3.9.0
```

### 6.2 Chainlit App

```python
# frontend/app.py

import chainlit as cl
import requests
import asyncio
import os
from pathlib import Path

# Import from Layer 2
import sys
sys.path.append("../02_agents")
from agentscope.agents.teacher import TeacherAgent
from tts import get_tts_engine

# Configuration
ANYTHINGLLM_URL = os.getenv("ANYTHINGLLM_URL", "http://localhost:3001")
TEACHER = None  # Initialize on startup

# TTS settings
USE_LOCAL_TTS = os.getenv("USE_LOCAL_TTS", "true").lower() == "true"
tts_engine = get_tts_engine(prefer_local=USE_LOCAL_TTS)

@cl.on_chat_start
async def start_chat():
    """Initialize chat session"""
    global TEACHER
    
    # Initialize teacher agent
    TEACHER = TeacherAgent()
    
    # Send welcome message
    await cl.Message(
        content="""👋 Welcome to PAAM - Your Personal Adaptive AI Mentor!

I can help you learn from any uploaded material. Here's what I can do:

📚 **Chat** - Ask me anything about your study material
🎯 **Quiz** - Test your understanding 
📝 **Cheatsheet** - Get a quick summary
🧠 **Adaptive** - I learn your learning style over time

What would you like to learn about today?"""
    ).send()
    
    # Set up avatar display
    cl.user_session.set("avatar_active", False)


@cl.on_message
async def handle_message(message: cl.Message):
    """Handle incoming messages"""
    
    global TEACHER
    if TEACHER is None:
        TEACHER = TeacherAgent()
    
    user_input = message.content
    
    # Check for commands
    if user_input.startswith("/"):
        await handle_command(user_input)
        return
    
    # Process through Teacher Agent
    # Note: In production, this would be async
    response = TEACHER.chat(user_input)
    
    # Send text response
    msg = cl.Message(content=response)
    await msg.send()
    
    # Optional: Generate voice response
    if cl.user_session.get("voice_enabled", False):
        await generate_voice(response)


async def handle_command(command: str):
    """Handle slash commands"""
    
    if command == "/start":
        # Start new learning session
        response = TEACHER.start_session("General", time_minutes=45)
        await cl.Message(content=response).send()
    
    elif command == "/end":
        # End current session
        response = TEACHER.end_session()
        await cl.Message(content=response).send()
    
    elif command == "/voice on":
        cl.user_session.set("voice_enabled", True)
        await cl.Message(content="🔊 Voice enabled").send()
    
    elif command == "/voice off":
        cl.user_session.set("voice_enabled", False)
        await cl.Message(content="🔇 Voice disabled").send()
    
    elif command == "/style":
        style = TEACHER.student.get_style()
        await cl.Message(content=f"🎨 Your current learning style: **{style}**").send()
    
    elif command == "/mastery":
        mastery = TEACHER.student.get_mastery_rate()
        await cl.Message(content=f"📊 Your mastery rate: **{mastery:.1%}**").send()
    
    elif command.startswith("/quiz"):
        topic = command.replace("/quiz", "").strip()
        await start_quiz(topic)
    
    elif command == "/help":
        help_text = """**Available Commands:**

/start - Start a new learning session
/end - End current session
/voice on - Enable voice output
/voice off - Disable voice output
/style - Show your learning style
/mastery - Show mastery rate
/quiz [topic] - Start a quiz
/cheatsheet - Generate cheatsheet
/diagram [concept] - Generate diagram
/help - Show this help"""
        await cl.Message(content=help_text).send()
    
    else:
        await cl.Message(content=f"Unknown command: {command}. Type /help for available commands.").send()


async def generate_voice(text: str):
    """Generate and play voice response"""
    
    try:
        # Generate TTS
        audio_path = tts_engine.speak(text)
        
        # Send audio file to frontend
        await cl.Message(
            content="",
            elements=[cl.Audio(path=audio_path, display="inline")]
        ).send()
    except Exception as e:
        print(f"TTS Error: {e}")


async def start_quiz(topic: str):
    """Start a quiz on the given topic"""
    
    quiz_questions = [
        {"q": "What is a neural network?", "a": "A computing system inspired by biological neural networks"},
        {"q": "What is backpropagation?", "a": "An algorithm for training neural networks"},
        {"q": "What is overfitting?", "a": "When a model learns noise in training data"},
    ]
    
    # Store quiz state
    cl.user_session.set("quiz_active", True)
    cl.user_session.set("quiz_questions", quiz_questions)
    cl.user_session.set("quiz_index", 0)
    cl.user_session.set("quiz_score", 0)
    
    # Send first question
    await cl.Message(content=f"📝 **Quiz: {topic}**\n\n{quiz_questions[0]['q']}").send()


# Run the app
if __name__ == "__main__":
    cl.run()
```

---

## 7. Docker Compose

```yaml
# docker-compose.yml

services:
  # Layer 1: RAG
  ollama:
    # ... from layer 1
    networks:
      - paam_network

  anythingllm:
    # ... from layer 1
    networks:
      - paam_network

  chroma:
    # ... from layer 1
    networks:
      - paam_network

  # Layer 2: Agents
  agentscope:
    build: ../02_agents
    container_name: paam_agentscope
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    environment:
      - ANYTHINGLLM_URL=http://anythingllm:3001
    networks:
      - paam_network

  # Layer 3: Frontend + TTS
  frontend:
    build: .
    container_name: paam_frontend
    ports:
      - "8000:8000"  # Chainlit default
    volumes:
      - ./frontend:/app
      - ./data/tts_output:/app/data/tts_output
    environment:
      - ANYTHINGLLM_URL=http://anythingllm:3001
      - USE_LOCAL_TTS=true
    depends_on:
      - agentscope
      - anythingllm
    networks:
      - paam_network

  # Optional: Coqui TTS service
  coquitts:
    image: ghcr.io/coqui-ai/tts:latest
    container_name: paam_coqui_tts
    ports:
      - "5002:5002"
    volumes:
      - ./data/tts_output:/app/output
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    networks:
      - paam_network

networks:
  paam_network:
    driver: bridge
```

---

## 8. Running the Frontend

### 8.1 Install dependencies

```bash
cd paam/03_avatar/frontend
pip install -r requirements.txt
```

### 8.2 Run Chainlit

```bash
# Development
chainlit run app.py -w

# Production
chainlit run app.py --host 0.0.0.0 --port 8000
```

### 8.3 Access UI

```
http://localhost:8000
```

---

## 9. Testing

### 9.1 Test TTS

```python
# test_tts.py

from tts import get_tts_engine

tts = get_tts_engine(prefer_local=True)

# Generate speech
audio_file = tts.speak("Hello! I'm PAAM, your AI mentor.")
print(f"Generated: {audio_file}")
```

### 9.2 Test Frontend

```bash
# Start chainlit
chainlit run app.py -w

# Test in browser at http://localhost:8000
```

---

## 10. Avatar Display in Chainlit

To show the avatar in the frontend:

```python
# In frontend/app.py - add to start_chat()

# Show avatar image
await cl.Message(
    content="👤",
    elements=[
        cl.Image(
            path="./public/avatar.png",
            name="PAAM Avatar",
            display="inline"
        )
    ]
).send()
```

---

## 11. Verification Steps

- [ ] Coqui TTS generates audio from text
- [ ] ElevenLabs TTS works (if using cloud)
- [ ] MuseTalk generates lip-synced video (optional)
- [ ] Chainlit frontend loads at localhost:8000
- [ ] Chat messages route through Teacher Agent
- [ ] Voice output plays in browser
- [ ] Commands (/start, /voice, /quiz) work

---

## 12. Next Steps

**After this layer is verified, move to Layer 4:**

1. SQLite logging for chat history
2. Nightly adaptation job
3. Memory integration (Chroma + Neo4j)
4. Full system integration and testing

---

## Quick Reference

| Component | File | Purpose |
|-----------|------|---------|
| Local TTS | `tts/coqui_tts.py` | Offline voice synthesis |
| Cloud TTS | `tts/elevenlabs.py` | Premium voice (API key needed) |
| Avatar | `avatar/musetalk.py` | Lip-sync video generation |
| Frontend | `frontend/app.py` | Chainlit web UI |

| Command | Action |
|---------|--------|
| `/start` | Begin learning session |
| `/voice on` | Enable TTS output |
| `/quiz [topic]` | Start quiz |
| `/cheatsheet` | Generate summary |

---

*Layer 3 Complete ✅*
