"""audio_utils.py

Utilities for saving audio and transcribing with Whisper small (local).
Falls back to HuggingFace Inference API, then OpenAI API if local model
isn't installed.
"""

import io
import os
import tempfile
from datetime import datetime, timezone
from typing import Optional

import requests
import streamlit as st

try:
    import whisper as _whisper
    _WHISPER_LOCAL = True
except Exception:
    _WHISPER_LOCAL = False

try:
    from openai import OpenAI as _OpenAI
    _OPENAI_AVAILABLE = True
except Exception:
    _OPENAI_AVAILABLE = False

# Module-level cache keyed by model name
_whisper_cache: dict = {}


def _load_whisper(model_name: str):
    if model_name not in _whisper_cache:
        _whisper_cache[model_name] = _whisper.load_model(model_name)
    return _whisper_cache[model_name]


def save_audio_file(audio_bytes, dest_dir: str = "data/audio", filename: Optional[str] = None) -> str:
    """Save uploaded audio to disk and return the path."""
    os.makedirs(dest_dir, exist_ok=True)
    if filename is None:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        filename = f"recording_{ts}.webm"
    path = os.path.join(dest_dir, filename)
    data = audio_bytes.getvalue() if hasattr(audio_bytes, "getvalue") else audio_bytes
    with open(path, "wb") as f:
        f.write(data)
    return path


def transcribe_with_whisper(audio_bytes, model_name: str = "small", language: Optional[str] = "de") -> str:
    """Transcribe audio. Tries in order:
    1. Local Whisper model (openai-whisper package)
    2. HuggingFace Inference API
    3. OpenAI Whisper API
    Returns plain transcript string.
    """
    if audio_bytes is None:
        return ""

    data = audio_bytes.getvalue() if hasattr(audio_bytes, "getvalue") else audio_bytes

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    transcript = ""
    try:
        # 1. Local Whisper
        if _WHISPER_LOCAL:
            try:
                model = _load_whisper(model_name)
                result = model.transcribe(tmp_path, language=language)
                transcript = result.get("text", "").strip()
            except Exception as e:
                st.warning(f"Lokale Whisper-Transkription fehlgeschlagen: {e}")

        # 2. HuggingFace Inference API
        if not transcript:
            hf_token = os.environ.get("HUGGINGFACE_API_KEY") or _secret("HUGGINGFACE_API_KEY")
            if hf_token:
                try:
                    hf_model = f"openai/whisper-{model_name}"
                    headers = {"Authorization": f"Bearer {hf_token}"}
                    with open(tmp_path, "rb") as fh:
                        resp = requests.post(
                            f"https://api-inference.huggingface.co/models/{hf_model}",
                            headers=headers,
                            data=fh.read(),
                            timeout=120,
                        )
                    if resp.status_code == 200:
                        body = resp.json()
                        transcript = (body.get("text") or body.get("transcription") or "").strip()
                    else:
                        st.warning(f"HuggingFace API {resp.status_code}: {resp.text[:200]}")
                except Exception as e:
                    st.warning(f"HuggingFace-Transkription fehlgeschlagen: {e}")

        # 3. OpenAI Whisper API
        if not transcript and _OPENAI_AVAILABLE:
            api_key = _secret("OPENAI_API_KEY")
            if api_key:
                try:
                    client = _OpenAI(api_key=api_key)
                    with open(tmp_path, "rb") as fh:
                        buf = io.BytesIO(fh.read())
                        buf.name = os.path.basename(tmp_path)
                        result = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=buf,
                            language=language,
                        )
                        transcript = result.text.strip()
                except Exception as e:
                    st.warning(f"OpenAI-Transkription fehlgeschlagen: {e}")
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    return transcript


def _secret(key: str) -> Optional[str]:
    try:
        return st.secrets.get(key)
    except Exception:
        return None
