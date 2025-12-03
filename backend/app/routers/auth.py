from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest) -> LoginResponse:
    """
    Simple dev-only login:
    - email: dev@cloudreadyai.com
    - password: test
    Anything else → 401.
    """
    if payload.email == "dev@cloudreadyai.com" and payload.password == "test":
        return LoginResponse(access_token="dev-devtoken")

    raise HTTPException(status_code=401, detail="Invalid email or password")
