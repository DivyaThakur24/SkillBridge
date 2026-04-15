from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from .config import AppConfig
from .intent import IntentClassifier
from .models import ExecutionResult
from .stt import SpeechToTextEngine
from .tools import SafeWorkspaceTools


class VoiceAgent:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.stt = SpeechToTextEngine(config)
        self.intent_classifier = IntentClassifier(config)
        self.tools = SafeWorkspaceTools(config)

    def handle_audio(self, audio_path: Path) -> ExecutionResult:
        transcription = self.stt.transcribe(audio_path)
        intent = self.intent_classifier.classify(transcription)

        if intent.intent == "create_file":
            if intent.target_path and not Path(intent.target_path).suffix:
                action, artifacts = self.tools.create_folder(intent.target_path)
                output = action
            else:
                action, artifacts = self.tools.create_file(intent.target_path)
                output = action
        elif intent.intent == "write_code":
            action, artifacts, output = self.tools.write_code(intent.target_path, intent.content or transcription)
        elif intent.intent == "summarize_text":
            source = intent.summary_source or transcription
            action = "Summarized the supplied text."
            output = self.tools.summarize_text(source)
            artifacts = []
        else:
            action = "Handled the request as general chat."
            output = self.tools.general_chat(transcription)
            artifacts = []

        return ExecutionResult(
            transcription=transcription,
            intent=intent,
            action=action,
            output=output,
            artifacts=artifacts,
        )

    def persist_uploaded_audio(self, filename: str, raw_bytes: bytes) -> Path:
        suffix = Path(filename).suffix or ".wav"
        target = self.config.temp_dir / f"{uuid4().hex}{suffix}"
        target.write_bytes(raw_bytes)
        return target

    def persist_recorded_audio(self, raw_bytes: bytes) -> Path:
        target = self.config.temp_dir / f"{uuid4().hex}.wav"
        target.write_bytes(raw_bytes)
        return target

    def clear_temp(self) -> None:
        if self.config.temp_dir.exists():
            shutil.rmtree(self.config.temp_dir)
        self.config.temp_dir.mkdir(exist_ok=True)
