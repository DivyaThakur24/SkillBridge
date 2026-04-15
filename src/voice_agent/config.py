from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "output"
TEMP_DIR = REPO_ROOT / "temp"

OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)


@dataclass(slots=True)
class AppConfig:
    stt_mode: str = os.getenv("STT_MODE", "local")
    stt_model_id: str = os.getenv("STT_MODEL_ID", "openai/whisper-tiny.en")
    llm_mode: str = os.getenv("LLM_MODE", "ollama")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    output_dir: Path = OUTPUT_DIR
    temp_dir: Path = TEMP_DIR


def get_config() -> AppConfig:
    return AppConfig()
