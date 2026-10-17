"""
Dense semantic embeddings used by the deduplication stage.

Two interchangeable backends, selected with EMBEDDING_BACKEND:

  api (default)  NVIDIA NIM hosted embeddings, default model
                 nvidia/nemotron-3-embed-1b (2048-d). Runs off-process, so
                 torch / transformers / sentence-transformers are never
                 imported by the application.
  local_minilm   sentence-transformers all-MiniLM-L6-v2 (384-d). Offline
                 development path; needs the optional sentence-transformers
                 install, which is deliberately absent from requirements.txt.

get_embedding() never raises. When the configured backend is unavailable it
returns None and dedup degrades to "treat as a new challenge" rather than
failing a citizen submission.

Vector identity is exposed through embedding_tag() and persisted next to every
vector, because vectors from different models are not comparable and a silent
mix would corrupt similarity scores.
"""

import logging
import os

from pipeline import nvidia_embed

logger = logging.getLogger(__name__)

LOCAL_MODEL = "all-MiniLM-L6-v2"

# Dimensions belong to the model, so they are derived here instead of being read
# from a free-floating env var that could silently drift from reality.
_MODEL_DIMENSIONS = {
    "nvidia/nemotron-3-embed-1b": 2048,
    "nvidia/llama-nemotron-embed-1b-v2": 2048,
    "nvidia/llama-3.2-nv-embedqa-1b-v2": 2048,
    "nvidia/nv-embedqa-e5-v5": 1024,
    LOCAL_MODEL: 384,
}

EMBEDDING_BACKEND = (os.getenv("EMBEDDING_BACKEND") or "api").strip().lower()

if EMBEDDING_BACKEND == "local_minilm":
    EMBEDDING_MODEL = LOCAL_MODEL
else:
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL") or nvidia_embed.default_model()

EMBEDDING_DIM = _MODEL_DIMENSIONS.get(
    EMBEDDING_MODEL, 384 if EMBEDDING_BACKEND == "local_minilm" else 2048
)

_embedder = None


def embedding_tag() -> str:
    """Identity of the vectors this process produces (model + dimension)."""
    return f"{EMBEDDING_MODEL}:{EMBEDDING_DIM}"


def load_embedder():
    """Warm the local model. No-op for the api backend, which has nothing to load."""
    if EMBEDDING_BACKEND != "local_minilm":
        return

    global _embedder
    if _embedder is None:
        print("[embeddings] Loading sentence-transformers model...")
        # Imported inside the function so the api backend never pulls torch in.
        from sentence_transformers import SentenceTransformer

        _embedder = SentenceTransformer(LOCAL_MODEL)
        print("[embeddings] Model loaded.")


def _embed_local(text: str):
    try:
        load_embedder()
    except Exception as exc:  # ImportError when the optional extra is not installed
        logger.warning("[embeddings] local model unavailable: %s", exc)
        return None

    if _embedder is None:
        return None
    return _embedder.encode(text).tolist()


def _embed_api(text: str):
    if not nvidia_embed.is_configured():
        logger.error(
            "[embeddings] NVIDIA_API_KEY is not set; skipping embeddings "
            "(deduplication disabled for this item)"
        )
        return None

    try:
        return nvidia_embed.embed(text, input_type="passage", model=EMBEDDING_MODEL)
    except nvidia_embed.NvidiaEmbedError as exc:
        logger.error("[embeddings] NVIDIA embed request failed: %s", exc)
        return None


def get_embedding(text: str) -> list[float] | None:
    """
    Return a dense vector for `text`, or None when no backend can serve it.

    The api backend intentionally does NOT fall back to the local model: mixing
    2048-d and 384-d vectors in one comparison set would silently corrupt
    dedup. Returning None keeps every stored vector dimensionally consistent
    and lets the caller degrade explicitly.
    """
    if EMBEDDING_BACKEND == "local_minilm":
        return _embed_local(text)
    return _embed_api(text)
