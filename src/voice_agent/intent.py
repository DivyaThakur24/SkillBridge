from __future__ import annotations

from .config import AppConfig
from .llm import OllamaClient
from .models import IntentResult, SUPPORTED_INTENTS


class IntentClassifier:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.ollama = OllamaClient(config)

    def classify(self, transcript: str) -> IntentResult:
        if self.config.llm_mode == "ollama":
            try:
                parsed = self.ollama.classify(transcript)
                return self._normalize(parsed, transcript)
            except Exception:
                pass
        return self._rule_based(transcript)

    def _normalize(self, payload: dict, transcript: str) -> IntentResult:
        intent = str(payload.get("intent", "general_chat")).strip()
        if intent not in SUPPORTED_INTENTS:
            intent = "general_chat"

        confidence = float(payload.get("confidence", 0.5))
        target_path = self._sanitize_path(payload.get("target_path"))
        content = str(payload.get("content", transcript)).strip() or transcript
        summary_source = str(payload.get("summary_source", "")).strip() or None
        rationale = str(payload.get("rationale", "Classified with Ollama.")).strip()
        should_create_parent = bool(payload.get("should_create_parent", False))

        return IntentResult(
            intent=intent,
            confidence=max(0.0, min(1.0, confidence)),
            rationale=rationale,
            target_path=target_path,
            content=content,
            summary_source=summary_source,
            should_create_parent=should_create_parent,
        )

    def _rule_based(self, transcript: str) -> IntentResult:
        lowered = transcript.lower()

        if any(token in lowered for token in ["summarize", "summary", "short summary", "key points"]):
            intent = "summarize_text"
        elif any(token in lowered for token in ["write code", "python file", "script", "function", "class", "implement", "code"]):
            intent = "write_code"
        elif any(token in lowered for token in ["create file", "new file", "create folder", "make a folder", "make directory"]):
            intent = "create_file"
        else:
            intent = "general_chat"

        target_path = self._guess_path(lowered)
        summary_source = transcript.split("summarize", 1)[-1].strip(" :") if intent == "summarize_text" else None

        return IntentResult(
            intent=intent,
            confidence=0.58,
            rationale="Used the built-in fallback classifier because the local LLM was unavailable.",
            target_path=target_path,
            content=transcript,
            summary_source=summary_source,
            should_create_parent="/" in target_path if target_path else False,
        )

    @staticmethod
    def _guess_path(text: str) -> str | None:
        for suffix in [".py", ".txt", ".md", ".json", ".html", ".js"]:
            marker = text.find(suffix)
            if marker != -1:
                start = marker
                while start > 0 and text[start - 1] not in {" ", '"', "'", ":"}:
                    start -= 1
                return text[start : marker + len(suffix)].strip().strip("\"'")
        return None

    @staticmethod
    def _sanitize_path(value: object) -> str | None:
        if value is None:
            return None
        cleaned = str(value).replace("\\", "/").lstrip("/")
        if not cleaned or cleaned.startswith(".."):
            return None
        return cleaned
