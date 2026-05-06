"""audio_utils

Utilities for handling audio: saving uploaded audio to disk and transcribing
locally using a Whisper model when available. Falls back to OpenAI API if the
local whisper package is not installed but an OpenAI key is configured.
"""

import io
import os
import tempfile
from typing import Optional
import streamlit as st

try:
    # Local whisper (OpenAI's whisper implementation) - uses PyTorch
    import whisper
    WHISPER_LOCAL = True
except Exception:
    WHISPER_LOCAL = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False


def save_audio_file(audio_bytes, dest_dir: str = "data/audio", filename: Optional[str] = None) -> str:
    """Save an uploaded audio-like object to disk and return the path.

    audio_bytes is expected to be a BytesIO-like object (has getvalue()).
    """
    os.makedirs(dest_dir, exist_ok=True)

    if filename is None:
        from datetime import datetime
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        filename = f"recording_{ts}.webm"

    path = os.path.join(dest_dir, filename)
    data = audio_bytes.getvalue() if hasattr(audio_bytes, "getvalue") else audio_bytes
    with open(path, "wb") as f:
        f.write(data)

    return path


def transcribe_with_whisper(audio_bytes, model_name: str = "small", language: Optional[str] = "de") -> str:
    """Transcribe audio using a local Whisper model if available, otherwise
    attempt the OpenAI audio transcription API. Returns a plain transcript
    (string).
    """
    if audio_bytes is None:
        return ""

    # Save to a temp file for the model to read
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        data = audio_bytes.getvalue() if hasattr(audio_bytes, "getvalue") else audio_bytes
        tmp.write(data)
        tmp_path = tmp.name

    transcript_text = ""
    try:
        if WHISPER_LOCAL:
            try:
                model = whisper.load_model(model_name)
                # whisper returns a dict with 'text'
                result = model.transcribe(tmp_path, language=language)
                transcript_text = result.get("text", "")
            except Exception as e:
                st.warning(f"Lokale Whisper-Transkription fehlgeschlagen: {e}")
                transcript_text = ""

        # If local not available or failed, try OpenAI API if configured
        if (not transcript_text) and OPENAI_AVAILABLE:
            try:
                api_key = st.secrets.get("OPENAI_API_KEY", None)
                if api_key:
                    client = OpenAI(api_key=api_key)
                    with open(tmp_path, "rb") as fh:
                        # name attribute helps some clients decide format
                        file_bytes = io.BytesIO(fh.read())
                        file_bytes.name = os.path.basename(tmp_path)
                        transcript = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=file_bytes,
                            language=language
                        )
                        transcript_text = transcript.text
            except Exception as e:
                st.warning(f"OpenAI-Transkription fehlgeschlagen: {e}")

    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    if not transcript_text:
        # fallback short message
        return ""

    return transcript_text

