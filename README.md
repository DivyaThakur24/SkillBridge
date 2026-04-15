# Voice-Controlled Local AI Agent

A local-first AI agent that accepts audio, transcribes it into text, classifies the user's intent, executes safe local tools, and shows the full pipeline in a Streamlit interface.

## Features

- Audio input from:
  - microphone recording in the UI
  - uploaded audio files such as `.wav`, `.mp3`, and `.m4a`
- Speech-to-text with a local Hugging Face Whisper model by default
- Intent understanding with a local Ollama model by default
- Safe tool execution restricted to the repository's `output/` folder
- UI output for:
  - transcribed text
  - detected intent
  - action taken
  - final result

## Supported Intents

- `create_file`
- `write_code`
- `summarize_text`
- `general_chat`

## Architecture

```text
Audio Input
  -> Speech-to-Text
  -> Intent Classifier
  -> Tool Router
  -> Safe Local Execution
  -> Streamlit UI
```

### Speech-to-Text

- Default: `openai/whisper-tiny.en` via Hugging Face `transformers`
- Optional fallback: OpenAI or Groq transcription APIs if local hardware is too limited

### Intent Understanding

- Default: local Ollama model, configured as `llama3.2:3b`
- Fallback: deterministic rule-based classifier if Ollama is unavailable

### Tool Execution

The agent supports:

- creating files and folders
- generating and writing code to a file
- summarizing text
- answering general chat prompts

All writes are constrained to:

```text
output/
```

The app refuses to write outside that directory.

## Project Structure

```text
.
|-- LICENSE
|-- README.md
|-- requirements.txt
|-- output/
`-- src/
    |-- app.py
    `-- voice_agent/
        |-- __init__.py
        |-- agent.py
        |-- config.py
        |-- intent.py
        |-- llm.py
        |-- models.py
        |-- stt.py
        |-- tools.py
        `-- ui.py
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run src/app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Environment Variables

Create a `.env` file if needed:

```env
STT_MODE=local
STT_MODEL_ID=openai/whisper-tiny.en
LLM_MODE=ollama
OLLAMA_MODEL=llama3.2:3b
OLLAMA_URL=http://localhost:11434/api/generate
OPENAI_API_KEY=
GROQ_API_KEY=
```

## Example Flow

Voice input:

```text
Create a Python file with a retry function.
```

Execution:

1. Whisper transcribes the audio.
2. The classifier maps the request to `write_code`.
3. The tool layer generates Python code.
4. The file is written inside `output/`.
5. The UI shows the transcription, intent, action, and result.

## Hardware Workaround

This project is local-first. If your machine cannot run Whisper or an Ollama model smoothly:

- set `STT_MODE=api` and use OpenAI or Groq for transcription
- keep the intent stage on Ollama if available
- rely on the built-in rule-based intent fallback if Ollama is unavailable

If you switch to API STT for a submission, document that hardware limitation clearly in your final demo notes.

## Deliverables Notes

This repository contains the working app code and setup instructions. For the assignment submission, add:

- a 2-3 minute demo video link
- a technical article link on Medium, Dev.to, or Substack

## Suggested Demo Prompts

- `Create a file named notes.txt`
- `Create a Python file with a retry function`
- `Summarize this paragraph about local AI agents`
- `Tell me what this assistant can do`
