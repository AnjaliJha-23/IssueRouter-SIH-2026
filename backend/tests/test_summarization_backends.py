"""
backend/tests/test_summarization_backends.py
Contract tests for the summarization providers.

The suite runs the deterministic extractive backend (see conftest.py); the
hosted NVIDIA NIM path is exercised here with a stubbed HTTP layer so no key or
network is needed. Set SUMMARIZE_LIVE_TEST=1 with NVIDIA_API_KEY to hit NIM.
"""
import json
import os
import sys

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

from pipeline import nvidia_llm
import pipeline.summarization as summarization
from pipeline.summarization import generate_summary


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text or str(payload)

    def json(self):
        if self._payload is None:
            raise ValueError("no JSON body")
        return self._payload


def chat_response(content):
    return FakeResponse(200, {
        "choices": [{"index": 0, "message": {"role": "assistant", "content": content}}],
        "usage": {"prompt_tokens": 80, "completion_tokens": 20},
    })


def install_post(monkeypatch, responses):
    """Stub httpx.post with a scripted list of responses; records each call."""
    calls = []

    def fake_post(url, **kwargs):
        calls.append({"url": url, **kwargs})
        result = responses[min(len(calls) - 1, len(responses) - 1)]
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(nvidia_llm.httpx, "post", fake_post)
    return calls


@pytest.fixture
def nvidia_backend(monkeypatch):
    monkeypatch.setattr(summarization, "SUMMARIZATION_BACKEND", "nvidia")
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-test-key")
    monkeypatch.delenv("NVIDIA_MODEL", raising=False)
    monkeypatch.setattr(nvidia_llm.time, "sleep", lambda _seconds: None)
    return summarization


# ── Deterministic backend ──────────────────────────────────────────────────

def test_extractive_backend_is_deterministic_offline(monkeypatch):
    monkeypatch.setattr(summarization, "SUMMARIZATION_BACKEND", "extractive")
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-test-key")

    calls = install_post(monkeypatch, [chat_response('{"title": "ignored", "description": "ignored"}')])
    result = generate_summary(None, "Broken handpump in Kanke", "Water & Sanitation", "Kanke, Ranchi")

    assert result == {
        "title": "Water & Sanitation Issue in Kanke, Ranchi",
        "description": "Broken handpump in Kanke",
        "model": "extractive",
    }
    assert calls == []


def test_long_evidence_is_truncated_in_fallback(monkeypatch):
    monkeypatch.setattr(summarization, "SUMMARIZATION_BACKEND", "extractive")

    result = generate_summary(None, "x" * 400, "Healthcare", "Ranchi")

    assert result["description"].endswith("...")
    assert len(result["description"]) == 150


# ── Hosted backend contract ────────────────────────────────────────────────

def test_request_payload_matches_nim_chat_contract(nvidia_backend, monkeypatch):
    calls = install_post(monkeypatch, [chat_response(
        '{"title": "PHC without doctor", "description": "Namkum PHC has no doctor for 3 months."}'
    )])

    result = generate_summary(None, "PHC me doctor nahi hai", "Healthcare", "Namkum, Ranchi")

    assert result == {
        "title": "PHC without doctor",
        "description": "Namkum PHC has no doctor for 3 months.",
        "model": summarization.SUMMARIZATION_MODEL,
    }
    assert len(calls) == 1
    assert calls[0]["url"].endswith("/chat/completions")

    payload = calls[0]["json"]
    assert payload["model"] == summarization.SUMMARIZATION_MODEL
    assert payload["max_tokens"] == 150
    assert payload["temperature"] == 0.1
    assert payload["messages"][0]["role"] == "user"
    assert "PHC me doctor nahi hai" in payload["messages"][0]["content"]
    assert calls[0]["headers"]["Authorization"] == "Bearer nvapi-test-key"


def test_nvidia_model_env_override_is_used(nvidia_backend, monkeypatch):
    # Deliberately different from config.SUMMARIZATION_MODEL, so this proves the
    # override rather than restating the default.
    override = "mistralai/mistral-7b-instruct-v0.3"
    assert override != summarization.SUMMARIZATION_MODEL
    monkeypatch.setenv("NVIDIA_MODEL", override)
    calls = install_post(monkeypatch, [chat_response('{"title": "T", "description": "D"}')])

    generate_summary(None, "text", "Healthcare", "Ranchi")

    assert calls[0]["json"]["model"] == override
    assert summarization.active_model() == override


def test_markdown_wrapped_json_is_parsed(nvidia_backend, monkeypatch):
    install_post(monkeypatch, [chat_response(
        '```json\n{"title": "Water crisis", "description": "Wells dried up in Jharia."}\n```'
    )])

    result = generate_summary(None, "pani nahi hai", "Water & Sanitation", "Jharia, Dhanbad")

    assert result["title"] == "Water crisis"


def test_missing_key_falls_back_to_extractive(nvidia_backend, monkeypatch):
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    calls = install_post(monkeypatch, [chat_response('{"title": "T", "description": "D"}')])

    result = generate_summary(None, "power cut since morning", "Energy", "Ranchi")

    assert result["title"] == "Energy Issue in Ranchi"
    assert calls == []


def test_retryable_status_is_retried(nvidia_backend, monkeypatch):
    calls = install_post(monkeypatch, [
        FakeResponse(429, text="rate limited"),
        chat_response('{"title": "T", "description": "D"}'),
    ])

    result = generate_summary(None, "text", "Healthcare", "Ranchi")

    assert result["title"] == "T"
    assert result["description"] == "D"
    assert result["model"] == summarization.SUMMARIZATION_MODEL
    assert len(calls) == 2


def test_unparsable_reply_falls_back_to_extractive(nvidia_backend, monkeypatch):
    install_post(monkeypatch, [chat_response("I cannot help with that.")])

    result = generate_summary(None, "handpump broken", "Water & Sanitation", "Kanke")

    assert result["title"] == "Water & Sanitation Issue in Kanke"
    assert result["description"] == "handpump broken"


def test_http_error_falls_back_to_extractive(nvidia_backend, monkeypatch):
    install_post(monkeypatch, [FakeResponse(401, text="unauthorized")])

    result = generate_summary(None, "handpump broken", "Water & Sanitation", "Kanke")

    assert result["description"] == "handpump broken"
