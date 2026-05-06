"""summarizer.py

Simple extractive summarizer using sentence-transformers (BERT) to embed
sentences and select the top-k most representative sentences.
"""

from typing import List
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    S_EMBED_AVAILABLE = True
except Exception:
    S_EMBED_AVAILABLE = False

try:
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False


def extractive_summary(text: str, top_k: int = 5, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2") -> str:
    """Return an extractive summary composed of the top_k sentences.

    If sentence-transformers isn't available, falls back to returning the
    first N sentences.
    """
    if not text or not text.strip():
        return ""

    # Very simple sentence split by newlines or periods for robustness
    import re
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\\s+|\\n+", text) if s.strip()]

    if len(sentences) <= top_k:
        return "\n\n".join(sentences)

    if S_EMBED_AVAILABLE and SKLEARN_AVAILABLE:
        try:
            model = SentenceTransformer(model_name)
            embeddings = model.encode(sentences, convert_to_numpy=True)
            # Compute pairwise similarity and a simple "centrality" score
            sim = cosine_similarity(embeddings)
            scores = sim.sum(axis=1)
            top_idx = np.argsort(scores)[-top_k:][::-1]
            selected = [sentences[i] for i in sorted(top_idx)]
            return "\n\n".join(selected)
        except Exception:
            # Fallback
            return "\n\n".join(sentences[:top_k])
    else:
        # Fallback simple approach: pick evenly spaced sentences
        idxs = np.linspace(0, len(sentences) - 1, top_k, dtype=int)
        selected = [sentences[i] for i in idxs]
        return "\n\n".join(selected)
