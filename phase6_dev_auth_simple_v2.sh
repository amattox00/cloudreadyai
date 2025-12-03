#!/usr/bin/env bash
set -euo pipefail

echo "==[ Phase 6 – Dev Auth v2: simple login for any credentials ]=="

cd ~/cloudreadyai/backend

# Activate venv if present
if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

AUTH_FILE="app/auth.py"

if [[ ! -f "$AUTH_FILE" ]]; then
  echo "ERROR: $AUTH_FILE not found. Adjust the path if your auth module lives elsewhere."
  exit 1
fi

echo "Rewriting $AUTH_FILE with dev-friendly auth module..."

cat > "$AUTH_FILE" << 'PYEOF'
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# Dev-only token and defaults
DEV_TOKEN = "dev-token"
DEV_DEFAULT_EMAIL = "dev@cloudready.local"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(prefix="/auth", tags=["auth"])
# In case app.main imports a different name
auth_router = router  # alias


class LoginRequest(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str


class MeResponse(BaseModel):
    email: str
    name: str
    role: str = "developer"


def _ensure_token(token: str = Depends(oauth2_scheme)) -> str:
    if token != DEV_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid dev token",
        )
    return token


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    """
    Dev-only login endpoint.

    - Accepts ANY email/password.
    - Always returns the same dev token.
    - Echoes back the email (or a default one if empty).
    """
    email = payload.email or DEV_DEFAULT_EMAIL
    return TokenResponse(access_token=DEV_TOKEN, email=email)


@router.get("/me", response_model=MeResponse)
async def me(_: str = Depends(_ensure_token)) -> MeResponse:
    """
    Dev-only /auth/me endpoint.

    - Returns a static dev user.
    - Frontend "Who am I?" or auth checks should work as-is.
    """
    return MeResponse(
        email=DEV_DEFAULT_EMAIL,
        name="CloudReadyAI Dev User",
        role="developer",
    )
PYEOF

echo "Running a quick compile check on $AUTH_FILE..."
python3 -m compileall "$AUTH_FILE"

echo "Restarting backend to load new dev auth module..."
sudo systemctl restart cloudready-backend

echo "Dev auth module installed. You can now log in with ANY email/password."
