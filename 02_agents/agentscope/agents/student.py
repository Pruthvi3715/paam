import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


STUDENT_AGENT_PROMPT = """You are the Student Agent - the guardian of learner profile data.

Your responsibilities:
- Track learning style (visual, auditory, reading, kinesthetic)
- Monitor mastery rates and weak concepts
- Store and retrieve student preferences
- Analyze confusion patterns

You have access to the student_profile.json file.
"""


class StudentAgent:
    def __init__(self, profile_path: str = None):
        if profile_path is None:
            profile_path = os.path.join(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                ),
                "data",
                "profiles",
                "student_profile.json",
            )
        self.profile_path = Path(profile_path)
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        self.profile = self._load_profile()

    def _load_profile(self) -> Dict[str, Any]:
        if self.profile_path.exists():
            with open(self.profile_path) as f:
                return json.load(f)

        default = {
            "style": "reading",
            "mastery_rate": 0.0,
            "weak_concepts": [],
            "confusion_history": [],
            "quiz_scores": [],
            "session_count": 0,
            "prompt_version": 1,
        }
        self._save_profile(default)
        return default

    def _save_profile(self, profile: Dict[str, Any]):
        with open(self.profile_path, "w") as f:
            json.dump(profile, f, indent=2)

    def get_style(self) -> str:
        return self.profile.get("style", "reading")

    def get_weak_concepts(self) -> list:
        return self.profile.get("weak_concepts", [])

    def get_mastery_rate(self) -> float:
        return self.profile.get("mastery_rate", 0.0)

    def update_profile(
        self,
        style: str = None,
        mastery: float = None,
        weak_concepts: list = None,
        quiz_score: float = None,
        confusion: str = None,
    ):
        if style:
            self.profile["style"] = style
        if mastery is not None:
            self.profile["mastery_rate"] = mastery
        if weak_concepts:
            existing = set(self.profile.get("weak_concepts", []))
            self.profile["weak_concepts"] = list(existing.union(weak_concepts))
        if quiz_score is not None:
            self.profile["quiz_scores"].append(quiz_score)
            self.profile["quiz_scores"] = self.profile["quiz_scores"][-20:]
            if self.profile["quiz_scores"]:
                self.profile["mastery_rate"] = sum(self.profile["quiz_scores"]) / len(
                    self.profile["quiz_scores"]
                )
        if confusion:
            self.profile["confusion_history"].append(
                {"concept": confusion, "timestamp": "now"}
            )

        self.profile["session_count"] += 1
        self._save_profile(self.profile)

    def get_profile_summary(self) -> str:
        return f"""Student Profile:
- Learning Style: {self.get_style()}
- Mastery Rate: {self.get_mastery_rate():.1%}
- Weak Concepts: {", ".join(self.get_weak_concepts()) or "None"}
- Sessions Completed: {self.profile.get("session_count", 0)}"""
