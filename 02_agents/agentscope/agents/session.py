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
    def __init__(self, session_id: str = None, time_limit_minutes: int = 45):
        self.session_id = (
            session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.time_limit_minutes = time_limit_minutes
        self.start_time = datetime.now()
        self.topics_covered: List[str] = []
        self.questions_asked: List[str] = []
        self.responses_given: List[str] = []

    def get_time_remaining(self) -> int:
        elapsed = (datetime.now() - self.start_time).total_seconds() / 60
        return max(0, int(self.time_limit_minutes - elapsed))

    def is_time_up(self) -> bool:
        return self.get_time_remaining() <= 0

    def record_topic(self, topic: str):
        if topic not in self.topics_covered:
            self.topics_covered.append(topic)

    def record_question(self, question: str, response: str):
        self.questions_asked.append(question)
        self.responses_given.append(response)

    def get_session_summary(self) -> str:
        elapsed = (datetime.now() - self.start_time).total_seconds() / 60
        return f"""Session: {self.session_id}
Time Elapsed: {elapsed:.1f} minutes
Time Remaining: {self.get_time_remaining()} minutes
Topics Covered: {len(self.topics_covered)}
- {", ".join(self.topics_covered)}
Questions Asked: {len(self.questions_asked)}"""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "time_limit": self.time_limit_minutes,
            "start_time": self.start_time.isoformat(),
            "topics_covered": self.topics_covered,
            "questions_asked": self.questions_asked,
            "responses_given": self.responses_given,
        }
