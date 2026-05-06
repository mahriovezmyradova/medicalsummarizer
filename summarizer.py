"""summarizer.py

Extractive summarizer using local sentence-transformers (multilingual BERT).
Falls back to HuggingFace Inference API if the local package isn't installed,
then to simple first-N extraction.
"""

import re
import os
import requests
from math import sqrt
from typing import List, Optional

_DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

try:
    from sentence_transformers import SentenceTransformer as _ST
    from sklearn.metrics.pairwise import cosine_similarity as _cosine_sim
    import numpy as np
    _LOCAL_AVAILABLE = True
except Exception:
    _LOCAL_AVAILABLE = False

# Module-level cache so the model loads once per process
_cached_model: Optional[object] = None
_cached_model_name: Optional[str] = None


def _load_local_model(model_name: str):
    global _cached_model, _cached_model_name
    if _cached_model is None or _cached_model_name != model_name:
        _cached_model = _ST(model_name)
        _cached_model_name = model_name
    return _cached_model


def _cosine_simple(u, v):
    dot = sum(a * b for a, b in zip(u, v))
    nu = sqrt(sum(a * a for a in u))
    nv = sqrt(sum(b * b for b in v))
    return dot / (nu * nv) if nu and nv else 0.0


def _hf_embeddings(sentences: List[str], model_name: str) -> Optional[List]:
    token = os.environ.get("HUGGINGFACE_API_KEY")
    if not token:
        try:
            import streamlit as st
            token = st.secrets.get("HUGGINGFACE_API_KEY")
        except Exception:
            pass
    if not token:
        return None
    try:
        resp = requests.post(
            f"https://api-inference.huggingface.co/embeddings/{model_name}",
            headers={"Authorization": f"Bearer {token}"},
            json={"inputs": sentences},
            timeout=60,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        return data.get("embeddings", data) if isinstance(data, dict) else data
    except Exception:
        return None


def _rank_sentences(sentences: List[str], embeddings) -> List[int]:
    """Return sentence indices ranked by centroid similarity (most central first)."""
    if _LOCAL_AVAILABLE and hasattr(embeddings, "shape"):
        sim = _cosine_sim(embeddings)
        scores = sim.sum(axis=1)
        return list(np.argsort(scores)[::-1])
    else:
        n = len(embeddings)
        scores = [
            sum(_cosine_simple(embeddings[i], embeddings[j]) for j in range(n) if i != j)
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

    # 1. Try local sentence-transformers (BERT)
    if _LOCAL_AVAILABLE:
        try:
            model = _load_local_model(model_name)
            embeddings = model.encode(sentences, convert_to_numpy=True)
        except Exception:
            embeddings = None

    # 2. Fall back to HuggingFace Inference API
    if embeddings is None:
        embeddings = _hf_embeddings(sentences, model_name)

    if embeddings is not None:
        try:
            ranked = _rank_sentences(sentences, embeddings)
            selected = sorted(ranked[:top_k])
            return "\n\n".join(sentences[i] for i in selected)
        except Exception:
            pass

    # 3. Simple fallback: first top_k sentences
    return "\n\n".join(sentences[:top_k])
