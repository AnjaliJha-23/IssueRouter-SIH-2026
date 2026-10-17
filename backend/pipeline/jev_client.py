"""
Thin HTTP client for TypeSafe's System One ("Jev") decision model.

Deliberately minimal: one POST to /v1/systemone carrying a named map of typed
questions, a bounded retry on 429 (rate limited) / 529 (overloaded), and a hard
timeout. It uses httpx, which the project already depends on, so no new package
is introduced.

API reference: https://docs.typesafe.ai/api
"""

import os
import time

import httpx

DEFAULT_API_URL = "https://api.typesafe.ai/v1/systemone"


class JevError(RuntimeError):
    """Raised when Jev cannot be reached, is misconfigured, or returns an error."""


def api_url() -> str:
    return (os.getenv("TYPESAFE_API_URL") or DEFAULT_API_URL).strip()


def api_key() -> str:
    return (os.getenv("TYPESAFE_API_KEY") or "").strip()


def is_configured() -> bool:
    """True when a Jev API key is present. Never exposes the key itself."""
    return bool(api_key())


def default_model() -> str:
    return (os.getenv("JEV_MODEL") or "jev-latest").strip()


def _timeout() -> float:
    try:
        return float(os.getenv("JEV_TIMEOUT", "20"))
    except ValueError:
        return 20.0


def _max_retries() -> int:
    try:
        return int(os.getenv("JEV_MAX_RETRIES", "2"))
    except ValueError:
        return 2


def ask(state, questions: dict, model: str | None = None, timeout: float | None = None) -> dict:
    """Evaluate `state` against a map of typed `questions`.

    Returns the parsed JSON response (``{"model", "answers", "usage"}``).
    Raises :class:`JevError` if the key is missing or every attempt fails.
    """
    key = api_key()
    if not key:
        raise JevError("TYPESAFE_API_KEY is not set")

    payload = {
        "state": state,
        "model": model or default_model(),
        "questions": questions,
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    timeout = timeout or _timeout()
    retries = _max_retries()
    last_error = "unknown error"

    for attempt in range(retries + 1):
        if attempt:
            time.sleep(0.5 * (2 ** (attempt - 1)))  # 0.5s, then 1.0s
        try:
            response = httpx.post(api_url(), json=payload, headers=headers, timeout=timeout)
        except httpx.HTTPError as exc:
            last_error = f"transport error: {exc}"
            continue

        # Retry these two; they are transient by definition.
        if response.status_code in (429, 529):
            last_error = f"HTTP {response.status_code}: {response.text[:200]}"
            continue

        if response.status_code >= 400:
            raise JevError(f"HTTP {response.status_code}: {response.text[:300]}")

        try:
            return response.json()
        except ValueError as exc:
            raise JevError(f"invalid JSON in response: {exc}") from exc

    raise JevError(f"request failed after {retries + 1} attempt(s): {last_error}")
