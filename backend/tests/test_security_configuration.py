"""
backend/tests/test_security_configuration.py
Comprehensive test suite for Phase 4:
- Dynamic CORS origin parsing, trimming, empty token filtering, and error handling
- Verification that allow_credentials=True and wildcards are prohibited
- JWT secret configuration via environment variables
- Consistent secret encoding/decoding and mismatch rejection
- Explicit production missing-secret guard and development fallback
- API-level CORS header verification using FastAPI TestClient
- Authentication contract regression (Bearer tokens, /api/auth/login, /api/auth/me)
"""
import os
import sys
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app, get_cors_origins, DEFAULT_CORS_ORIGINS
from api.auth import (
    get_jwt_secret,
    create_access_token,
    decode_token,
    DEV_JWT_SECRET,
    SECRET_KEY,
    ALGORITHM
)


class TestCorsConfiguration:
    def test_default_cors_origins(self):
        """Without CORS_ORIGINS set, default development origins include http://localhost:3000."""
        with patch.dict(os.environ, {}, clear=True):
            origins = get_cors_origins()
            assert "http://localhost:3000" in origins
            assert "http://localhost:5173" in origins
            assert "http://127.0.0.1:5173" in origins

    def test_multiple_cors_origins(self):
        """Comma-separated CORS_ORIGINS should be parsed and whitespace-trimmed."""
        env_val = "http://localhost:3000, http://localhost:5173, https://example.com"
        with patch.dict(os.environ, {"CORS_ORIGINS": env_val}, clear=True):
            origins = get_cors_origins()
            assert origins == ["http://localhost:3000", "http://localhost:5173", "https://example.com"]

    def test_empty_cors_entries_removed(self):
        """Empty entries between commas or trailing commas must be filtered out."""
        env_val = "http://localhost:3000,, https://example.com, "
        with patch.dict(os.environ, {"CORS_ORIGINS": env_val}, clear=True):
            origins = get_cors_origins()
            assert origins == ["http://localhost:3000", "https://example.com"]

    def test_explicit_empty_cors_origins_raises_error(self):
        """Explicitly empty or whitespace-only CORS_ORIGINS must raise ValueError rather than silently broadening access."""
        with patch.dict(os.environ, {"CORS_ORIGINS": ""}, clear=True):
            with pytest.raises(ValueError, match="CORS_ORIGINS environment variable is set but empty"):
                get_cors_origins()

        with patch.dict(os.environ, {"CORS_ORIGINS": "   "}, clear=True):
            with pytest.raises(ValueError, match="CORS_ORIGINS environment variable is set but empty"):
                get_cors_origins()

        with patch.dict(os.environ, {"CORS_ORIGINS": " , , "}, clear=True):
            with pytest.raises(ValueError, match="CORS_ORIGINS environment variable contains no valid origins"):
                get_cors_origins()

    def test_credentials_enabled_and_no_wildcard(self):
        """Verify middleware configuration preserves allow_credentials=True and prohibits wildcard '*'."""
        cors_middlewares = [m for m in app.user_middleware if "CORSMiddleware" in str(m.cls)]
        assert len(cors_middlewares) > 0, "CORSMiddleware must be present in FastAPI user_middleware"

        kwargs = cors_middlewares[0].kwargs
        assert kwargs.get("allow_credentials") is True, "allow_credentials must be True for credentialed auth"
        
        configured_origins = kwargs.get("allow_origins", [])
        assert "*" not in configured_origins, "Wildcard '*' origin is strictly forbidden when allow_credentials=True"


class TestJwtSecretConfiguration:
    def test_jwt_secret_from_environment(self):
        """Verify JWT secret is read from JWT_SECRET environment variable."""
        custom_secret = "test-custom-secure-random-secret-key-987654321-32chars"
        with patch.dict(os.environ, {"JWT_SECRET": custom_secret}, clear=True):
            resolved = get_jwt_secret()
            assert resolved == custom_secret

    def test_secret_key_env_var_fallback(self):
        """Verify SECRET_KEY environment variable is honored if JWT_SECRET is unset."""
        legacy_secret = "test-legacy-secret-key-1234567890-32byteslong"
        with patch.dict(os.environ, {"SECRET_KEY": legacy_secret}, clear=True):
            resolved = get_jwt_secret()
            assert resolved == legacy_secret

    def test_jwt_secret_consistency_and_mismatch_rejection(self):
        """Token encoded with Secret A must decode with Secret A, and fail with Secret B."""
        secret_a = "secret-key-aaaa-1111-2222-3333-4444-5555"
        secret_b = "secret-key-bbbb-4444-5555-6666-7777-8888"

        with patch.dict(os.environ, {"JWT_SECRET": secret_a}, clear=True):
            token = create_access_token({"sub": "user-test-1", "role": "Citizen"})
            decoded = decode_token(token)
            assert decoded["sub"] == "user-test-1"
            assert decoded["role"] == "Citizen"

        with patch.dict(os.environ, {"JWT_SECRET": secret_b}, clear=True):
            from fastapi import HTTPException
            with pytest.raises(HTTPException) as exc_info:
                decode_token(token)
            assert exc_info.value.status_code == 401

    def test_missing_jwt_secret_in_development_uses_fallback(self):
        """When ENVIRONMENT=development, missing JWT_SECRET safely uses development fallback."""
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}, clear=True):
            resolved = get_jwt_secret()
            assert resolved == DEV_JWT_SECRET

    def test_missing_jwt_secret_in_production_raises_error(self):
        """When ENVIRONMENT=production or staging, missing JWT_SECRET must raise RuntimeError."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=True):
            with pytest.raises(RuntimeError, match="CRITICAL: JWT_SECRET environment variable is missing"):
                get_jwt_secret()

        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}, clear=True):
            with pytest.raises(RuntimeError, match="CRITICAL: JWT_SECRET environment variable is missing"):
                get_jwt_secret()

    def test_missing_jwt_secret_on_render_raises_error(self):
        """When deployed on Render (RENDER=true), missing JWT_SECRET must raise RuntimeError."""
        with patch.dict(os.environ, {"RENDER": "true"}, clear=True):
            with pytest.raises(RuntimeError, match="CRITICAL: JWT_SECRET environment variable is missing"):
                get_jwt_secret()

    def test_misconfigured_environment_raises_error(self):
        """Unknown or misspelled ENVIRONMENT values must raise RuntimeError rather than assuming dev fallback."""
        with patch.dict(os.environ, {"ENVIRONMENT": "produciton_misspelled"}, clear=True):
            with pytest.raises(RuntimeError, match="CRITICAL: Unknown ENVIRONMENT="):
                get_jwt_secret()

    def test_secret_key_symbol_preserved(self):
        """Verify SECRET_KEY symbol remains imported and accessible as a string for backwards compatibility."""
        assert isinstance(SECRET_KEY, str)
        assert len(SECRET_KEY) > 0


class TestApiLevelCorsVerification:
    def test_cors_headers_for_allowed_origin(self):
        """Allowed origin should receive Access-Control-Allow-Origin and Access-Control-Allow-Credentials."""
        client = TestClient(app)
        
        # Test OPTIONS preflight
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        }
        res_options = client.options("/", headers=headers)
        assert res_options.headers.get("access-control-allow-origin") == "http://localhost:3000"
        assert res_options.headers.get("access-control-allow-credentials") == "true"

        # Test GET request
        res_get = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert res_get.headers.get("access-control-allow-origin") == "http://localhost:3000"
        assert res_get.headers.get("access-control-allow-credentials") == "true"

    def test_cors_headers_denied_for_unauthorized_origin(self):
        """Unauthorized origin must NOT receive Access-Control-Allow-Origin header."""
        client = TestClient(app)
        res = client.get("/", headers={"Origin": "https://unauthorized-attacker.example.com"})
        assert "access-control-allow-origin" not in res.headers


class TestAuthenticationRegression:
    def test_login_and_bearer_me_flow(self):
        """Full authentication flow preserving Bearer token contract and response models."""
        client = TestClient(app)
        login_res = client.post("/api/auth/login", json={"email": "rahul@citizen.in", "password": "dummy"})
        assert login_res.status_code == 200
        data = login_res.json()
        assert data["token_type"] == "bearer"
        assert "access_token" in data
        assert data["role"] == "Citizen"

        token = data["access_token"]
        me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        me_data = me_res.json()
        assert me_data["name"] == "Rahul Kumar"
        assert me_data["role"] == "Citizen"
