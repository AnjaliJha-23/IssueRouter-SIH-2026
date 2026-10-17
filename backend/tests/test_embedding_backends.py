"""
backend/tests/test_embedding_backends.py
Contract tests for the hosted (NVIDIA NIM) and local embedding backends.

The suite runs against the local backend (see conftest.py); the hosted path is
exercised here with a stubbed HTTP layer so no key or network is needed. Set
EMBED_LIVE_TEST=1 with NVIDIA_API_KEY to hit the real endpoint.
"""
import os
import subprocess
import sys

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

from pipeline import nvidia_embed
from pipeline.deduplication import resolve
from pipeline.embeddings import _MODEL_DIMENSIONS, embedding_tag


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text or str(payload)

    def json(self):
        if self._payload is None:
            raise ValueError("no JSON body")
        return self._payload


def vector_response(size=2048):
    return FakeResponse(200, {
        "object": "list",
        "data": [{"object": "embedding", "index": 0, "embedding": [0.01] * size}],
        "model": "nvidia/nemotron-3-embed-1b",
        "usage": {"prompt_tokens": 12, "total_tokens": 12},
    })


@pytest.fixture
def api_backend(monkeypatch):
    """Point pipeline.embeddings at the hosted backend with a usable key."""
    import pipeline.embeddings as embeddings

    monkeypatch.setattr(embeddings, "EMBEDDING_BACKEND", "api")
    monkeypatch.setattr(embeddings, "EMBEDDING_MODEL", "nvidia/nemotron-3-embed-1b")
    monkeypatch.setattr(embeddings, "EMBEDDING_DIM", 2048)
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-test-key")
    monkeypatch.setattr(nvidia_embed.time, "sleep", lambda _seconds: None)
    return embeddings


def install_post(monkeypatch, responses):
    """Stub httpx.post with a scripted list of responses; records each call."""
    calls = []

    def fake_post(url, **kwargs):
        calls.append({"url": url, **kwargs})
        result = responses[min(len(calls) - 1, len(responses) - 1)]
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(nvidia_embed.httpx, "post", fake_post)
    return calls


# ── Model metadata ─────────────────────────────────────────────────────────

def test_embedding_tag_encodes_model_and_dimension():
    tag = embedding_tag()
    model, _, dim = tag.rpartition(":")
    assert model
    assert dim.isdigit()


def test_known_models_have_declared_dimensions():
    assert _MODEL_DIMENSIONS["nvidia/nemotron-3-embed-1b"] == 2048
    assert _MODEL_DIMENSIONS["all-MiniLM-L6-v2"] == 384


def test_base_url_inherits_shared_nvidia_base_url(monkeypatch):
    # Embeddings and chat share one base URL in practice, so setting the shared
    # variable alone must be enough.
    monkeypatch.delenv("NVIDIA_EMBED_BASE_URL", raising=False)
    monkeypatch.setenv("NVIDIA_BASE_URL", "https://nim.internal.example/v1")

    assert nvidia_embed.base_url() == "https://nim.internal.example/v1"

    monkeypatch.setenv("NVIDIA_EMBED_BASE_URL", "https://embed-only.example/v1/")

    assert nvidia_embed.base_url() == "https://embed-only.example/v1"


# ── Hosted backend request/response contract ───────────────────────────────

def test_request_payload_matches_nim_contract(api_backend, monkeypatch):
    calls = install_post(monkeypatch, [vector_response()])

    vector = api_backend.get_embedding("Doctor absenteeism at Namkum PHC")

    assert len(vector) == 2048
    assert len(calls) == 1
    assert calls[0]["url"].endswith("/embeddings")

    payload = calls[0]["json"]
    assert payload["model"] == "nvidia/nemotron-3-embed-1b"
    assert payload["input"] == ["Doctor absenteeism at Namkum PHC"]
    # Nemotron embedding models require an explicit input_type.
    assert payload["input_type"] == "passage"
    assert payload["truncate"] == "END"
    assert calls[0]["headers"]["Authorization"] == "Bearer nvapi-test-key"


def test_retryable_status_is_retried(api_backend, monkeypatch):
    calls = install_post(monkeypatch, [
        FakeResponse(429, text="rate limited"),
        FakeResponse(529, text="overloaded"),
        vector_response(),
    ])

    vector = api_backend.get_embedding("Water pipeline burst in Jharia")

    assert len(vector) == 2048
    assert len(calls) == 3


def test_client_error_is_not_retried(api_backend, monkeypatch):
    calls = install_post(monkeypatch, [FakeResponse(401, text="unauthorized")])

    assert api_backend.get_embedding("Anything") is None
    assert len(calls) == 1


def test_missing_key_returns_none_without_calling_http(api_backend, monkeypatch):
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    calls = install_post(monkeypatch, [vector_response()])

    assert api_backend.get_embedding("Anything") is None
    assert calls == []


def test_api_failure_does_not_emit_a_different_dimension_vector(api_backend, monkeypatch):
    # A silent fall back to the 384-d local model here would put mixed
    # dimensions in the same comparison set and corrupt dedup scores.
    install_post(monkeypatch, [FakeResponse(500, text="server error")])

    assert api_backend.get_embedding("Anything") is None


def test_malformed_response_body_returns_none(api_backend, monkeypatch):
    install_post(monkeypatch, [FakeResponse(200, payload={"data": []})])

    assert api_backend.get_embedding("Anything") is None


# ── Degradation contract ───────────────────────────────────────────────────

def test_dedup_treats_missing_embedding_as_new_challenge():
    candidates = [
        {"id": "HC-001", "domain": "Healthcare", "district": "Ranchi",
         "canonical_embedding": [0.1] * 2048}
    ]

    res = resolve(None, "Healthcare", "Ranchi", candidates)

    assert res["action"] == "new_challenge"
    assert res["matched_challenge_id"] is None


def test_api_backend_never_imports_torch():
    # The whole point of the hosted backend: torch/transformers stay out of the
    # process. Verified in a subprocess so earlier tests cannot mask the result.
    code = (
        "import os, sys;"
        "os.environ['EMBEDDING_BACKEND'] = 'api';"
        "os.environ.pop('NVIDIA_API_KEY', None);"
        "import pipeline.embeddings as e;"
        "e.get_embedding('probe');"
        "print('torch' in sys.modules, 'transformers' in sys.modules)"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip().endswith("False False"), proc.stdout
