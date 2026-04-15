from __future__ import annotations

from pathlib import Path

import streamlit as st
from streamlit_mic_recorder import mic_recorder

from .agent import VoiceAgent
from .config import get_config


def render_result(result) -> None:
    st.subheader("Pipeline Result")
    st.text_area("Transcribed text", value=result.transcription, height=120)
    st.text_input("Detected intent", value=result.intent.intent)
    st.caption(
        f"Confidence: {result.intent.confidence:.2f} | Reasoning: {result.intent.rationale}"
    )
    st.text_area("Action taken", value=result.action, height=90)
    st.text_area("Final output", value=result.output, height=180)
    if result.artifacts:
        st.write("Artifacts")
        for artifact in result.artifacts:
            st.code(artifact)


def main() -> None:
    st.set_page_config(
        page_title="Voice-Controlled Local AI Agent",
        page_icon="🎙️",
        layout="wide",
    )

    st.title("Voice-Controlled Local AI Agent")
    st.write(
        "Record from your microphone or upload an audio file, then inspect the complete transcription, intent classification, action, and result pipeline."
    )

    config = get_config()
    agent = VoiceAgent(config)

    with st.sidebar:
        st.header("Runtime")
        st.write(f"STT mode: `{config.stt_mode}`")
        st.write(f"STT model: `{config.stt_model_id}`")
        st.write(f"LLM mode: `{config.llm_mode}`")
        st.write(f"Ollama model: `{config.ollama_model}`")
        if st.button("Clear temporary audio"):
            agent.clear_temp()
            st.success("Temporary audio files deleted.")

    uploaded = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a"])
    recorded = mic_recorder(
        start_prompt="Start recording",
        stop_prompt="Stop recording",
        just_once=True,
        key="voice-recorder",
    )

    audio_path: Path | None = None
    preview_bytes: bytes | None = None

    if uploaded is not None:
        preview_bytes = uploaded.getvalue()
        audio_path = agent.persist_uploaded_audio(uploaded.name, preview_bytes)
        st.audio(preview_bytes)
    elif recorded and recorded.get("bytes"):
        preview_bytes = recorded["bytes"]
        audio_path = agent.persist_recorded_audio(preview_bytes)
        st.audio(preview_bytes, format="audio/wav")

    if st.button("Run agent", type="primary", disabled=audio_path is None):
        with st.spinner("Running the voice agent pipeline..."):
            result = agent.handle_audio(audio_path)
        render_result(result)

    with st.expander("Supported intents"):
        st.write("- Create a file or folder")
        st.write("- Write code into a file")
        st.write("- Summarize text")
        st.write("- General chat")
