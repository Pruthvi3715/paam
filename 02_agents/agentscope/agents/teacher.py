import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
    def __init__(self, workspace: str = "paam_workspace"):
        self.workspace = workspace
        self.lecture = LectureAgent()
        self.student = StudentAgent()
        self.session = SessionAgent()

    def chat(self, user_message: str) -> str:
        style = self.student.get_style()
        weak_concepts = self.student.get_weak_concepts()
        mastery_rate = self.student.get_mastery_rate()

        time_remaining = self.session.get_time_remaining()
        topics = self.session.topics_covered

        if self.session.is_time_up():
            return "Time's up for this session! Would you like to continue tomorrow?"

        lecture_response = self.lecture.query(user_message)

        response = self._synthesize(
            user_message=user_message,
            lecture_answer=lecture_response,
            style=style,
            weak_concepts=weak_concepts,
            time_remaining=time_remaining,
            topics=topics,
        )

        self.session.record_question(user_message, response)

        return response

    def _synthesize(
        self,
        user_message: str,
        lecture_answer: str,
        style: str,
        weak_concepts: list,
        time_remaining: int,
        topics: list,
    ) -> str:
        confusion_signals = ["don't understand", "confused", "don't get it", "unclear"]
        if any(signal in user_message.lower() for signal in confusion_signals):
            concept = user_message
            self.student.update_profile(confusion=concept)
            weak_concepts.append(concept)

        if style == "visual":
            response = f"{lecture_answer}\n\n"
            if time_remaining > 30:
                response += "*Want me to show a diagram for this?*"

        elif style == "auditory":
            response = f"{lecture_answer}\n\n"
            response += "*Should I explain this aloud?*"

        elif style == "kinesthetic":
            response = f"{lecture_answer}\n\n"
            response += "*Want to try a hands-on example?*"

        else:
            response = lecture_answer

        if weak_concepts and len(weak_concepts) <= 3:
            response += f"\n\n*Review later: {', '.join(weak_concepts[-3:])}*"

        return response

    def start_session(self, topic: str, time_minutes: int = 45):
        self.session = SessionAgent(time_limit_minutes=time_minutes)
        self.session.record_topic(topic)
        return f"Starting {time_minutes}-minute session on '{topic}'. Let's begin!"

    def end_session(self) -> str:
        summary = self.session.get_session_summary()
        mastery = self.student.get_mastery_rate()
        return f"""Session Complete!

{summary}

Overall Mastery: {mastery:.1%}

See you next time!"""
