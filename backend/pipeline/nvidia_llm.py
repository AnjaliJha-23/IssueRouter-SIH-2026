"""
Thin client for NVIDIA NIM chat completions.

NIM exposes an OpenAI-compatible /chat/completions endpoint, so this is a plain
httpx POST with a bounded retry. No SDK dependency is added.

Endpoint: POST {NVIDIA_BASE_URL}/chat/completions

Two gateway behaviours this client must handle explicitly:

* ``stream`` defaults to **true** in the NIM schema. We always want one JSON
  body, so ``stream=False`` is sent rather than trusted.
* Reasoning models (the "Nemotron" family) think before answering. The trace is
  returned in ``message.reasoning_content`` rather than ``message.content`` and
  is produced first, so a small ``max_tokens`` is spent on reasoning and the
  answer arrives empty. ``reasoning_budget`` is set to 0 to end the trace
  immediately; see :func:`reasoning_budget`.

``chat_template_kwargs.enable_thinking=false`` is the other obvious switch, and
it appears in NVIDIA's own request examples -- but on this gateway it **hangs**
when combined with ``stream=False``. The request never returns, and the caller
sees only a read timeout (measured: >120s vs ~5s for the same call). Do not
reintroduce it without testing both stream modes.
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


def reasoning_budget() -> str:
    """Value for the top-level ``reasoning_budget`` field, or ``"omit"``.

    The reasoning trace is generated before the answer and counts against
    ``max_tokens``, so with a small budget the reply arrives empty and carries
    only ``message.reasoning_content``. ``reasoning_budget=0`` forces the trace
    to end immediately, which is the documented way to turn thinking off.

    This is deliberately the top-level field rather than
    ``chat_template_kwargs.enable_thinking``: the latter hangs this gateway when
    combined with ``stream=False`` (see the module docstring).

    Return ``"omit"`` to drop the field entirely for models whose request
    schema lacks it.
    """
    value = _env("NVIDIA_REASONING_BUDGET", "0").lower()
    if value in ("omit", "unset", "none", ""):
        return "omit"
    return value


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
        # The NIM schema defaults stream to true. Ask for a single JSON body
        # explicitly instead of relying on the gateway to downgrade SSE.
        "stream": False,
    }

    budget = reasoning_budget()
    if budget != "omit":
        # Send a number when the value looks numeric, so the gateway sees the
        # documented integer type rather than a string.
        payload["reasoning_budget"] = int(budget) if budget.lstrip("-").isdigit() else budget
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
        message = (choices[0].get("message") or {}) if choices else {}
        content = message.get("content")
        if not content:
            finish_reason = choices[0].get("finish_reason") if choices else None
            reasoning = message.get("reasoning_content")
            if reasoning:
                # Distinguish this from a genuinely empty reply: the model
                # thought instead of answering, so either the reasoning budget
                # is still open or max_tokens ran out before the answer began.
                raise NvidiaLLMError(
                    "model returned only a reasoning trace "
                    f"({len(reasoning)} chars, finish_reason={finish_reason!r}); "
                    "thinking is still enabled - check NVIDIA_REASONING_BUDGET"
                )
            raise NvidiaLLMError(
                f"response contained no message content (finish_reason={finish_reason!r})"
            )

        return content

    raise NvidiaLLMError(f"failed after {attempts} attempt(s): {last_error}")
