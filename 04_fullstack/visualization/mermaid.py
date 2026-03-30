from typing import List
import requests


class MermaidGenerator:
    """Generate Mermaid diagrams from concepts"""

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "llama3.1:70b"

    def generate_flowchart(self, concept: str, steps: List[str]) -> str:
        """Generate a flowchart"""

        steps_md = "\n".join([f"    {i + 1}[{step}]" for i, step in enumerate(steps)])
        connections = "\n".join(
            [f"    {i + 1} --> {i + 2}" for i in range(len(steps) - 1)]
        )

        return f"""```mermaid
flowchart TD
{steps_md}
{connections}
```"""

    def generate_mindmap(self, topic: str, subtopics: List[str]) -> str:
        """Generate a mind map"""

        subtopics_md = "\n".join([f"      - {s}" for s in subtopics])

        return f"""```mermaid
mindmap
  root(( {topic} ))
{subtopics_md}
```"""

    def generate_sequence(self, actors: List[str], interactions: List[tuple]) -> str:
        """Generate a sequence diagram"""

        actors_md = "\n".join([f"    {actor}" for actor in actors])
        interactions_md = "\n".join(
            [f"    {a} -> {b}: {desc}" for a, b, desc in interactions]
        )

        return f"""```mermaid
sequenceDiagram
{actors_md}
{interactions_md}
```"""

    def generate_from_llm(self, concept: str) -> str:
        """Generate diagram using LLM"""

        prompt = f"""Create a Mermaid diagram for: {concept}

Output ONLY valid Mermaid code, no explanation.
Choose the best diagram type (flowchart, mindmap, sequence, class, state).

Example:
```mermaid
flowchart TD
    A[Start] --> B[Process]
    B --> C[End]
```
"""

        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 500},
            },
        )

        if response.status_code == 200:
            return response.json().get("response", "")
        return "Error generating diagram"


mermaid_gen = MermaidGenerator()
