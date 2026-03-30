import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Add agents directory to path
agents_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agents")
sys.path.insert(0, agents_path)

# Add tools directory to path
tools_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")
sys.path.insert(0, tools_path)

print("Starting PAAM AgentScope...")
print(f"Python path: {sys.path[:3]}")

try:
    from agents.lecture import LectureAgent
    from agents.student import StudentAgent
    from agents.session import SessionAgent
    from agents.teacher import TeacherAgent
    from config import Config

    print("All imports successful!")
except Exception as e:
    print(f"Import error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)


def create_msg_hub():
    lecture = LectureAgent()
    student = StudentAgent()
    session = SessionAgent()
    teacher = TeacherAgent()

    return {
        "lecture": lecture,
        "student": student,
        "session": session,
        "teacher": teacher,
    }


def run_chat_session(message: str):
    teacher = TeacherAgent()
    return teacher.chat(message)


if __name__ == "__main__":
    print("Initializing Teacher Agent...")
    teacher = TeacherAgent()

    print(teacher.start_session("Python Basics", time_minutes=5))

    response = teacher.chat("What is a variable?")
    print(response)

    print(teacher.end_session())

    # Keep container running
    print("\nAgentScope ready! Keeping container alive...")
    import time

    while True:
        time.sleep(60)
