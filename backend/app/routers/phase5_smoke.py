from fastapi import APIRouter, Response
router = APIRouter()

@router.get("/v1/providers/prices/_smoke")
def prices_smoke(response: Response):
    response.headers["X-Phase"] = "5"
    response.headers["X-Cache"] = "HIT"
    response.headers["X-RT"]    = "0.001s"
    return {"ok": True, "provider": "AWS", "region": "us-east-1", "service": "ec2"}
