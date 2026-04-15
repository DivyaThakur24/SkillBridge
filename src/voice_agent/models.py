from __future__ import annotations

from dataclasses import dataclass, field


SUPPORTED_INTENTS = {
    "create_file",
    "write_code",
    "summarize_text",
    "general_chat",
}


@dataclass(slots=True)
class IntentResult:
    intent: str
    confidence: float
    rationale: str
    target_path: str | None = None
    content: str | None = None
    summary_source: str | None = None
    should_create_parent: bool = False


@dataclass(slots=True)
class ExecutionResult:
    transcription: str
    intent: IntentResult
    action: str
    output: str
    artifacts: list[str] = field(default_factory=list)
