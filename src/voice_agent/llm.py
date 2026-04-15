from __future__ import annotations

import json
from textwrap import dedent

import requests

from .config import AppConfig


INTENT_PROMPT = dedent(
    """
    You are an intent classifier for a local voice-controlled desktop AI agent.
    Read the transcription and return strict JSON with the keys:
    - intent: one of create_file, write_code, summarize_text, general_chat
    - confidence: number from 0 to 1
    - rationale: short explanation
    - target_path: optional relative path under output/
    - content: optional extracted content or instruction details
    - summary_source: optional text that should be summarized
    - should_create_parent: boolean

    Transcription:
    {transcript}
    """
).strip()


class OllamaClient:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def classify(self, transcript: str) -> dict:
        response = requests.post(
            self.config.ollama_url,
            json={
                "model": self.config.ollama_model,
                "prompt": INTENT_PROMPT.format(transcript=transcript),
                "stream": False,
                "format": "json",
            },
            timeout=120,
        )
        response.raise_for_status()
        payload = response.json()
        return json.loads(payload["response"])
