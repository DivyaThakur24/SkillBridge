from __future__ import annotations

import re
from pathlib import Path

from .config import AppConfig


class SafeWorkspaceTools:
    def __init__(self, config: AppConfig) -> None:
        self.output_dir = config.output_dir.resolve()
        self.output_dir.mkdir(exist_ok=True)

    def _resolve(self, requested_path: str | None, default_name: str) -> Path:
        candidate = (requested_path or default_name).replace("\\", "/").lstrip("/")
        resolved = (self.output_dir / candidate).resolve()
        if resolved != self.output_dir and self.output_dir not in resolved.parents:
            raise ValueError("Refusing to write outside the output directory.")
        return resolved

    def create_file(self, requested_path: str | None, initial_text: str = "") -> tuple[str, list[str]]:
        path = self._resolve(requested_path, "new_file.txt")
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(initial_text, encoding="utf-8")
            return f"Created file at {path}.", [str(path)]
        return f"File already exists at {path}.", [str(path)]

    def create_folder(self, requested_path: str | None) -> tuple[str, list[str]]:
        path = self._resolve(requested_path, "new_folder")
        path.mkdir(parents=True, exist_ok=True)
        return f"Created folder at {path}.", [str(path)]

    def write_code(self, requested_path: str | None, instruction: str) -> tuple[str, list[str], str]:
        path = self._resolve(requested_path, "generated_script.py")
        path.parent.mkdir(parents=True, exist_ok=True)
        code = self._generate_code(instruction, path.suffix)
        path.write_text(code, encoding="utf-8")
        return f"Wrote generated code to {path}.", [str(path)], code

    def summarize_text(self, text: str) -> str:
        cleaned = " ".join(text.split())
        if not cleaned:
            return "No text was supplied to summarize."
        sentences = re.split(r"(?<=[.!?])\s+", cleaned)
        if len(sentences) == 1:
            return sentences[0][:280]
        return " ".join(sentences[:2]).strip()

    def general_chat(self, text: str) -> str:
        return (
            "This is a general chat request. "
            "I can create files, generate code into files, summarize text, and respond conversationally. "
            f"Your message was: {text}"
        )

    @staticmethod
    def _generate_code(instruction: str, suffix: str) -> str:
        lowered = instruction.lower()

        if suffix == ".html":
            return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Generated Page</title>
</head>
<body>
  <main>
    <h1>Generated from the Voice Agent</h1>
    <p>This file was created from a voice instruction.</p>
  </main>
</body>
</html>
"""

        if "retry" in lowered:
            return '''import time


def retry(operation, attempts=3, delay_seconds=1):
    """Retry a callable until it succeeds or attempts are exhausted."""
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == attempts:
                break
            time.sleep(delay_seconds)
    raise last_error
'''

        if "fastapi" in lowered:
            return '''from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello from the generated FastAPI app"}
'''

        if suffix == ".js":
            return '''function main() {
  console.log("Generated from the voice-controlled local AI agent.");
}

main();
'''

        return f'''def main():
    """Generated from a voice instruction."""
    print("Instruction: {instruction}")


if __name__ == "__main__":
    main()
'''
