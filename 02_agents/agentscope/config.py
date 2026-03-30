import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    ANYTHINGLLM_URL = os.getenv("ANYTHINGLLM_URL", "http://localhost:3001")
    ANYTHINGLLM_API_KEY = os.getenv("ANYTHINGLLM_API_KEY", "")

    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:70b")

    MAX_TOKENS = 300
    TEMPERATURE = 0.7

    DEFAULT_WORKSPACE = "paam_workspace"

    PROFILE_DIR = os.getenv("PROFILE_DIR", "./data/profiles")
