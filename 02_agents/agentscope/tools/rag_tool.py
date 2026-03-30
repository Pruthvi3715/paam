import requests
from typing import List, Dict, Any

try:
    from agentscope import service

    HAS_AGENTSCOPE = True
except ImportError:
    HAS_AGENTSCOPE = False

    def service(func):
        return func


import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


class RAGTool:
    def __init__(self):
        self.base_url = Config.ANYTHINGLLM_URL
        self.workspace = Config.DEFAULT_WORKSPACE

    def query(self, question: str) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/api/v1/workspace/{self.workspace}/chat",
            json={"message": question, "mode": "chat"},
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "answer": data.get("response", ""),
                "sources": data.get("sources", []),
                "success": True,
            }
        else:
            return {"answer": "", "error": response.text, "success": False}

    def retrieve_context(self, query: str, top_k: int = 5) -> List[str]:
        result = self.query(query)
        return result.get("sources", [])[:top_k]


@service
def retrieve_knowledge(query: str, top_k: int = 5) -> str:
    tool = RAGTool()
    context = tool.retrieve_context(query, top_k)

    if not context:
        return "No relevant information found in the source material."

    context_text = "\n\n".join(
        [f"[Source {i + 1}]: {chunk}" for i, chunk in enumerate(context)]
    )
    return f"Retrieved context:\n{context_text}"
