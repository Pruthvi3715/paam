from typing import List, Dict
import requests


class CheatsheetGenerator:
    """Generate cheatsheets from study material"""

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "llama3.1:70b"

    def generate(self, topic: str, context: str) -> str:
        """Generate a cheatsheet for the topic"""

        prompt = f"""You are an expert teacher. Create a concise cheatsheet for "{topic}".

Requirements:
- Use markdown format
- Include: key concepts, formulas, mnemonics, common pitfalls
- Use tables for comparisons
- Include 1-line analogies where helpful
- Fit on one A4 page (mentally)
- Use **bold** for emphasis

Context from study material:
{context}

Cheatsheet:"""

        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 800},
            },
        )

        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            return "Error generating cheatsheet"


cheatsheet_gen = CheatsheetGenerator()
