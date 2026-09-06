"""
api/auth.py - Simple JWT Authentication for SIH Mock setup.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
try:
    import jwt
except ImportError:
    jwt = None

from db.database import get_db
from db.models import User, Organization

router = APIRouter(prefix="/api/auth", tags=["auth"])

SECRET_KEY = "sih-mock-secret-key"
ALGORITHM = "HS256"

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
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(days=1))
    to_encode.update({"exp": expire})
    if jwt:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    else: # Fallback if PyJWT isn't installed
        encoded_jwt = f"mock_token_{data['sub']}"
    return encoded_jwt

@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    # Very simple mock authentication (ignores password check for MVP)
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
def get_me(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    org = None
    if user.org_id:
        org_obj = db.query(Organization).filter(Organization.id == user.org_id).first()
        if org_obj:
            org = {"id": org_obj.id, "name": org_obj.name, "type": org_obj.type}

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "organization": org
    }
