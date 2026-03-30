# PAAM Layer 1: RAG & Knowledge Base

> **Status:** Ready for opencode session #1
> **Goal:** Set up AnythingLLM with Ollama for RAG-powered knowledge base

---

## 1. Prerequisites

### Hardware
- NVIDIA GPU with 8GB+ VRAM (RTX 3060+)
- 16GB RAM minimum
- 50GB+ free disk space

### Pre-installed
- Docker Desktop
- Git

---

## 2. Project Structure

```
paam/
├── 01_rag_knowledge/        # This layer
│   ├── docker-compose.yml   # AnythingLLM + Ollama
│   ├── .env                 # Configuration
│   └── data/                # Persistent data
├── 02_agents/               # (next layer)
├── 03_avatar/              # (next layer)
└── 04_fullstack/           # (next layer)
```

---

## 3. Docker Setup

### 3.1 Create directories

```bash
mkdir -p paam/01_rag_knowledge/data
cd paam/01_rag_knowledge
```

### 3.2 Create docker-compose.yml

```yaml
version: '3.9'

services:
  # Local LLM Backend
  ollama:
    image: ollama/ollama:latest
    container_name: paam_ollama
    ports:
      - "11434:11434"
    volumes:
      - ./data/ollama:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped

  # AnythingLLM (RAG + Chat Interface)
  anythingllm:
    image: mintplexlabs/anythingllm:latest
    container_name: paam_anythingllm
    ports:
      - "3001:3001"
    volumes:
      - ./data/anythingllm:/app/server/storage
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - LLM_PROVIDER=ollama
      - LLM_MODEL=llama3.1:70b
      - EMBEDDING_MODEL=nomic-embed-text
      - EMBEDDING_PROVIDER=ollama
      - VECTOR_DB=chroma
      - CHROMA_ENDPOINT=http://chroma:8000
    depends_on:
      - ollama
      - chroma
    restart: unless-stopped

  # Chroma Vector Database
  chroma:
    image: chromadb/chroma:latest
    container_name: paam_chroma
    ports:
      - "8000:8000"
    volumes:
      - ./data/chroma:/chroma/chroma
    restart: unless-stopped

networks:
  default:
    name: paam_network
```

### 3.3 Create .env file

```bash
# Ollama
OLLAMA_HOST=0.0.0.0:11434

# AnythingLLM
LLAMA_CLOUD_API_KEY=  # Optional: for premium embeddings
ANTHROPIC_API_KEY=    # Optional: for Claude
OPENAI_API_KEY=       # Optional: for GPT

# Storage
STORAGE_DIR=/app/server/storage
```

---

## 4. Start Services

```bash
cd paam/01_rag_knowledge
docker-compose up -d
```

### Verify services are running

```bash
# Check container status
docker ps

# Check Ollama is responding
curl http://localhost:11434/api/tags

# Check AnythingLLM
curl http://localhost:3001/api/health
```

### Pull required models

```bash
# SSH into Ollama container and pull models
docker exec -it paam_ollama ollama pull llama3.1:70b
docker exec -it paam_ollama ollama pull nomic-embed-text
```

> **Note:** First pull may take 20-40 minutes depending on model size.

---

## 5. AnythingLLM Configuration

### 5.1 Access Web UI

Open browser: http://localhost:3001

### 5.2 Setup Wizard

1. **Workspace name:** `paam_workspace`
2. **LLM Provider:** Ollama
3. **Model:** llama3.1:70b
4. **Embedding Model:** nomic-embed-text
5. **Vector Database:** Chroma

### 5.3 Add Test Content

Try uploading a PDF or pasting a YouTube URL:

```
https://www.youtube.com/watch?v=your-video-id
```

AnythingLLM will:
- Transcribe video with Whisper
- Chunk the content
- Generate embeddings with nomic-embed-text
- Store in Chroma

---

## 6. API Integration (For Next Layer)

### 6.1 Chat API Example

```python
import requests

BASE_URL = "http://localhost:3001"

def chat_with_workspace(message: str, workspace: str = "paam_workspace"):
    """Send a message to the RAG system"""
    response = requests.post(
        f"{BASE_URL}/api/v1/workspace/{workspace}/chat",
        json={
            "message": message,
            "mode": "chat"
        }
    )
    return response.json()

# Test
result = chat_with_workspace("What is this document about?")
print(result["response"])
```

### 6.2 Document Ingestion API

```python
def ingest_youtube_video(url: str, workspace: str = "paam_workspace"):
    """Ingest a YouTube video into the knowledge base"""
    response = requests.post(
        f"{BASE_URL}/api/v1/workspace/{workspace}/embeddings",
        json={
            "url": url,
            "embed_method": "chroma"
        }
    )
    return response.json()

# Test
result = ingest_youtube_video("https://www.youtube.com/watch?v=...")
print(result)
```

### 6.3 Get Available Workspaces

```python
def list_workspaces():
    """List all workspaces"""
    response = requests.get(f"{BASE_URL}/api/v1/workspaces")
    return response.json()
```

---

## 7. Verification Steps

### Check 1: Ollama Running
```bash
curl http://localhost:11434/api/tags
# Should return list of available models
```

### Check 2: Chroma Running
```bash
curl http://localhost:8000/api/v1/collections
# Should return empty list or existing collections
```

### Check 3: AnythingLLM Web UI
- Open http://localhost:3001
- Should see login/setup screen

### Check 4: RAG Functionality
1. Upload a test PDF in AnythingLLM
2. Ask a question about the content
3. Verify answer is grounded in the document

### Check 5: API Response
```bash
curl -X POST http://localhost:3001/api/v1/workspace/paam_workspace/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "mode": "chat"}'
```

---

## 8. Troubleshooting

### Ollama not using GPU
```bash
# Check nvidia-smi inside container
docker exec -it paam_ollama nvidia-smi
```

### AnythingLLM can't connect to Ollama
```bash
# Check logs
docker logs paam_anythingllm

# Verify network
docker network inspect paam_network
```

### Models not loading
```bash
# Pull manually
docker exec -it paam_ollama ollama list
docker exec -it paam_ollama ollama pull llama3.1:70b
```

---

## 9. Next Steps

**After this layer is verified, move to Layer 2:**

1. AgentScope setup with 4 agents
2. Connect to AnythingLLM API
3. Implement Lecture/Student/Session/Teacher agent architecture

---

## 10. Quick Reference

| Service | URL | Credentials |
|---------|-----|-------------|
| AnythingLLM | http://localhost:3001 | Set on first run |
| Ollama | http://localhost:11434 | - |
| Chroma | http://localhost:8000 | - |

---

*Layer 1 Complete ✅*
