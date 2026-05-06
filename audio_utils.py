"""audio_utils.py

Transcription order (to stay within Streamlit Cloud memory limits):
  1. HuggingFace Inference API  — no local RAM, free tier
  2. OpenAI Whisper API          — if OPENAI_API_KEY is set
  3. Local openai-whisper        — only if running locally with enough RAM

Returns (transcript_text, error_message_or_None).
"""

import io
import os
import time
import tempfile
from datetime import datetime, timezone
from typing import Optional, Tuple

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

_HF_RETRIES = 4
_HF_RETRY_DELAYS = [15, 25, 35, 45]   # seconds between retries on 503/429
_HF_TIMEOUT = 180                       # seconds — covers ~3 min recordings


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


def _hf_transcribe(audio_data: bytes, model_name: str, token: str) -> Tuple[str, Optional[str]]:
    """Call HF Inference API for Whisper with retry logic.
    Returns (transcript, error_message_or_None).
    """
    url = f"https://api-inference.huggingface.co/models/openai/whisper-{model_name}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "audio/webm",
    }

    last_error: Optional[str] = None
    for attempt in range(_HF_RETRIES):
        try:
            resp = requests.post(url, headers=headers, data=audio_data, timeout=_HF_TIMEOUT)

            if resp.status_code == 200:
                body = resp.json()
                text = (body.get("text") or body.get("transcription") or "").strip()
                return text, None

            if resp.status_code in (503, 429):
                # Model loading or rate limit — wait and retry
                delay = _HF_RETRY_DELAYS[min(attempt, len(_HF_RETRY_DELAYS) - 1)]
                last_error = f"HF API {resp.status_code} (Versuch {attempt + 1}/{_HF_RETRIES})"
                if attempt < _HF_RETRIES - 1:
                    time.sleep(delay)
                continue

            # Any other error — no point retrying
            try:
                body = resp.json()
                detail = body.get("error", resp.text[:200])
            except Exception:
                detail = resp.text[:200]
            return "", f"HF API Fehler {resp.status_code}: {detail}"

        except requests.Timeout:
            last_error = f"HF API Timeout nach {_HF_TIMEOUT}s (Versuch {attempt + 1}/{_HF_RETRIES})"
            if attempt < _HF_RETRIES - 1:
                time.sleep(10)
            continue
        except Exception as exc:
            return "", f"HF API Verbindungsfehler: {exc}"

    return "", last_error or "HF API: Alle Versuche fehlgeschlagen"


def transcribe_with_whisper(
    audio_bytes, model_name: str = "small", language: Optional[str] = "de"
) -> Tuple[str, Optional[str]]:
    """Transcribe audio. Returns (transcript, error_or_None).

    Priority:
    1. HuggingFace Inference API (zero local RAM)
    2. OpenAI Whisper API
    3. Local openai-whisper (only viable locally)
    """
    if audio_bytes is None:
        return "", None

    raw = audio_bytes.getvalue() if hasattr(audio_bytes, "getvalue") else audio_bytes

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(raw)
        tmp_path = tmp.name

    transcript = ""
    error: Optional[str] = None
    errors = []

    try:
        # 1. HuggingFace Inference API
        token = _hf_token()
        if token:
            with open(tmp_path, "rb") as fh:
                audio_data = fh.read()
            transcript, hf_err = _hf_transcribe(audio_data, model_name, token)
            if hf_err:
                errors.append(hf_err)

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
                            model="whisper-1", file=buf, language=language
                        )
                        transcript = result.text.strip()
                except Exception as exc:
                    errors.append(f"OpenAI API: {exc}")

        # 3. Local Whisper
        if not transcript and _WHISPER_LOCAL:
            try:
                if model_name not in _whisper_cache:
                    _whisper_cache[model_name] = _whisper.load_model(model_name)
                result = _whisper_cache[model_name].transcribe(tmp_path, language=language)
                transcript = result.get("text", "").strip()
            except Exception as exc:
                errors.append(f"Lokales Whisper: {exc}")

        if not transcript:
            if not token and not (_OPENAI_AVAILABLE and _secret("OPENAI_API_KEY")):
                error = (
                    "Kein Transkriptions-Backend konfiguriert. "
                    "HUGGINGFACE_API_KEY in Streamlit Secrets setzen."
                )
            else:
                error = " | ".join(errors) if errors else "Transkription leer — Audio zu kurz oder API-Fehler"

    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    return transcript, error
