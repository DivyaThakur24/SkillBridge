from __future__ import annotations

from pathlib import Path

import requests
from transformers import pipeline

from .config import AppConfig


class SpeechToTextEngine:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._pipeline = None

    def _get_pipeline(self):
        if self._pipeline is None:
            self._pipeline = pipeline(
                task="automatic-speech-recognition",
                model=self.config.stt_model_id,
            )
        return self._pipeline

    def transcribe(self, audio_path: Path) -> str:
        if self.config.stt_mode == "api":
            return self._transcribe_with_api(audio_path)
        return self._transcribe_locally(audio_path)

    def _transcribe_locally(self, audio_path: Path) -> str:
        result = self._get_pipeline()(str(audio_path))
        if isinstance(result, dict):
            return str(result.get("text", "")).strip()
        return str(result).strip()

    def _transcribe_with_api(self, audio_path: Path) -> str:
        if self.config.openai_api_key:
            return self._call_openai(audio_path)
        if self.config.groq_api_key:
            return self._call_groq(audio_path)
        raise RuntimeError(
            "STT_MODE=api was selected, but no OPENAI_API_KEY or GROQ_API_KEY was provided."
        )

    def _call_openai(self, audio_path: Path) -> str:
        with audio_path.open("rb") as audio_file:
            response = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {self.config.openai_api_key}"},
                files={"file": (audio_path.name, audio_file, "audio/wav")},
                data={"model": "gpt-4o-mini-transcribe"},
                timeout=120,
            )
        response.raise_for_status()
        return response.json()["text"].strip()

    def _call_groq(self, audio_path: Path) -> str:
        with audio_path.open("rb") as audio_file:
            response = requests.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {self.config.groq_api_key}"},
                files={"file": (audio_path.name, audio_file, "audio/wav")},
                data={"model": "whisper-large-v3-turbo"},
                timeout=120,
            )
        response.raise_for_status()
        return response.json()["text"].strip()
