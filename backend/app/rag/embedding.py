from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)

_model = None
_fallback_mode = False

EMBEDDING_DIMENSION = 384


def _load_model():
    global _model, _fallback_mode
    if _model is not None or _fallback_mode:
        return
    try:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("sentence-transformers model loaded: all-MiniLM-L6-v2")
    except Exception as exc:
        logger.warning("Failed to load sentence-transformers model, falling back to keyword mode: %s", exc)
        _fallback_mode = True


def generate_embedding(text: str) -> list[float]:
    _load_model()
    if _fallback_mode or not text.strip():
        return [0.0] * EMBEDDING_DIMENSION
    vector = _model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    _load_model()
    if _fallback_mode:
        return [[0.0] * EMBEDDING_DIMENSION for _ in texts]
    valid_texts = [t if t.strip() else " " for t in texts]
    vectors = _model.encode(valid_texts, normalize_embeddings=True)
    return [v.tolist() for v in vectors]


def is_fallback_mode() -> bool:
    _load_model()
    return _fallback_mode
