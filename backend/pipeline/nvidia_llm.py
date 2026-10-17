"""
Thin client for NVIDIA NIM chat completions.

NIM exposes an OpenAI-compatible /chat/completions endpoint, so this is a plain
httpx POST with a bounded retry. No SDK dependency is added.

Endpoint: POST {NVIDIA_BASE_URL}/chat/completions
"""

import os
import time

import httpx

DEFAULT_BASE_URL = "https://integrate.api.nvidia.com/v1"

# 429 and 5xx are transient. 400/401/403/404/422 are caller errors and must not
# be retried: the same request fails the same way and only burns quota.
_RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504, 529})


class NvidiaLLMError(RuntimeError):
    """Raised when the chat endpoint is unreachable or returns an error."""


def _env(name: str, default: str) -> str:
    return (os.getenv(name) or default).strip()


def api_key() -> str:
    return _env("NVIDIA_API_KEY", "")


def is_configured() -> bool:
    return bool(api_key())


def base_url() -> str:
    return _env("NVIDIA_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def _timeout() -> float:
    try:
        return float(_env("NVIDIA_TIMEOUT", "30"))
    except ValueError:
        return 30.0


def _max_retries() -> int:
    try:
        return int(_env("NVIDIA_MAX_RETRIES", "2"))
    except ValueError:
        return 2


def chat(
    messages: list[dict],
    model: str,
    max_tokens: int = 150,
    temperature: float = 0.1,
) -> str:
    """
    Return the assistant message content for a chat completion.

    Raises NvidiaLLMError if the key is missing or every attempt fails. The
    caller decides whether that is fatal (see pipeline.summarization).
    """
    key = api_key()
    if not key:
        raise NvidiaLLMError("NVIDIA_API_KEY is not set")

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    url = f"{base_url()}/chat/completions"

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
            raise NvidiaLLMError(f"HTTP {response.status_code}: {response.text[:300]}")

        try:
            body = response.json()
        except ValueError as exc:
            raise NvidiaLLMError(f"invalid JSON in response: {exc}") from exc

        choices = body.get("choices") or []
        content = ((choices[0].get("message") or {}).get("content") if choices else None)
        if not content:
            raise NvidiaLLMError("response contained no message content")

        return content

    raise NvidiaLLMError(f"failed after {attempts} attempt(s): {last_error}")
