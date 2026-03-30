import gradio as gr
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / "02_agents"))
try:
    from agentscope.agents.teacher import TeacherAgent

    AGENTSCOPE_AVAILABLE = True
except ImportError:
    AGENTSCOPE_AVAILABLE = False
    TeacherAgent = None

sys.path.append(str(Path(__file__).parent.parent / "tts"))
try:
    from elevenlabs import ElevenLabsTTS

    tts_engine = ElevenLabsTTS()
    TTS_AVAILABLE = True
except ImportError:
    tts_engine = None
    TTS_AVAILABLE = False

ANYTHINGLLM_URL = os.getenv("ANYTHINGLLM_URL", "http://localhost:3001")
TEACHER = None

welcome = """👋 Welcome to PAAM - Your Personal Adaptive AI Mentor!

I can help you learn from any uploaded material. Here's what I can do:

📚 **Chat** - Ask me anything about your study material
🎯 **Quiz** - Test your understanding 
📝 **Cheatsheet** - Get a quick summary
🔊 **Voice** - Enable TTS for voice responses
🧠 **Adaptive** - I learn your learning style over time

What would you like to learn about today?"""


def chat(message, history, voice_enabled):
    global TEACHER

    if TEACHER is None and AGENTSCOPE_AVAILABLE:
        TEACHER = TeacherAgent()

    if not AGENTSCOPE_AVAILABLE:
        response = f"Demo mode: You said '{message}'. Agent backend not available."
        return response, None

    response = TEACHER.chat(message)
    return response, None


def generate_voice(text):
    if not TTS_AVAILABLE or not tts_engine:
        return None
    try:
        audio_path = tts_engine.speak(text)
        return audio_path
    except Exception as e:
        print(f"TTS Error: {e}")
        return None


def toggle_voice(enabled):
    return enabled


with gr.Blocks(title="PAAM - AI Mentor") as demo:
    gr.Markdown("# 🎓 PAAM - Personal Adaptive AI Mentor")
    gr.Markdown(welcome)

    with gr.Row():
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(
                height=500,
                avatar_images=(
                    "https://api.dicebear.com/7.x/bottts/svg?seed=PAAM",
                    "https://api.dicebear.com/7.x/avataaars/svg?seed=Student",
                ),
            )
            msg = gr.Textbox(
                label="Your message",
                placeholder="Ask me anything about your study material...",
                lines=2,
            )
            with gr.Row():
                submit_btn = gr.Button("Send", variant="primary")
                clear_btn = gr.Button("Clear")

        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ Settings")
            voice_toggle = gr.Checkbox(label="Enable Voice (TTS)", value=False)
            voice_test_btn = gr.Button("Test Voice")
            voice_output = gr.Audio(label="Voice Output", visible=True)

            gr.Markdown("### 📊 Stats")
            style_btn = gr.Button("Show Learning Style")
            mastery_btn = gr.Button("Show Mastery Rate")

            gr.Markdown("### 🎯 Actions")
            quiz_btn = gr.Button("Start Quiz")
            cheatsheet_btn = gr.Button("Generate Cheatsheet")

    def respond(message, history, voice_enabled):
        global TEACHER

        if TEACHER is None and AGENTSCOPE_AVAILABLE:
            TEACHER = TeacherAgent()

        if not AGENTSCOPE_AVAILABLE:
            response = f"Demo mode: You said '{message}'. Agent backend not available."
        else:
            response = TEACHER.chat(message)

        history.append((message, response))

        audio_file = None
        if voice_enabled and TTS_AVAILABLE:
            try:
                audio_file = tts_engine.speak(response)
            except Exception as e:
                print(f"TTS Error: {e}")

        return "", history, audio_file

    submit_btn.click(
        respond,
        inputs=[msg, chatbot, voice_toggle],
        outputs=[msg, chatbot, voice_output],
    )

    msg.submit(
        respond,
        inputs=[msg, chatbot, voice_toggle],
        outputs=[msg, chatbot, voice_output],
    )

    def clear_chat():
        return [], None

    clear_btn.click(clear_chat, outputs=[chatbot, voice_output])

    def test_voice():
        if TTS_AVAILABLE:
            return tts_engine.speak(
                "Hello! This is a test of the text to speech system."
            )
        return None

    voice_test_btn.click(test_voice, outputs=voice_output)

    def show_style():
        if TEACHER:
            return f"🎨 Your current learning style: **{TEACHER.student.get_style()}**"
        return "Agent not available"

    style_btn.click(show_style, outputs=msg)

    def show_mastery():
        if TEACHER:
            return f"📊 Your mastery rate: **{TEACHER.student.get_mastery_rate():.1%}**"
        return "Agent not available"

    mastery_btn.click(show_mastery, outputs=msg)

    def start_quiz():
        return "Quiz feature coming soon!"

    quiz_btn.click(start_quiz, outputs=msg)

    def generate_cheatsheet():
        return "Cheatsheet feature coming soon!"

    cheatsheet_btn.click(generate_cheatsheet, outputs=msg)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft())
