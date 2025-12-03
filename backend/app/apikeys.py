from fastapi import APIRouter, Depends, HTTPException, Request, Body
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
import hashlib, secrets, base64
from .db import get_db
from .auth import current_user as get_current_user  # reuse bearer auth
from typing import Optional

router = APIRouter(prefix="/apikeys", tags=["apikeys"])

def _new_key() -> str:
    raw = base64.urlsafe_b64encode(secrets.token_bytes(24)).decode().rstrip("=")
    return f"crk_{raw}"

def _hash(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def audit(db: Session, user_id: Optional[str], action: str, meta: dict|None=None):
    db.execute(text("""
        insert into audit_logs(id,user_id,action,metadata,created_at)
        values (gen_random_uuid(), :uid, :act, :meta::jsonb, now())
    """), {"uid": user_id, "act": action, "meta": meta and json_dumps(meta)})
    db.commit()

try:
    import json
    def json_dumps(d): return json.dumps(d)
except Exception:  # minimal fallback
    def json_dumps(d): return "{}"

class CreateKeyIn(BaseModel):
    name: str

@router.post("", summary="Create API key (returns plaintext once)")
def create_apikey(body: CreateKeyIn, db: Session = Depends(get_db), me=Depends(get_current_user)):
    key = _new_key()
    kh = _hash(key)
    db.execute(text("""
        insert into api_keys(id,user_id,name,key_hash) values (gen_random_uuid(), :uid, :name, :kh)
    """), {"uid": me["id"], "name": body.name, "kh": kh})
    db.commit()
    #audit(db, me["id"], "api_key.create", {"name": body.name})
    return {"ok": True, "api_key": key}

@router.get("", summary="List my API keys (no secrets)")
def list_apikeys(db: Session = Depends(get_db), me=Depends(get_current_user)):
    rows = db.execute(text("""
        select id, name, created_at, revoked_at, last_used_at from api_keys
        where user_id=:uid order by created_at desc
    """), {"uid": me["id"]}).mappings().all()
    return {"ok": True, "items": rows}

@router.delete("/{key_id}", summary="Revoke API key by id")
def revoke_apikey(key_id: str, db: Session = Depends(get_db), me=Depends(get_current_user)):
    r = db.execute(text("""
        update api_keys set revoked_at=now()
        where id=:id and user_id=:uid and revoked_at is null
        returning id
    """), {"id": key_id, "uid": me["id"]}).first()
    if not r:
        raise HTTPException(404, "Not found or already revoked")
    db.commit()
    #audit(db, me["id"], "api_key.revoke", {"id": key_id})
    return {"ok": True}

# ===== API-key auth dependency =====
def api_user_from_key(request: Request, db: Session = Depends(get_db)):
    key = request.headers.get("X-API-Key")
    if not key:
        raise HTTPException(401, "Missing X-API-Key")
    kh = _hash(key)
    row = db.execute(text("""
        select u.id, u.email, u.display_name
        from api_keys k join users u on u.id=k.user_id
        where k.key_hash=:kh and k.revoked_at is null
    """), {"kh": kh}).mappings().first()
    if not row:
        raise HTTPException(401, "Invalid API key")
    db.execute(text("update api_keys set last_used_at=now() where key_hash=:kh"), {"kh": kh})
    db.commit()
    return row

# ===== RBAC helper =====
def require_role(role_name: str):
    def inner(me = Depends(get_current_user), db: Session = Depends(get_db)):
        has = db.execute(text("""
            select 1 from user_roles ur
              join roles r on r.id=ur.role_id
            where ur.user_id=:uid and r.name=:rn
        """), {"uid": me["id"], "rn": role_name}).first()
        if not has:
            raise HTTPException(403, "Forbidden")
        return me
    return inner

# ===== Probes: admin & service endpoints =====
@router.get("/admin/ping", summary="Admin-only ping")
def admin_ping(me = Depends(require_role("admin"))):
    return {"ok": True, "role": "admin", "user_id": me["id"]}

@router.get("/svc/ping", summary="Service ping (API key or bearer OK)")
def svc_ping(me_bearer = Depends(get_current_user), me_key = Depends(api_user_from_key)):
    # If either dep passes, return OK. If both run, prefer bearer.
    me = me_bearer or me_key
    return {"ok": True, "via": "bearer" if me_bearer else "apikey", "user_id": me["id"]}
