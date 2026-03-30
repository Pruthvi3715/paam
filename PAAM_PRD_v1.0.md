# PAAM — Personal Adaptive AI Mentor

## Product Requirements Document · v1.0 · 2026

| Status | Version | Author | Date |
|--------|---------|--------|------|
| Draft | 1.0 | Pruthviraj | March 2026 |

---

## Table of Contents

1. [Product Vision](#1-product-vision)
2. [Core Goals](#2-core-goals)
3. [Key Features](#3-key-features)
4. [AgentScope Integration Details](#4-agentscope-integration-details)
5. [Database & Storage Layer](#5-database--storage-layer)
6. [Additional Integrations](#6-additional-integrations)
7. [Recommended Tech Stack](#7-recommended-tech-stack)
8. [Adaptive Learning Mechanism](#8-adaptive-learning-mechanism)
9. [Core User Flows](#9-core-user-flows)
10. [Non-Functional Requirements](#10-non-functional-requirements)
11. [Out of Scope (v1.0)](#11-out-of-scope-v10)
12. [Success Metrics](#12-success-metrics)
13. [Quick-Start Prototype Plan](#13-quick-start-prototype-plan)
- [Appendix A — Prompt Templates](#appendix-a--prompt-templates)

---

## 1. Product Vision

PAAM is a private, self-hosted AI study companion that transforms any video, book, or document into a living, talking mentor. It teaches anything — from pasta recipes to advanced engineering — remembers your exact learning style, tracks your doubts, stays laser-focused on the topic at hand, and continuously grows smarter at teaching you over time.

**The core promise:**

- You upload any learning material.
- A scoped multi-agent system extracts, organises, and grounds all knowledge.
- A talking avatar mentor teaches you in your preferred style (visual, auditory, reading, kinesthetic).
- Three memory layers ensure the mentor never hallucinates, never forgets your weaknesses, and always knows where the session left off.
- Everything runs 100% locally — no cloud lock-in, no subscriptions.

---

## 2. Core Goals

| Goal | Description | Success Indicator |
|------|-------------|-------------------|
| Zero Hallucinations | All answers grounded strictly in uploaded source material | 0 factually incorrect answers per session |
| Full Adaptability | Auto-detect and adjust to visual / auditory / reading / kinesthetic style | Mastery rate improves week-over-week |
| Time-Box Awareness | Honest, realistic lesson plans scoped to available time | Lessons complete on time 90%+ |
| Cross-Domain Linking | Connect new topics to everything in the knowledge vault | Students report "aha" moments in feedback |
| Private & Local | Runs on user hardware with no cloud dependency | Zero data leaves the device |

---

## 3. Key Features

### 3.1 Ingestion Pipeline

- **Video / YouTube:** yt-dlp + faster-whisper for transcription.
- **Books / PDFs:** Direct text extraction + Gemini Embedding 2 for multimodal chunks.
- **Live web content:** Scrapling agent fetches up-to-date supplementary material on demand (user-confirmed).
- **Output:** Structured notes, auto-generated cheatsheets, Mermaid diagrams.

### 3.2 4-Agent Scoped Architecture (AgentScope)

| Agent | Scope | Key Responsibility |
|-------|-------|--------------------|
| Lecture Agent | Source material only | RAG retrieval, concept extraction, zero-hallucination grounding |
| Student Agent | Learner profile only | Style detection, mastery tracking, nightly prompt adaptation |
| Session Agent | Current lesson only | Time-box enforcement, session summary, continuity across sessions |
| Teacher Agent | Orchestrator (user-facing) | Routes queries, applies style, enforces guardrails, outputs reply + avatar command |

### 3.3 3-Layer Memory System

- **Lecture Memory** — ground-truth facts from the uploaded source. Vector store (Chroma) + Graphiti knowledge graph on Neo4j.
- **Student Memory** — your learning style, weak points, confusion history, mastery scores. Neo4j graph + `student_profile.json` (updated nightly).
- **Session Memory** — what happened today: topics covered, questions asked, quiz score. AgentScope native short-term buffer + SQLite log.

### 3.4 Talking Avatar Mentor

- MuseTalk or LivePortrait for real-time lip-sync from any reference photo.
- Coqui TTS (local) or ElevenLabs (optional cloud) for voice synthesis.
- Chainlit or Gradio frontend embeds the avatar stream.

### 3.5 Adaptive Learning Engine

- Detects style from behaviour: skips text = visual; asks for audio replay = auditory; prefers step-by-step = kinesthetic.
- Nightly job scans chat logs and quiz scores; auto-updates `student_profile.json` with new style flags and weak concepts.
- Teacher Agent loads the profile at session start and swaps its system prompt accordingly.

### 3.6 Focus Guardrails

- Every agent has a strict scope prompt — cannot discuss topics outside its defined boundary.
- Teacher Agent runs a final relevance check before every reply.
- Response length capped at 150–250 words; topic-lock keywords (e.g., "back to topic") trigger a hard reset.

### 3.7 Cheatsheet & Visualisation Generator

- **Cheatsheets:** LLM prompt converts structured notes into a concise single-page Markdown/PDF cheatsheet with tables, mnemonics, and analogies.
- **Diagrams:** Mermaid flowcharts / mind maps / sequence diagrams rendered inline (Streamlit / Chainlit).
- **AI images:** Optional Flux / Grok Imagine API for illustrated concept cards.

### 3.8 Universal Subject Support

- No hard-coded subjects. Every session starts fresh from the uploaded material.
- **Time-box scaler:** user states available time; system auto-selects depth (basics-only for 10 min; deep dive for 1 hour).
- "Impossible" requests handled gracefully: system responds with a realistic roadmap instead of over-promising.

---

## 4. AgentScope Integration Details

### 4.1 Why AgentScope?

AgentScope (v1.x, 2026) is chosen as the orchestration layer for the following reasons:

- First-class multi-agent support with **MsgHub** for strict, controlled message routing.
- Native short-term and long-term memory modules with ReMe integration.
- Built-in RAG tools, ReAct agent pattern, and guardrail-friendly prompt system.
- 100% local Python runtime — compatible with Ollama, no cloud required.
- Human-in-the-loop support and persistence out of the box.

### 4.2 Communication Flow

```
User Message
     │
     ▼
Teacher Agent  ◄──── loads student_profile.json
     │
     ├──► Lecture Agent   → retrieves ground-truth facts from Chroma/Graphiti
     ├──► Student Agent   → returns current style + mastery + weak concepts
     └──► Session Agent   → returns time remaining + today's context
     │
     ▼
Teacher synthesizes → applies guardrails → final reply + avatar command
```

> **Nightly:** Student Agent scans SQLite logs → updates `student_profile.json` → Teacher Agent loads updated profile next morning.

### 4.3 Guardrail Specification

| Guardrail | Implementation | Effect |
|-----------|---------------|--------|
| Scope lock | System prompt: "You may ONLY respond about [scope]. Off-topic? Reply: 'Staying focused.'" | Prevents topic drift per agent |
| Focus checker | Teacher Agent rates its own reply relevance (0–10); below 8 = re-prompt | 90%+ on-topic replies |
| Length cap | `max_tokens = 300` per reply | Keeps sessions concise |
| Topic-lock keyword | User says "back to [topic]" or "reset" → hard session reset | Instant context recovery |

### 4.4 Agent Definitions (Summary)

**Lecture Agent**
- Scope: source material only
- Tools: `retrieve_knowledge`, `extract_key_concepts`
- Memory: Chroma vector store + Graphiti nodes

**Student Agent**
- Scope: learner profile only
- Tools: `update_profile`, `get_learning_style`, `get_mastery_rate`
- Memory: Neo4j graph + `student_profile.json`

**Session Agent**
- Scope: current lesson timeline only
- Memory: AgentScope short-term buffer + SQLite

**Teacher Agent**
- Scope: orchestrator (user-facing)
- Queries all three agents via MsgHub before every reply
- Enforces guardrails + outputs final reply + avatar/cheatsheet command

---

## 5. Database & Storage Layer

| Memory Layer | Storage | Purpose | Size Estimate |
|--------------|---------|---------|---------------|
| Lecture Memory | Chroma + Neo4j via Graphiti | Semantic search + knowledge graph of source material | < 1 GB (many courses) |
| Student Memory | Neo4j + `student_profile.json` | Learning style, mastery, confusion edges; temporal fact tracking | < 10 MB |
| Session Memory | AgentScope native + SQLite | Today's lesson log, time-box tracker, progress buffer | Negligible |
| Overall Logs | SQLite (single file) | All chat history for nightly adaptation analysis | < 100 MB after months |

**Key rules:**
- All databases are self-contained (Docker or Python-embedded).
- Backup = copy 3 folders: `chroma/`, `neo4j/`, `sqlite.db` + `student_profile.json`.
- No complex migrations — Graphiti and AgentScope handle all schema evolution.

---

## 6. Additional Integrations

### 6.1 Scrapling (Live Web Enrichment)

- Attached as a tool to Teacher Agent (and optionally Lecture Agent).
- Triggers on demand: "teach me the latest X technique" → scrape → validate against source → ingest to Chroma.
- Always requires explicit user confirmation before fetching external content.
- Output: clean Markdown/JSON piped directly into the lecture memory store.

### 6.2 Always-On Agent Memory

- Background AgentScope worker that continuously summarises, forgets stale facts, and surfaces relevant history.
- Replaces static DB lookups with specialist sub-agents; works on top of existing Neo4j + SQLite stores.
- Maps to all three memory layers: grounding (Lecture), evolution (Student), real-time buffer (Session).
- Open-source implementation (MIT) — zero extra cost.

### 6.3 Gemini Embedding 2 (Multimodal)

- Replaces or augments Chroma's default text embeddings for new uploads.
- Handles text, images, video frames, audio, and PDFs in a single unified **3072-dimensional space**.
- Enables cross-modal retrieval: show a diagram while explaining a concept vocally.
- **Hybrid mode:** Gemini embeddings for uploads; local fallback (`nomic-embed`) for offline / privacy-first use.

**Updated storage view:**

| Layer | Now Uses | Benefit |
|-------|----------|---------|
| Lecture Memory | Chroma + Gemini Embedding 2 + Scrapling | Multimodal + live web data |
| Student Memory | Neo4j + Always-On Memory Agent + JSON | Never forgets your style |
| Session Memory | AgentScope native + Always-On | Real-time + persistent |

---

## 7. Recommended Tech Stack

| Component | Tool | Notes |
|-----------|------|-------|
| Video Ingestion | yt-dlp + faster-whisper | Any YouTube / local video; multilingual |
| Orchestration | AgentScope v1.x | Multi-agent, guardrails, memory, local-first |
| LLM Backend | Ollama (Llama 3.1 70B / Mixtral) | Runs on local GPU; swap for Grok API if needed |
| RAG / NotebookLM | AnythingLLM + Chroma | One-click Docker; YouTube URL support |
| Knowledge Graph | Neo4j + Graphiti | Temporal facts, student weakness tracking |
| Embeddings | Gemini Embedding 2 + nomic-embed (fallback) | Multimodal; local fallback for offline |
| Always-On Memory | Google Always-On Memory Agent (MIT) | Persistent evolving memory across sessions |
| Web Enrichment | Scrapling / Crawl4AI | Demand-only; user-confirmed |
| Avatar | MuseTalk / LivePortrait | Real-time lip-sync from reference photo |
| TTS | Coqui TTS (local) / ElevenLabs | Voice synthesis; local preferred |
| Frontend | Chainlit or Gradio | Web UI; avatar embed; voice input |
| Visualisation | Mermaid + Streamlit | Inline diagrams; AI image optional via Flux |
| Persistence | SQLite + Neo4j + JSON files | Zero server overhead; backup = copy folder |

---

## 8. Adaptive Learning Mechanism

### 8.1 Style Detection

| Signal | Detected Style | Teaching Adaptation |
|--------|---------------|---------------------|
| Skips text; lingers on diagrams | Visual | Start with mind maps / diagrams; use bold colours |
| Replays audio; asks to repeat | Auditory | Speak slowly; repeat key points; suggest voice notes |
| Requests step-by-step; builds things | Kinesthetic | Simulate; build it; hands-on analogies |
| Reads all text; asks for definitions | Reading / Writing | Dense notes; glossaries; written summaries |

### 8.2 Mastery Metrics

- **Mastery Rate:** % of concepts answered correctly after no more than 3 attempts.
- **Confusion Drop:** Fewer "I don't get it" messages per session over time.
- **Quiz Score Trend:** Rolling 7-day average; triggers style-switch if declining.
- **Time-on-Task:** Unusually long pauses flag difficulty — trigger hint / re-explain.

### 8.3 Nightly Adaptation Loop

```
Input   → SQLite chat logs: questions, answers, confusion flags, quiz scores
Process → Student Agent LLM analyses logs, computes new mastery_rate,
          selects weak_concepts, picks optimal style for tomorrow
Output  → student_profile.json updated:
          { "style": "visual", "mastery_rate": 0.74,
            "weak_concepts": ["gluten elasticity"],
            "prompt_version": 7 }
```

Teacher Agent loads `student_profile.json` on next session start — no manual config needed.

---

## 9. Core User Flows

### Flow 1 — Upload & Learn

1. User uploads video URL / PDF / book.
2. Ingestion pipeline transcribes, chunks, embeds (Gemini Embedding 2), stores in Chroma.
3. Lecture Agent builds Graphiti knowledge graph from transcript.
4. User states: "Teach me this in 45 minutes."
5. Teacher Agent queries Session Agent (time-box), Lecture Agent (key concepts), Student Agent (style).
6. Lesson plan generated: 5 concepts × 9 minutes each. Avatar begins teaching.

### Flow 2 — Chat & Doubt Resolution

1. User asks: "I don't understand gluten elasticity."
2. Teacher Agent routes to Lecture Agent (ground-truth retrieval).
3. Student Agent logs confusion flag for "gluten elasticity."
4. Teacher responds in user's style (e.g., visual: includes Mermaid diagram of gluten network).
5. Session Agent records this exchange in today's summary.

### Flow 3 — Nightly Adaptation

1. Scheduler triggers Student Agent at 2 AM.
2. Reads today's SQLite log: 3 confusion flags on "dough elasticity"; quiz 6/10.
3. Updates `student_profile.json`: `weak_concepts += "dough elasticity"`; style confirmed "visual."
4. Tomorrow Teacher Agent opens session: "Last time you had trouble with elasticity — want to start with a diagram?"

---

## 10. Non-Functional Requirements

| Requirement | Specification |
|-------------|---------------|
| Privacy | All processing on-device. No user data leaves the machine. |
| Performance | Response latency < 3 seconds on a mid-range GPU (RTX 3060+). |
| Reliability | Guardrails prevent off-topic drift > 95% of turns. |
| Scalability | Supports 1,000+ lecture hours in Chroma without performance degradation. |
| Portability | Single `docker-compose.yml` bootstraps entire stack. |
| Backup | Full backup = copy 3 folders + `student_profile.json`. |

---

## 11. Out of Scope (v1.0)

- Multi-user / classroom support.
- Mobile native app (web-first only).
- Fine-tuning the base LLM weights (prompt-based adaptation only in v1.0).
- Automatic curriculum generation without any source upload.

---

## 12. Success Metrics

| Metric | Target | How Measured |
|--------|--------|--------------|
| Mastery Rate | > 80% after 3 sessions on any topic | Quiz score log in SQLite |
| On-Topic Rate | > 95% of turns stay in scope | Teacher Agent relevance checker log |
| Style Accuracy | Correct style detected within 2 sessions | User feedback + confusion drop |
| Lesson Time Accuracy | Within 10% of stated time-box | Session Agent timer vs. actual duration |
| Hallucination Rate | 0 factual errors per session | Manual spot-check + Lecture Agent audit |

---

## 13. Quick-Start Prototype Plan

**Weekend MVP (4 steps):**

1. `docker run -p 3001:3001 anythingllm` — connect to Ollama (Llama 3.1 70B). Drop a YouTube URL. Instant RAG knowledge base.
2. Add AgentScope: define 4 agents with scoped system prompts. Wire MsgHub.
3. Add Chainlit frontend + MuseTalk avatar. Test one full lesson flow.
4. Add SQLite logging + Student Agent nightly job. Adaptive loop live.

> Each step is independently testable. Build in order — each step adds value on its own.

---

## Appendix A — Prompt Templates

### Cheatsheet Generator

```
You are an expert teacher. Turn the following notes into a concise cheatsheet
for [topic]. Use markdown tables, bullet points, and bold emphasis.
Include: key formulas, mnemonics, common pitfalls, 1-line analogies.
Fit it on one A4 page mentally.

Notes: [PASTE NOTES]
```

### Visualisation Generator

```
Create a Mermaid flowchart / mindmap / sequence diagram for [concept].
Make it clear, with labels, and educational.
Focus on relationships and flow.
Output only valid Mermaid code.
```

### Scope Guardrail (per Agent)

```
You are the [Lecture / Student / Session] Agent.
You may ONLY respond about [your scope].
If the query is off-topic, reply exactly:
"Staying focused — ask me about [topic]."
Never break this rule.
```

### Teacher Agent System Prompt Template

```
You are PAAM, a personal adaptive AI mentor.
Current student style: {style}
Weak concepts to revisit: {weak_concepts}
Time remaining in session: {time_remaining}
Today's topic: {topic}

Rules:
- Always ground answers in the Lecture Agent's retrieved content.
- Teach in the student's detected style.
- Stay within the time-box.
- If off-topic, redirect: "Let's stay focused on [topic]."
- Max 250 words per reply.
```

---

*End of Document — PAAM PRD v1.0*
