from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# OAuth2 scheme used by other endpoints (if any)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/auth/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    # Simple dev-only login:
    #   email: dev@cloudreadyai.com
    #   password: test
    if payload.email == "dev@cloudreadyai.com" and payload.password == "test":
        return TokenResponse(access_token="dev-devtoken")
    # Anything else → 401
    raise HTTPException(status_code=401, detail="Invalid email or password")
