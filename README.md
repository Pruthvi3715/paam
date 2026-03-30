# PAAM - Personal Adaptive AI Mentor

## Quick Start Guide

This is a **4-layer project** designed to run in **4 parallel opencode sessions**.

---

## Layer Files

| # | File | Layer | What It Sets Up |
|---|------|-------|-----------------|
| 1 | `01_rag_knowledge.md` | RAG/Knowledge | AnythingLLM + Ollama + Chroma |
| 2 | `02_agents.md` | Agents | AgentScope with 4 agents |
| 3 | `03_avatar.md` | Avatar | TTS + MuseTalk + Chainlit frontend |
| 4 | `04_fullstack.md` | Full Stack | SQLite + Nightly adapt + Integration |

---

## How to Run in Parallel

### Step 1: Open 4 Terminals

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Terminal 1  │ Terminal 2  │ Terminal 3  │ Terminal 4  │
│ 01_rag_     │ 02_agents   │ 03_avatar   │ 04_full     │
│ knowledge   │             │             │ stack       │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### Step 2: Run Each Session

**Session 1 (Terminal 1):**
```bash
cd C:\Users\pshin\CODEE\timepass\01_rag_knowledge
# Follow instructions in 01_rag_knowledge.md
```

**Session 2 (Terminal 2):**
```bash
cd C:\Users\pshin\CODEE\timepass\02_agents
# Follow instructions in 02_agents.md
```

**Session 3 (Terminal 3):**
```bash
cd C:\Users\pshin\CODEE\timepass\03_avatar
# Follow instructions in 03_avatar.md
```

**Session 4 (Terminal 4):**
```bash
cd C:\Users\pshin\CODEE\timepass\04_fullstack
# Follow instructions in 04_fullstack.md
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Frontend                         │
│              (Chainlit - localhost:8000)            │
└─────────────────────────────────────────────────────┘
                          │
┌─────────────────────────┼─────────────────────────┐
│                   Teacher Agent                     │
│  (Orchestrator - Routes to other agents)           │
├─────────────┬──────────────────┬────────────────────┤
│ Lecture     │ Student          │ Session            │
│ Agent       │ Agent            │ Agent              │
│ (RAG)       │ (Profile)        │ (Time/History)     │
└─────────────┴──────────────────┴────────────────────┘
                          │
┌─────────────────────────┼─────────────────────────┐
│              AnythingLLM API                         │
│  (RAG + Chroma + Whisper)                          │
├─────────────────────────────────────────────────────┤
│              Ollama (LLM + Embeddings)              │
└─────────────────────────────────────────────────────┘
```

---

## Dependencies

- **Docker Desktop** with GPU support
- **RTX 3060+ GPU** (8GB+ VRAM)
- **16GB RAM**

---

## Ports

| Service | URL |
|---------|-----|
| AnythingLLM | http://localhost:3001 |
| Ollama | http://localhost:11434 |
| Chroma | http://localhost:8000 |
| Chainlit Frontend | http://localhost:8000 |

---

## Quick Verification

```bash
# Check all services
curl http://localhost:3001/api/health   # AnythingLLM
curl http://localhost:11434/api/tags    # Ollama
curl http://localhost:8000              # Frontend
```

---

## Troubleshooting

### GPU Not Detected
```bash
# Check nvidia-smi
nvidia-smi

# Restart Docker Desktop
```

### Services Can't Connect
```bash
# Check network
docker network inspect paam_network

# Restart containers
docker-compose down && docker-compose up -d
```

### Out of Memory
```bash
# Use smaller models
# In .env: LLM_MODEL=llama3.1:8b
# In .env: EMBEDDING_MODEL=nomic-embed-text
```

---

## License

MIT

---

*End of README*
