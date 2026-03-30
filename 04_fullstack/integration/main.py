import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from chainlit import cl
from db.database import PADatabase
from cheatsheet.generator import cheatsheet_gen
from visualization.mermaid import mermaid_gen
from nightly.adapter import nightly_adapter
from nightly.scheduler import start_scheduler

db = PADatabase()
teacher_agent = None
AGENTSCOPE_AVAILABLE = False


@cl.on_chat_start
async def start():
    """Initialize on chat start"""
    global teacher_agent, AGENTSCOPE_AVAILABLE

    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "02_agents"))
        from agentscope.agents.teacher import TeacherAgent

        teacher_agent = TeacherAgent()
        AGENTSCOPE_AVAILABLE = True
    except ImportError as e:
        print(f"AgentScope import failed: {e}")
        teacher_agent = None
        AGENTSCOPE_AVAILABLE = False

    start_scheduler()

    await cl.Message(
        content="""**PAAM - Full System Ready!**

All systems integrated:
- RAG Knowledge Base (http://localhost:3001)
- Multi-Agent System  
- TTS Voice Output
- Talking Avatar
- SQLite Logging
- Nightly Adaptation

Type /help for available commands.

Note: Agent backend status: """ + ("✅ Available" if AGENTSCOPE_AVAILABLE else "❌ Not available (running in demo mode)"))
    ).send()


@cl.on_message
async def handle_message(message: cl.Message):
    """Handle messages with full integration"""

    global teacher_agent, AGENTSCOPE_AVAILABLE
    user_input = message.content

    if user_input.startswith("/"):
        await handle_command(user_input)
        return

    import time

    start_time = time.time()

    if teacher_agent and AGENTSCOPE_AVAILABLE:
        try:
            response = teacher_agent.chat(user_input)
        except Exception as e:
            response = f"Error: {str(e)}"
    else:
        # Demo mode - simple response
        responses = [
            "That's interesting! Tell me more about what you're learning.",
            "I see! What specific aspect would you like to explore?",
            "Great question! Let's break this down step by step.",
            "I'd love to help you learn! Ask me anything about your study material.",
        ]
        import random
        response = random.choice(responses)

    response_time = int((time.time() - start_time) * 1000)

    session_id = (
        getattr(getattr(teacher_agent, "session", None), "session_id", "default")
        if teacher_agent
        else "default"
    )
    db.log_message(session_id, "user", user_input, response_time)
    db.log_message(session_id, "assistant", response, response_time)

    confusion_signals = ["don't understand", "confused", "don't get it"]
    if any(s in user_input.lower() for s in confusion_signals):
        db.log_confusion(session_id, user_input)
        if teacher_agent and hasattr(teacher_agent, "student"):
            teacher_agent.student.update_profile(confusion=user_input)

    await cl.Message(content=response).send()


async def handle_command(command: str):
    """Handle slash commands"""

    global teacher_agent

    if command == "/cheatsheet":
        topic = "Current Topic"
        cheatsheet = cheatsheet_gen.generate(topic, "Generate from RAG context")
        await cl.Message(content=f"**Cheatsheet**\n\n{cheatsheet}").send()

    elif command == "/diagram":
        diagram = mermaid_gen.generate_from_llm("neural network")
        await cl.Message(content=diagram).send()

    elif command == "/adapt":
        result = nightly_adapter.analyze_and_update()
        await cl.Message(content=f"**Adaptation Complete**\n\n{result}").send()

    elif command == "/stats":
        session_id = (
            getattr(getattr(teacher_agent, "session", None), "session_id", "default")
            if teacher_agent
            else "default"
        )
        stats = db.get_session_stats(session_id)
        await cl.Message(content=f"**Session Stats**\n\n{stats}").send()

    elif command == "/confusion":
        confusion = db.get_all_confusion_concepts()
        await cl.Message(
            content=f"**Weak Concepts**\n\n{', '.join(confusion) or 'None'}"
        ).send()

    elif command == "/help":
        await cl.Message(
            content="""**Commands:**
- /cheatsheet - Generate summary
- /diagram - Generate diagram
- /adapt - Trigger adaptation
- /stats - Session statistics
- /confusion - Show weak concepts
- /help - Show this message"""
        ).send()

    else:
        await cl.Message(
            content="Unknown command. Type /help for available commands."
        ).send()


if __name__ == "__main__":
    import chainlit

    chainlit.run()
