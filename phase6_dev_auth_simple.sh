#!/usr/bin/env bash
set -euo pipefail

echo "==[ Phase 6 – Dev Auth: simple login for any credentials ]=="

cd ~/cloudreadyai/backend

# Activate venv if present
if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

AUTH_ROUTER="app/routers/auth.py"

if [[ ! -f "$AUTH_ROUTER" ]]; then
  echo "ERROR: $AUTH_ROUTER not found. Adjust the path if your auth router lives elsewhere."
  exit 1
fi

echo "Rewriting $AUTH_ROUTER with dev-friendly auth router..."

cat > "$AUTH_ROUTER" << 'PYEOF'
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

DEV_TOKEN = "dev-token"
DEV_DEFAULT_EMAIL = "dev@cloudready.local"


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
  Dev-only /auth/me.

  - Returns a static dev user.
  - Frontend "Who am I?" should work as-is.
  """
  return MeResponse(
    email=DEV_DEFAULT_EMAIL,
    name="CloudReadyAI Dev User",
    role="developer",
  )
PYEOF

echo "Running a quick compile check on $AUTH_ROUTER..."
python3 -m compileall "$AUTH_ROUTER"

echo "Restarting backend to load new dev auth router..."
sudo systemctl restart cloudready-backend

echo "Dev auth router installed. You can now log in with ANY email/password."
