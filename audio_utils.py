"""audio_utils.py

Transcription order (to stay within Streamlit Cloud memory limits):
  1. HuggingFace Inference API  — no local RAM, free tier
  2. OpenAI Whisper API          — if OPENAI_API_KEY is set
  3. Local openai-whisper        — only if running locally with enough RAM
"""

import io
import os
import tempfile
from datetime import datetime, timezone
from typing import Optional

import requests
import streamlit as st

try:
    from openai import OpenAI as _OpenAI
    _OPENAI_AVAILABLE = True
except Exception:
    _OPENAI_AVAILABLE = False

try:
    import whisper as _whisper
    _WHISPER_LOCAL = True
except Exception:
    _WHISPER_LOCAL = False

_whisper_cache: dict = {}


def _secret(key: str) -> Optional[str]:
    try:
        return st.secrets.get(key)
    except Exception:
        return None


def _hf_token() -> Optional[str]:
    return os.environ.get("HUGGINGFACE_API_KEY") or _secret("HUGGINGFACE_API_KEY")


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
    """Transcribe audio. Priority order:
    1. HuggingFace Inference API (zero local RAM — preferred on Streamlit Cloud)
    2. OpenAI Whisper API
    3. Local openai-whisper (only viable when running locally)
    """
    if audio_bytes is None:
        return ""

    data = audio_bytes.getvalue() if hasattr(audio_bytes, "getvalue") else audio_bytes

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    transcript = ""
    try:
        # 1. HuggingFace Inference API — no model loaded locally
        token = _hf_token()
        if token:
            try:
                hf_model = f"openai/whisper-{model_name}"
                with open(tmp_path, "rb") as fh:
                    audio_data = fh.read()
                resp = requests.post(
                    f"https://api-inference.huggingface.co/models/{hf_model}",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "audio/webm",
                    },
                    data=audio_data,
                    timeout=120,
                )
                if resp.status_code == 200:
                    body = resp.json()
                    transcript = (body.get("text") or body.get("transcription") or "").strip()
                elif resp.status_code == 503:
                    # Model loading on HF side — retry once after a short wait
                    import time
                    time.sleep(10)
                    resp2 = requests.post(
                        f"https://api-inference.huggingface.co/models/{hf_model}",
                        headers={
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "audio/webm",
                        },
                        data=audio_data,
                        timeout=120,
                    )
                    if resp2.status_code == 200:
                        body = resp2.json()
                        transcript = (body.get("text") or body.get("transcription") or "").strip()
                    else:
                        st.warning(f"HuggingFace API {resp2.status_code}: {resp2.text[:200]}")
                else:
                    st.warning(f"HuggingFace API {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                st.warning(f"HuggingFace-Transkription fehlgeschlagen: {e}")

        # 2. OpenAI Whisper API
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

        # 3. Local Whisper (only works when running locally with enough RAM)
        if not transcript and _WHISPER_LOCAL:
            try:
                if model_name not in _whisper_cache:
                    _whisper_cache[model_name] = _whisper.load_model(model_name)
                result = _whisper_cache[model_name].transcribe(tmp_path, language=language)
                transcript = result.get("text", "").strip()
            except Exception as e:
                st.warning(f"Lokale Whisper-Transkription fehlgeschlagen: {e}")

        if not transcript and not token and not (_OPENAI_AVAILABLE and _secret("OPENAI_API_KEY")):
            st.error(
                "Kein Transkriptions-Backend konfiguriert. "
                "Bitte HUGGINGFACE_API_KEY in den Streamlit Secrets setzen."
            )

    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    return transcript
