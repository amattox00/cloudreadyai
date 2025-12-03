#!/usr/bin/env bash
set -euo pipefail

echo "==[ Phase 6 – Dev Auth (multi-path) ]=="

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

echo "Rewriting $AUTH_FILE with dev-friendly auth module (supports /auth/* and /v1/auth/*)..."

cat > "$AUTH_FILE" << 'PYEOF'
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# Dev-only token and defaults
DEV_TOKEN = "dev-token"
DEV_DEFAULT_EMAIL = "dev@cloudready.local"

# Prefix is empty so paths are absolute (we'll register both /auth/* and /v1/auth/*)
router = APIRouter(tags=["auth"])
auth_router = router  # in case main.py imports this name

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


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


# --- Login endpoints: /auth/login AND /v1/auth/login -----------------------

@router.post("/auth/login", response_model=TokenResponse)
@router.post("/v1/auth/login", response_model=TokenResponse, include_in_schema=False)
async def login(payload: LoginRequest) -> TokenResponse:
    """
    Dev-only login endpoint.

    - Accepts ANY email/password.
    - Always returns the same dev token.
    - Echoes back the email (or a default one if empty).
    """
    email = payload.email or DEV_DEFAULT_EMAIL
    return TokenResponse(access_token=DEV_TOKEN, email=email)


# --- Me endpoints: /auth/me AND /v1/auth/me --------------------------------

@router.get("/auth/me", response_model=MeResponse)
@router.get("/v1/auth/me", response_model=MeResponse, include_in_schema=False)
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

echo "Dev auth module installed. It now serves:"
echo "  - POST /auth/login and /v1/auth/login"
echo "  - GET  /auth/me    and /v1/auth/me"
