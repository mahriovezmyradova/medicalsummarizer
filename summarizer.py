"""summarizer.py

Extractive summarization priority order (to stay within Streamlit Cloud memory limits):
  1. HuggingFace Inference API  — no local RAM, free tier
  2. Local sentence-transformers — only when running locally
  3. First-N fallback            — if no backend is available
"""

import re
import os
import math
import requests
from typing import List, Optional

_DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

try:
    from sentence_transformers import SentenceTransformer as _ST
    from sklearn.metrics.pairwise import cosine_similarity as _cosine_sim
    import numpy as np
    _LOCAL_AVAILABLE = True
except Exception:
    _LOCAL_AVAILABLE = False

_cached_model: Optional[object] = None
_cached_model_name: Optional[str] = None


def _hf_token() -> Optional[str]:
    val = os.environ.get("HUGGINGFACE_API_KEY")
    if not val:
        try:
            import streamlit as st
            val = st.secrets.get("HUGGINGFACE_API_KEY")
        except Exception:
            pass
    return val


def _hf_embeddings(sentences: List[str], model_name: str) -> Optional[List]:
    """Call HF feature-extraction pipeline. Returns list of float vectors or None."""
    token = _hf_token()
    if not token:
        return None
    try:
        resp = requests.post(
            f"https://api-inference.huggingface.co/models/{model_name}",
            headers={"Authorization": f"Bearer {token}"},
            json={"inputs": sentences, "options": {"wait_for_model": True}},
            timeout=60,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        # Response is a list of embedding vectors
        if isinstance(data, list) and data and isinstance(data[0], list):
            return data
        return None
    except Exception:
        return None


def _load_local_model(model_name: str):
    global _cached_model, _cached_model_name
    if _cached_model is None or _cached_model_name != model_name:
        _cached_model = _ST(model_name)
        _cached_model_name = model_name
    return _cached_model


def _cosine(u, v) -> float:
    dot = sum(a * b for a, b in zip(u, v))
    nu = math.sqrt(sum(a * a for a in u))
    nv = math.sqrt(sum(b * b for b in v))
    return dot / (nu * nv) if nu and nv else 0.0


def _rank(embeddings) -> List[int]:
    """Return sentence indices sorted by centroid score, most central first."""
    if _LOCAL_AVAILABLE and hasattr(embeddings, "shape"):
        sim = _cosine_sim(embeddings)
        scores = sim.sum(axis=1)
        return list(np.argsort(scores)[::-1])
    n = len(embeddings)
    scores = [
        sum(_cosine(embeddings[i], embeddings[j]) for j in range(n) if i != j)
        for i in range(n)
    ]
    return sorted(range(n), key=lambda i: scores[i], reverse=True)


def _split_sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def extractive_summary(text: str, top_k: int = 5, model_name: str = _DEFAULT_MODEL) -> str:
    """Return an extractive summary of the top_k most central sentences."""
    if not text or not text.strip():
        return ""

    sentences = _split_sentences(text)
    if len(sentences) <= top_k:
        return "\n\n".join(sentences)

    embeddings = None

    # 1. HuggingFace Inference API (zero local RAM)
    embeddings = _hf_embeddings(sentences, model_name)

    # 2. Local sentence-transformers (only viable locally)
    if embeddings is None and _LOCAL_AVAILABLE:
        try:
            model = _load_local_model(model_name)
            embeddings = model.encode(sentences, convert_to_numpy=True)
        except Exception:
            embeddings = None

    if embeddings is not None:
        try:
            ranked = _rank(embeddings)
            selected = sorted(ranked[:top_k])
            return "\n\n".join(sentences[i] for i in selected)
        except Exception:
            pass

    # 3. Fallback: first top_k sentences
    return "\n\n".join(sentences[:top_k])
