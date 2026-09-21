"""
api/auth.py - JWT Authentication & RBAC Dependencies for IssueRouter (SIH 2026).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List

try:
    import jwt
except ImportError:
    jwt = None

from db.database import get_db
from db.models import User, Organization

import os

router = APIRouter(prefix="/api/auth", tags=["auth"])

DEV_JWT_SECRET = "sih-2026-issuerouter-secure-jwt-secret-key-convergence"
ALGORITHM = "HS256"

# Permitted development environments for fallback secret
DEV_ENVIRONMENTS = {"development", "dev", "local", "test", "testing"}


def get_jwt_secret() -> str:
    """
    Resolve the JWT signing and verification secret.
    Canonical environment variable: JWT_SECRET (with fallback to SECRET_KEY env var).

    Security Policy:
    - If JWT_SECRET or SECRET_KEY is set in environment: returns it.
    - If not set:
      - In production/staging (ENVIRONMENT is production/prod/staging or RENDER/cloud PORT is set):
        raises RuntimeError refusing to boot or issue tokens with an insecure default.
      - In development/testing (ENVIRONMENT in DEV_ENVIRONMENTS):
        returns DEV_JWT_SECRET.
      - If ENVIRONMENT is misconfigured (unrecognized non-dev value):
        raises RuntimeError.
      - If ENVIRONMENT is completely omitted in local development:
        returns DEV_JWT_SECRET.
    """
    configured_secret = (os.getenv("JWT_SECRET") or "").strip() or (os.getenv("SECRET_KEY") or "").strip()
    if configured_secret:
        return configured_secret

    raw_env = os.getenv("ENVIRONMENT")
    env_str = raw_env.strip().lower() if raw_env is not None else ""

    is_render = bool(os.getenv("RENDER") or os.getenv("RENDER_SERVICE_ID"))
    is_explicit_prod = env_str in ("production", "prod", "staging")
    has_cloud_port = bool(os.getenv("PORT") and os.getenv("PORT") != "8000")

    if is_explicit_prod or is_render or has_cloud_port:
        raise RuntimeError(
            "CRITICAL: JWT_SECRET environment variable is missing in production/cloud environment. "
            "A secure secret must be configured via the JWT_SECRET environment variable."
        )

    if env_str in DEV_ENVIRONMENTS:
        return DEV_JWT_SECRET

    if env_str:
        raise RuntimeError(
            f"CRITICAL: Unknown ENVIRONMENT='{raw_env}'. "
            "Must be one of ('development', 'production', 'staging', 'test'). "
            "Development fallback secret cannot be assumed."
        )

    return DEV_JWT_SECRET


# Backwards compatibility symbol for any external code referencing SECRET_KEY
SECRET_KEY = DEV_JWT_SECRET

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    name: str | None = None
    role: str
    org_id: str | None = None
    organization: dict | None = None

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(days=7))
    to_encode.update({"exp": expire})
    if jwt:
        signing_secret = get_jwt_secret()
        encoded_jwt = jwt.encode(to_encode, signing_secret, algorithm=ALGORITHM)
    else: # Fallback if PyJWT isn't installed
        encoded_jwt = f"mock_token_{data['sub']}"
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Decodes a JWT token or handles mock token fallback."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check for fallback mock token format
    if token.startswith("mock_token_"):
        sub = token.replace("mock_token_", "")
        return {"sub": sub}
        
    if jwt:
        verification_secret = get_jwt_secret()
        try:
            payload = jwt.decode(token, verification_secret, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        return {"sub": token}

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """FastAPI dependency to extract and verify the current authenticated user."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_optional_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    """FastAPI dependency that returns the authenticated user if present, or None without raising 401."""
    if not token:
        return None
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return None
        return db.query(User).filter(User.id == user_id).first()
    except Exception:
        return None

def require_roles(*allowed_roles: str):
    """Dependency factory to enforce role-based access control."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: role '{current_user.role}' is not authorized for this operation."
            )
        return current_user
    return role_checker

@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    # Simple mock authentication for SIH
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": user.id, "role": user.role})
    
    org_data = None
    if user.org_id:
        org_obj = db.query(Organization).filter(Organization.id == user.org_id).first()
        if org_obj:
            org_data = {"id": org_obj.id, "name": org_obj.name, "type": org_obj.type}

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "name": user.name,
        "role": user.role,
        "org_id": user.org_id,
        "organization": org_data
    }

@router.get("/me")
def get_me(
    email: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_user = current_user
    # Allow Gov admins to query other users by email if explicitly requested
    if email and email != current_user.email:
        if current_user.role == "Gov":
            found = db.query(User).filter(User.email == email).first()
            if found:
                target_user = found
        else:
            raise HTTPException(status_code=403, detail="Not authorized to query other user profiles")
    
    org = None
    if target_user.org_id:
        org_obj = db.query(Organization).filter(Organization.id == target_user.org_id).first()
        if org_obj:
            org = {"id": org_obj.id, "name": org_obj.name, "type": org_obj.type}

    return {
        "id": target_user.id,
        "name": target_user.name,
        "email": target_user.email,
        "role": target_user.role,
        "org_id": target_user.org_id,
        "organization": org
    }
