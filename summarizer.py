"""summarizer.py

Extractive summarization priority order:
  1. HuggingFace Inference API  — no local RAM, free tier (Streamlit Cloud)
  2. Local sentence-transformers — lazy-imported only if HF API unavailable
  3. First-N fallback            — if neither backend is available

Heavy imports (sentence_transformers, sklearn, torch) are deferred to inside
the function so they never load at module import time. This prevents the
`transformers` package from flooding Streamlit's file watcher with torchvision
errors even when sentence-transformers is present in the environment.
"""

import re
import os
import math
import requests
from typing import List, Optional

_DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Module-level cache — populated lazily on first local-model use
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
        if isinstance(data, list) and data and isinstance(data[0], list):
            return data
        return None
    except Exception:
        return None


def _load_local_model(model_name: str):
    global _cached_model, _cached_model_name
    # Lazy import — only triggers if we actually reach this code path
    from sentence_transformers import SentenceTransformer as _ST  # noqa: PLC0415
    if _cached_model is None or _cached_model_name != model_name:
        _cached_model = _ST(model_name)
        _cached_model_name = model_name
    return _cached_model


def _cosine(u, v) -> float:
    dot = sum(a * b for a, b in zip(u, v))
    nu = math.sqrt(sum(a * a for a in u))
    nv = math.sqrt(sum(b * b for b in v))
    return dot / (nu * nv) if nu and nv else 0.0


def _rank_hf(embeddings: List) -> List[int]:
    """Rank using pure-Python cosine (for list-of-list embeddings from HF API)."""
    n = len(embeddings)
    scores = [
        sum(_cosine(embeddings[i], embeddings[j]) for j in range(n) if i != j)
        for i in range(n)
    ]
    return sorted(range(n), key=lambda i: scores[i], reverse=True)


def _rank_local(embeddings) -> List[int]:
    """Rank using numpy/sklearn cosine (for numpy arrays from sentence-transformers)."""
    from sklearn.metrics.pairwise import cosine_similarity  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415
    sim = cosine_similarity(embeddings)
    scores = sim.sum(axis=1)
    return list(np.argsort(scores)[::-1])


def _split_sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def extractive_summary(text: str, top_k: int = 5, model_name: str = _DEFAULT_MODEL) -> str:
    """Return an extractive summary of the top_k most central sentences."""
    if not text or not text.strip():
        return ""

    sentences = _split_sentences(text)
    if len(sentences) <= top_k:
        return "\n\n".join(sentences)

    # 1. HuggingFace Inference API (zero local RAM — preferred on Streamlit Cloud)
    hf_emb = _hf_embeddings(sentences, model_name)
    if hf_emb is not None:
        try:
            ranked = _rank_hf(hf_emb)
            return "\n\n".join(sentences[i] for i in sorted(ranked[:top_k]))
        except Exception:
            pass

    # 2. Local sentence-transformers (lazy import — only if HF API unavailable)
    try:
        model = _load_local_model(model_name)
        local_emb = model.encode(sentences, convert_to_numpy=True)
        ranked = _rank_local(local_emb)
        return "\n\n".join(sentences[i] for i in sorted(ranked[:top_k]))
    except Exception:
        pass

    # 3. Fallback: first top_k sentences
    return "\n\n".join(sentences[:top_k])
