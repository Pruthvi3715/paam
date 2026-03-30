import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from tools.rag_tool import retrieve_knowledge


LECTURE_AGENT_PROMPT = """You are the Lecture Agent - the source of truth for all uploaded material.

Your responsibilities:
- Answer ONLY based on retrieved knowledge from the source material
- Never hallucinate or add information not in the context
- Extract key concepts and facts
- Provide precise, accurate information

If you don't have enough information, say: "I don't have enough context to answer that. Would you like me to explain what's available?"

Scope: Source material only
"""


class LectureAgent:
    def __init__(self, name: str = "lecture_agent"):
        self.name = name
        self.sys_prompt = LECTURE_AGENT_PROMPT
        self.model = Config.OLLAMA_MODEL
        self.api_base = Config.OLLAMA_URL

    def _call_ollama(self, prompt: str) -> str:
        response = requests.post(
            f"{self.api_base}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=60,
        )
        if response.status_code == 200:
            return response.json().get("response", "")
        return f"Error: {response.text}"

    def query(self, question: str) -> str:
        context = retrieve_knowledge(question, top_k=5)
        prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {question}

Answer:"""
        return self._call_ollama(prompt)
