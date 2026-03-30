# PAAM Layer 2: Multi-Agent System (AgentScope)

> **Status:** Ready for opencode session #2
> **Goal:** Set up AgentScope with 4 specialized agents + MsgHub routing

---

## 1. Prerequisites

- ✅ Layer 1 completed (AnythingLLM + Ollama running)
- Docker Desktop
- Python 3.10+ locally (for AgentScope)

---

## 2. Project Structure

```
paam/
├── 01_rag_knowledge/        # Previous layer
├── 02_agents/               # This layer
│   ├── agentscope/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── lecture.py
│   │   │   ├── student.py
│   │   │   ├── session.py
│   │   │   └── teacher.py
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   └── rag_tool.py
│   │   └── main.py
│   ├── docker-compose.yml
│   └── .env
└── ...
```

---

## 3. Install AgentScope

### 3.1 Create project directory

```bash
mkdir -p paam/02_agents/agentscope/agents
mkdir -paam/02_agents/agentscope/tools
```

### 3.2 Create requirements.txt

```txt
agentscope>=1.0.0
openai>=1.0.0
requests>=2.31.0
python-dotenv>=1.0.0
pydantic>=2.0.0
```

### 3.3 Install locally

```bash
cd paam/02_agents
pip install -r requirements.txt
```

---

## 4. AgentScope Configuration

### 4.1 config.py

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # AnythingLLM API
    ANYTHINGLLM_URL = os.getenv("ANYTHINGLLM_URL", "http://localhost:3001")
    ANYTHINGLLM_API_KEY = os.getenv("ANYTHINGLLM_API_KEY", "")  # Set if configured
    
    # Ollama (fallback direct access)
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:70b")
    
    # Agent settings
    MAX_TOKENS = 300
    TEMPERATURE = 0.7
    
    # Workspace
    DEFAULT_WORKSPACE = "paam_workspace"
    
    # Paths
    PROFILE_DIR = os.getenv("PROFILE_DIR", "./data/profiles")
```

### 4.2 RAG Tool Integration

```python
# agentscope/tools/rag_tool.py

import requests
from typing import List, Dict, Any
from agentscope import msghub, service
from .config import Config

class RAGTool:
    """Tool for querying AnythingLLM RAG system"""
    
    def __init__(self):
        self.base_url = Config.ANYTHINGLLM_URL
        self.workspace = Config.DEFAULT_WORKSPACE
    
    def query(self, question: str) -> Dict[str, Any]:
        """Query the knowledge base"""
        response = requests.post(
            f"{self.base_url}/api/v1/workspace/{self.workspace}/chat",
            json={
                "message": question,
                "mode": "chat"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "answer": data.get("response", ""),
                "sources": data.get("sources", []),
                "success": True
            }
        else:
            return {
                "answer": "",
                "error": response.text,
                "success": False
            }
    
    def retrieve_context(self, query: str, top_k: int = 5) -> List[str]:
        """Retrieve top-k relevant chunks"""
        result = self.query(query)
        return result.get("sources", [])[:top_k]


# Register as AgentScope service
@service
def retrieve_knowledge(query: str, top_k: int = 5) -> str:
    """Agent tool: Retrieve knowledge from RAG system"""
    tool = RAGTool()
    context = tool.retrieve_context(query, top_k)
    
    if not context:
        return "No relevant information found in the source material."
    
    context_text = "\n\n".join([
        f"[Source {i+1}]: {chunk}" for i, chunk in enumerate(context)
    ])
    return f"Retrieved context:\n{context_text}"
```

---

## 5. Agent Definitions

### 5.1 Lecture Agent

```python
# agentscope/agents/lecture.py

from agentscope import Agent, msghub

LECTURE_AGENT_PROMPT = """You are the Lecture Agent - the source of truth for all uploaded material.

Your responsibilities:
- Answer ONLY based on retrieved knowledge from the source material
- Never hallucinate or add information not in the context
- Extract key concepts and facts
- Provide precise, accurate information

If you don't have enough information, say: "I don't have enough context to answer that. Would you like me to explain what's available?"

Scope: Source material only
"""

class LectureAgent(Agent):
    """Agent for retrieving and presenting source knowledge"""
    
    def __init__(self, name: str = "lecture_agent"):
        super().__init__(
            name=name,
            sys_prompt=LECTURE_AGENT_PROMPT,
            model=Config.OLLAMA_MODEL,
            api_base=Config.OLLAMA_URL,
            tools=[retrieve_knowledge]
        )
    
    def query(self, question: str) -> str:
        """Query the lecture material"""
        context = retrieve_knowledge(question, top_k=5)
        prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {question}

Answer:"""
        return self.chat(prompt)
```

### 5.2 Student Agent

```python
# agentscope/agents/student.py

import json
import os
from pathlib import Path
from typing import Dict, Any

STUDENT_AGENT_PROMPT = """You are the Student Agent - the guardian of learner profile data.

Your responsibilities:
- Track learning style (visual, auditory, reading, kinesthetic)
- Monitor mastery rates and weak concepts
- Store and retrieve student preferences
- Analyze confusion patterns

You have access to the student_profile.json file.
"""

class StudentAgent:
    """Agent for managing student profile and learning data"""
    
    def __init__(self, profile_path: str = "./data/profiles/student_profile.json"):
        self.profile_path = Path(profile_path)
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        self.profile = self._load_profile()
    
    def _load_profile(self) -> Dict[str, Any]:
        """Load or initialize student profile"""
        if self.profile_path.exists():
            with open(self.profile_path) as f:
                return json.load(f)
        
        # Default profile
        default = {
            "style": "reading",
            "mastery_rate": 0.0,
            "weak_concepts": [],
            "confusion_history": [],
            "quiz_scores": [],
            "session_count": 0,
            "prompt_version": 1
        }
        self._save_profile(default)
        return default
    
    def _save_profile(self, profile: Dict[str, Any]):
        """Save student profile"""
        with open(self.profile_path, 'w') as f:
            json.dump(profile, f, indent=2)
    
    def get_style(self) -> str:
        """Get current learning style"""
        return self.profile.get("style", "reading")
    
    def get_weak_concepts(self) -> list:
        """Get weak concepts to review"""
        return self.profile.get("weak_concepts", [])
    
    def get_mastery_rate(self) -> float:
        """Get overall mastery rate"""
        return self.profile.get("mastery_rate", 0.0)
    
    def update_profile(self, style: str = None, mastery: float = None, 
                       weak_concepts: list = None, quiz_score: float = None,
                       confusion: str = None):
        """Update student profile"""
        if style:
            self.profile["style"] = style
        if mastery is not None:
            self.profile["mastery_rate"] = mastery
        if weak_concepts:
            existing = set(self.profile.get("weak_concepts", []))
            self.profile["weak_concepts"] = list(existing.union(weak_concepts))
        if quiz_score is not None:
            self.profile["quiz_scores"].append(quiz_score)
            # Keep only last 20 scores
            self.profile["quiz_scores"] = self.profile["quiz_scores"][-20:]
            # Recalculate mastery
            if self.profile["quiz_scores"]:
                self.profile["mastery_rate"] = sum(self.profile["quiz_scores"]) / len(self.profile["quiz_scores"])
        if confusion:
            self.profile["confusion_history"].append({
                "concept": confusion,
                "timestamp": "now"  # Use actual timestamp in production
            })
        
        self.profile["session_count"] += 1
        self._save_profile(self.profile)
    
    def get_profile_summary(self) -> str:
        """Get formatted profile for Teacher Agent"""
        return f"""Student Profile:
- Learning Style: {self.get_style()}
- Mastery Rate: {self.get_mastery_rate():.1%}
- Weak Concepts: {', '.join(self.get_weak_concepts()) or 'None'}
- Sessions Completed: {self.profile.get('session_count', 0)}"""
```

### 5.3 Session Agent

```python
# agentscope/agents/session.py

import json
from datetime import datetime
from typing import Dict, Any, List

SESSION_AGENT_PROMPT = """You are the Session Agent - manages the current learning session.

Your responsibilities:
- Track time remaining in the session
- Maintain session history (topics covered, questions asked)
- Provide session summaries
- Enforce time-box constraints
"""

class SessionAgent:
    """Agent for managing current session state"""
    
    def __init__(self, session_id: str = None, time_limit_minutes: int = 45):
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.time_limit_minutes = time_limit_minutes
        self.start_time = datetime.now()
        self.topics_covered: List[str] = []
        self.questions_asked: List[str] = []
        self.responses_given: List[str] = []
    
    def get_time_remaining(self) -> int:
        """Get remaining time in minutes"""
        elapsed = (datetime.now() - self.start_time).total_seconds() / 60
        return max(0, int(self.time_limit_minutes - elapsed))
    
    def is_time_up(self) -> bool:
        """Check if session time is exhausted"""
        return self.get_time_remaining() <= 0
    
    def record_topic(self, topic: str):
        """Record a topic that was covered"""
        if topic not in self.topics_covered:
            self.topics_covered.append(topic)
    
    def record_question(self, question: str, response: str):
        """Record a Q&A exchange"""
        self.questions_asked.append(question)
        self.responses_given.append(response)
    
    def get_session_summary(self) -> str:
        """Get formatted session summary"""
        elapsed = (datetime.now() - self.start_time).total_seconds() / 60
        return f"""Session: {self.session_id}
Time Elapsed: {elapsed:.1f} minutes
Time Remaining: {self.get_time_remaining()} minutes
Topics Covered: {len(self.topics_covered)}
- {', '.join(self.topics_covered)}
Questions Asked: {len(self.questions_asked)}"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Export session data"""
        return {
            "session_id": self.session_id,
            "time_limit": self.time_limit_minutes,
            "start_time": self.start_time.isoformat(),
            "topics_covered": self.topics_covered,
            "questions_asked": self.questions_asked,
            "responses_given": self.responses_given
        }
```

### 5.4 Teacher Agent (Orchestrator)

```python
# agentscope/agents/teacher.py

from .lecture import LectureAgent
from .student import StudentAgent
from .session import SessionAgent

TEACHER_AGENT_PROMPT = """You are PAAM, the Personal Adaptive AI Mentor.

Your role is to orchestrate the learning experience by:
1. Loading the student profile (style, weak concepts, mastery)
2. Checking session context (time remaining, topics covered)
3. Querying lecture material for accurate answers
4. Synthesizing responses in the student's preferred style
5. Applying guardrails (stay on topic, max 250 words)

Rules:
- Always ground answers in Lecture Agent's retrieved content
- Teach in the student's detected style
- Stay within the time-box
- If off-topic, redirect: "Let's stay focused on [topic]."
- Max 250 words per reply
- Use Mermaid diagrams for visual learners
- Use audio explanations for auditory learners
"""

class TeacherAgent:
    """Main orchestrator agent - user-facing"""
    
    def __init__(self, workspace: str = "paam_workspace"):
        self.workspace = workspace
        self.lecture = LectureAgent()
        self.student = StudentAgent()
        self.session = SessionAgent()
    
    def chat(self, user_message: str) -> str:
        """Process user message and return response"""
        
        # 1. Get student profile
        style = self.student.get_style()
        weak_concepts = self.student.get_weak_concepts()
        mastery_rate = self.student.get_mastery_rate()
        
        # 2. Get session context
        time_remaining = self.session.get_time_remaining()
        topics = self.session.topics_covered
        
        # 3. Check if time is up
        if self.session.is_time_up():
            return "⏰ Time's up for this session! Would you like to continue tomorrow?"
        
        # 4. Route to Lecture Agent for answer
        lecture_response = self.lecture.query(user_message)
        
        # 5. Synthesize response based on style
        response = self._synthesize(
            user_message=user_message,
            lecture_answer=lecture_response,
            style=style,
            weak_concepts=weak_concepts,
            time_remaining=time_remaining,
            topics=topics
        )
        
        # 6. Log the interaction
        self.session.record_question(user_message, response)
        
        return response
    
    def _synthesize(self, user_message: str, lecture_answer: str, 
                    style: str, weak_concepts: list, 
                    time_remaining: int, topics: list) -> str:
        """Synthesize final response based on learning style"""
        
        # Check if this is a confusion signal
        confusion_signals = ["don't understand", "confused", "don't get it", "unclear"]
        if any(signal in user_message.lower() for signal in confusion_signals):
            # Extract concept (simplified)
            concept = user_message
            self.student.update_profile(confusion=concept)
            weak_concepts.append(concept)
        
        # Build style-appropriate response
        if style == "visual":
            # Add diagram suggestions
            response = f"{lecture_answer}\n\n"
            if time_remaining > 30:
                response += "💡 *Want me to show a diagram for this?*"
        
        elif style == "auditory":
            response = f"{lecture_answer}\n\n"
            response += "📢 *Should I explain this aloud?*"
        
        elif style == "kinesthetic":
            response = f"{lecture_answer}\n\n"
            response += "🧪 *Want to try a hands-on example?*"
        
        else:  # reading
            response = lecture_answer
        
        # Add weak concepts reminder
        if weak_concepts and len(weak_concepts) <= 3:
            response += f"\n\n⚠️ *Review later: {', '.join(weak_concepts[-3:])}*"
        
        return response
    
    def start_session(self, topic: str, time_minutes: int = 45):
        """Initialize a new learning session"""
        self.session = SessionAgent(time_limit_minutes=time_minutes)
        self.session.record_topic(topic)
        return f"🎓 Starting {time_minutes}-minute session on '{topic}'. Let's begin!"
    
    def end_session(self) -> str:
        """End session and provide summary"""
        summary = self.session.get_session_summary()
        mastery = self.student.get_mastery_rate()
        return f"""Session Complete! 🎉

{summary}

Overall Mastery: {mastery:.1%}

See you next time!"""
```

---

## 6. MsgHub Routing Setup

```python
# agentscope/main.py

from agentscope import msghub, MsgHub
from agentscope.agents import Agent
from .agents.lecture import LectureAgent
from .agents.student import StudentAgent
from .agents.session import SessionAgent, Session
from .agents.teacher import TeacherAgent
from .config import Config

def create_msg_hub():
    """Create the message hub for agent communication"""
    
    # Initialize agents
    lecture = LectureAgent()
    student = StudentAgent()
    session = SessionAgent()
    teacher = TeacherAgent()
    
    # Create hub with all agents
    hub = MsgHub(
        agents=[lecture, student, session],
        routing_policy="sequential"  # Sequential for predictable flow
    )
    
    return {
        "hub": hub,
        "lecture": lecture,
        "student": student,
        "session": session,
        "teacher": teacher
    }

def run_chat_session(message: str):
    """Run a chat message through the agent system"""
    # Direct to teacher for now (simplified for v1)
    teacher = TeacherAgent()
    return teacher.chat(message)
```

---

## 7. Docker Deployment (Optional)

```yaml
# docker-compose.yml for AgentScope service

services:
  agentscope:
    build: .
    container_name: paam_agentscope
    ports:
      - "5000:5000"
    volumes:
      - ./agentscope:/app
      - ./data:/app/data
    environment:
      - ANYTHINGLLM_URL=http://anythingllm:3001
      - OLLAMA_URL=http://ollama:11434
    depends_on:
      - ollama
      - anythingllm
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

---

## 8. Testing

### 8.1 Test Individual Agents

```python
# test_agents.py

from agentscope.agents.student import StudentAgent
from agentscope.agents.session import SessionAgent

# Test Student Agent
student = StudentAgent()
print(student.get_profile_summary())

student.update_profile(style="visual", quiz_score=0.8)
print(f"New style: {student.get_style()}")
print(f"Mastery: {student.get_mastery_rate()}")

# Test Session Agent
session = SessionAgent(time_limit_minutes=10)
print(f"Time remaining: {session.get_time_remaining()}")
session.record_topic("Python Basics")
print(session.get_session_summary())
```

### 8.2 Test Full Flow

```python
# test_teacher.py

from agentscope.agents.teacher import TeacherAgent

teacher = TeacherAgent()

# Start session
print(teacher.start_session("Machine Learning", time_minutes=5))

# Chat
response = teacher.chat("What is a neural network?")
print(response)

# End session
print(teacher.end_session())
```

---

## 9. Verification Steps

- [ ] StudentAgent loads/creates profile correctly
- [ ] SessionAgent tracks time and topics
- [ ] LectureAgent retrieves from AnythingLLM
- [ ] TeacherAgent orchestrates and responds
- [ ] All 4 agents communicate via MsgHub

---

## 10. Next Steps

**After this layer is verified, move to Layer 3:**

1. Coqui TTS or ElevenLabs for voice
2. MuseTalk/LivePortrait for avatar lip-sync
3. Chainlit frontend integration

---

## Quick Reference

| Agent | File | Responsibility |
|-------|------|----------------|
| Lecture | `agents/lecture.py` | RAG retrieval, ground truth |
| Student | `agents/student.py` | Profile, style, mastery |
| Session | `agents/session.py` | Time, history, topics |
| Teacher | `agents/teacher.py` | Orchestrator, user-facing |

---

*Layer 2 Complete ✅*
