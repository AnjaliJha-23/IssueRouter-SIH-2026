"""
Thin client for NVIDIA's NIM hosted text-embedding endpoint.

A single POST to /v1/embeddings with bounded retries. Uses httpx, which the
project already depends on, so the hosted backend adds no new packages and
keeps no model weights in the process.

API reference (verified against the live OpenAPI definition, 2026-08):
https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-embed-1b-infer

Note: `input_type` is mandatory on the Nemotron embedding models. "passage" is
for content being indexed, "query" for lookups, and the two must not be
interchanged or retrieval quality drops sharply. Every IssueRouter call site
compares evidence against evidence, so they are all passages.
"""

import os
import time

import httpx

DEFAULT_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "nvidia/nemotron-3-embed-1b"

# 429 and 5xx are transient. 400/401/403/422 are caller errors and must not be
# retried: the same request will fail the same way and only burns quota.
_RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504, 529})


class NvidiaEmbedError(RuntimeError):
    """Raised when the embedding endpoint is unreachable or returns an error."""


def _env(name: str, default: str) -> str:
    return (os.getenv(name) or default).strip()


def api_key() -> str:
    return _env("NVIDIA_API_KEY", "")


def is_configured() -> bool:
    return bool(api_key())


def base_url() -> str:
    # NVIDIA_EMBED_BASE_URL wins, then the shared NVIDIA_BASE_URL, then the
    # public catalog. Embeddings and chat normally share one base URL, so the
    # shared variable is usually the only one that needs setting.
    explicit = _env("NVIDIA_EMBED_BASE_URL", "")
    if explicit:
        return explicit.rstrip("/")
    return _env("NVIDIA_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def default_model() -> str:
    return _env("NVIDIA_EMBED_MODEL", DEFAULT_MODEL)


def _timeout() -> float:
    try:
        return float(_env("NVIDIA_EMBED_TIMEOUT", "20"))
    except ValueError:
        return 20.0


def _max_retries() -> int:
    try:
        return int(_env("NVIDIA_EMBED_MAX_RETRIES", "2"))
    except ValueError:
        return 2


def embed(text: str, input_type: str = "passage", model: str | None = None) -> list[float]:
    """
    Return the embedding vector for a single piece of text.

    Raises NvidiaEmbedError if the key is missing or every attempt fails. The
    caller decides whether that is fatal (see pipeline.embeddings).
    """
    key = api_key()
    if not key:
        raise NvidiaEmbedError("NVIDIA_API_KEY is not set")

    payload = {
        "input": [text],
        "model": model or default_model(),
        "input_type": input_type,
        "encoding_format": "float",
        # Complaints routinely exceed the 4096-token window; truncate rather
        # than fail the whole submission with a 400.
        "truncate": "END",
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    url = f"{base_url()}/embeddings"

    attempts = _max_retries() + 1
    last_error = "unknown error"

    for attempt in range(attempts):
        if attempt:
            time.sleep(0.5 * (2 ** (attempt - 1)))
        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=_timeout())
        except httpx.HTTPError as exc:
            last_error = f"transport error: {exc}"
            continue

        if response.status_code in _RETRYABLE_STATUS:
            last_error = f"HTTP {response.status_code}: {response.text[:200]}"
            continue

        if response.status_code >= 400:
            raise NvidiaEmbedError(f"HTTP {response.status_code}: {response.text[:300]}")

        try:
            body = response.json()
        except ValueError as exc:
            raise NvidiaEmbedError(f"invalid JSON in response: {exc}") from exc

        data = body.get("data") or []
        vector = data[0].get("embedding") if data else None
        if not vector:
            raise NvidiaEmbedError("response contained no embedding vector")

        return [float(value) for value in vector]

    raise NvidiaEmbedError(f"failed after {attempts} attempt(s): {last_error}")
