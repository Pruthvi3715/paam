import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any


class NightlyAdapter:
    """Nightly job to adapt student profile based on interaction data"""

    def __init__(self, profile_path: str = "./storage/student_profile.json"):
        self.profile_path = Path(profile_path)
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        self.profile = self._load_profile()

    def _load_profile(self) -> Dict[str, Any]:
        """Load current student profile"""
        if self.profile_path.exists():
            with open(self.profile_path) as f:
                return json.load(f)

        return {
            "style": "reading",
            "mastery_rate": 0.0,
            "weak_concepts": [],
            "confusion_history": [],
            "quiz_scores": [],
            "session_count": 0,
            "prompt_version": 1,
            "last_updated": None,
        }

    def _save_profile(self):
        """Save updated profile"""
        self.profile["last_updated"] = datetime.now().isoformat()
        with open(self.profile_path, "w") as f:
            json.dump(self.profile, f, indent=2)

    def analyze_and_update(self):
        """Main nightly analysis and update function"""

        try:
            from ..db.database import db
        except ImportError:
            import sys
            from pathlib import Path

            sys.path.insert(0, str(Path(__file__).parent.parent))
            from db.database import db

        confusion_concepts = db.get_all_confusion_concepts()

        quiz_trend = db.get_quiz_trend(days=7)

        new_mastery = 0.0
        if quiz_trend:
            new_mastery = sum([q["score"] for q in quiz_trend]) / len(quiz_trend)

        self.profile["weak_concepts"] = confusion_concepts
        self.profile["mastery_rate"] = new_mastery

        self.profile["prompt_version"] += 1

        self._save_profile()

        return {
            "updated": True,
            "new_mastery": new_mastery,
            "weak_concepts": confusion_concepts,
            "prompt_version": self.profile["prompt_version"],
        }

    def detect_learning_style(self) -> str:
        """Detect learning style from interaction patterns"""

        return self.profile.get("style", "reading")


nightly_adapter = NightlyAdapter()
