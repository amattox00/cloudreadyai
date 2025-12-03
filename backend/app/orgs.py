from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from .db import get_db
from .auth import current_user as get_current_user  # bearer-auth helper

router = APIRouter(prefix="/orgs", tags=["orgs"])

class OrgCreateIn(BaseModel):
    name: str

class ProjectCreateIn(BaseModel):
    name: str
    description: Optional[str] = None

def _is_org_role(db: Session, user_id: str, org_id: str, roles: List[str]) -> bool:
    row = db.execute(text("""
        select 1 from org_members where user_id=:uid and org_id=:oid and role = any(:roles)
    """), {"uid": user_id, "oid": org_id, "roles": roles}).first()
    return bool(row)

@router.post("", summary="Create org (caller becomes owner)")
def create_org(body: OrgCreateIn, db: Session = Depends(get_db), me = Depends(get_current_user)):
    org = db.execute(text("""
        insert into orgs(id,name) values (gen_random_uuid(), :name)
        returning id, name, created_at
    """), {"name": body.name}).mappings().first()
    db.execute(text("""
        insert into org_members(org_id,user_id,role) values (:oid, :uid, 'owner')
        on conflict do nothing
    """), {"oid": org["id"], "uid": me["id"]})
    db.commit()
    return {"ok": True, "org": org}

@router.get("", summary="List orgs where I am a member")
def list_my_orgs(db: Session = Depends(get_db), me = Depends(get_current_user)):
    rows = db.execute(text("""
        select o.id, o.name, o.created_at, m.role
        from orgs o
        join org_members m on m.org_id=o.id
        where m.user_id=:uid
        order by o.created_at desc
    """), {"uid": me["id"]}).mappings().all()
    return {"ok": True, "items": rows}

@router.post("/{org_id}/projects", summary="Create project (owner/admin)")
def create_project(org_id: str, body: ProjectCreateIn, db: Session = Depends(get_db), me = Depends(get_current_user)):
    if not _is_org_role(db, me["id"], org_id, ["owner","admin"]):
        raise HTTPException(403, "Forbidden: need owner/admin in org")
    proj = db.execute(text("""
        insert into projects(id, org_id, name, description)
        values (gen_random_uuid(), :oid, :name, :desc)
        returning id, org_id, name, description, created_at
    """), {"oid": org_id, "name": body.name, "desc": body.description}).mappings().first()
    db.commit()
    return {"ok": True, "project": proj}

@router.get("/{org_id}/projects", summary="List projects in org (any member)")
def list_org_projects(org_id: str, db: Session = Depends(get_db), me = Depends(get_current_user)):
    if not _is_org_role(db, me["id"], org_id, ["owner","admin","member"]):
        raise HTTPException(403, "Forbidden: not a member of org")
    rows = db.execute(text("""
        select id, org_id, name, description, created_at
        from projects
        where org_id=:oid
        order by created_at desc
    """), {"oid": org_id}).mappings().all()
    return {"ok": True, "items": rows}

@router.get("/projects", summary="List projects across my orgs")
def list_all_projects(db: Session = Depends(get_db), me = Depends(get_current_user)):
    rows = db.execute(text("""
        select p.id, p.org_id, p.name, p.description, p.created_at
        from projects p
        join org_members m on m.org_id=p.org_id
        where m.user_id=:uid
        order by p.created_at desc
    """), {"uid": me["id"]}).mappings().all()
    return {"ok": True, "items": rows}
