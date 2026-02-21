"""
Embedding generator for lesson semantic search.

Supports multiple backends (tried in order):
1. OpenAI text-embedding-3-small (if OPENAI_API_KEY set) — 384 dims
2. Voyage AI voyage-3-lite (if VOYAGE_API_KEY set) — 512 dims via httpx
3. Local sentence-transformers all-MiniLM-L6-v2 — 384 dims (needs enough RAM)

All backends produce normalized vectors for cosine similarity search.
If no backend is available, returns None (graceful degradation to keyword search).
"""

from __future__ import annotations

import os

# Detected backend (lazy initialization)
_backend: str | None = None  # "openai", "voyage", "local", or None
_openai_client = None
_local_model = None

EMBEDDING_DIM = 512  # Unified dimension: OpenAI (custom dims=512), Voyage (native 512), local (384 zero-padded)


def _detect_backend() -> str | None:
    """Detect the best available embedding backend."""
    global _backend

    if _backend is not None:
        return _backend if _backend != "none" else None

    # 1. OpenAI (installed, just needs API key)
    if os.getenv("OPENAI_API_KEY"):
        try:
            import openai  # noqa: F401
            _backend = "openai"
            print("[Embedding] Using OpenAI text-embedding-3-small")
            return _backend
        except ImportError:
            pass

    # 2. Voyage AI via httpx (no extra install, just API key)
    if os.getenv("VOYAGE_API_KEY"):
        try:
            import httpx  # noqa: F401
            _backend = "voyage"
            print("[Embedding] Using Voyage AI voyage-3-lite")
            return _backend
        except ImportError:
            pass

    # 3. Local sentence-transformers (if it loads without crashing)
    try:
        from sentence_transformers import SentenceTransformer
        global _local_model
        _local_model = SentenceTransformer("all-MiniLM-L6-v2")
        _backend = "local"
        print("[Embedding] Using local sentence-transformers")
        return _backend
    except Exception:
        pass

    _backend = "none"
    print("[Embedding] No embedding backend available. Set OPENAI_API_KEY or VOYAGE_API_KEY for semantic search.")
    return None


def _get_openai_client():
    """Get or create the OpenAI client."""
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI()
    return _openai_client


def _embed_openai(text: str) -> list[float] | None:
    """Generate embedding via OpenAI API."""
    try:
        client = _get_openai_client()
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
            dimensions=512,
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"[Embedding] OpenAI error: {e}")
        return None


def _embed_voyage(text: str) -> list[float] | None:
    """Generate embedding via Voyage AI API (using httpx)."""
    try:
        import httpx
        response = httpx.post(
            "https://api.voyageai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {os.getenv('VOYAGE_API_KEY')}",
                "Content-Type": "application/json",
            },
            json={
                "model": "voyage-3-lite",
                "input": [text],
                "input_type": "document",
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]
    except Exception as e:
        print(f"[Embedding] Voyage AI error: {e}")
        return None


def _embed_local(text: str) -> list[float] | None:
    """Generate embedding via local sentence-transformers (384 dims, zero-padded to 512)."""
    if _local_model is None:
        return None
    try:
        embedding = _local_model.encode(text, normalize_embeddings=True).tolist()
        # Zero-pad from 384 to 512 for pgvector compatibility
        if len(embedding) < EMBEDDING_DIM:
            embedding.extend([0.0] * (EMBEDDING_DIM - len(embedding)))
        return embedding
    except Exception as e:
        print(f"[Embedding] Local model error: {e}")
        return None


def _embed(text: str) -> list[float] | None:
    """Generate embedding using the detected backend."""
    backend = _detect_backend()
    if backend is None:
        return None

    if backend == "openai":
        return _embed_openai(text)
    elif backend == "voyage":
        return _embed_voyage(text)
    elif backend == "local":
        return _embed_local(text)
    return None


def get_embedding_dim() -> int:
    """Return the embedding dimension (always 512)."""
    return EMBEDDING_DIM


def is_available() -> bool:
    """Check if any embedding backend is available."""
    return _detect_backend() is not None


def generate_lesson_embedding(
    title: str,
    description: str = "",
    recommendation: str = "",
) -> list[float] | None:
    """Generate embedding for a lesson's semantic content.

    Concatenates the three most semantic fields into a single text.
    Returns None if no backend is available.
    """
    text = f"{title}. {description}. {recommendation}".strip(". ")
    return _embed(text)


def generate_query_embedding(query: str) -> list[float] | None:
    """Generate embedding for a search query.

    Returns None if no backend is available.
    """
    return _embed(query)
