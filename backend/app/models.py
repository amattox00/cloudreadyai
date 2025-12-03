from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Float,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from .db import Base


# ============================================================
# USERS / AUTH / ORGANIZATION MODELS (Existing)
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("roles.id"))


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    key_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================
# INVENTORY / INGESTION MODELS (Phase B2)
# ============================================================

class Server(Base):
    __tablename__ = "inventory_servers"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True, nullable=False)

    hostname = Column(String, index=True)
    environment = Column(String, index=True)
    os_name = Column(String)
    cpu_count = Column(Integer)
    memory_gb = Column(Float)
    cluster = Column(String)
    ip_address = Column(String)


class Application(Base):
    __tablename__ = "inventory_apps"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True, nullable=False)

    application_name = Column(String, index=True)
    criticality = Column(String)
    environment = Column(String, index=True)
    business_unit = Column(String)
    owner = Column(String)
    hostname = Column(String, index=True)
    notes = Column(String)


class StorageVolume(Base):
    __tablename__ = "inventory_storage"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True, nullable=False)

    array = Column(String, index=True)
    pool = Column(String, index=True)
    lun_id = Column(String, index=True)
    size_gb = Column(Float)
    provisioning = Column(String)
    raid = Column(String)
    used_percent = Column(Float)


class NetworkDevice(Base):
    __tablename__ = "inventory_networks"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True, nullable=False)

    device_name = Column(String, index=True)
    device_type = Column(String)
    role = Column(String)
    mgmt_ip = Column(String, index=True)
    site = Column(String)
    vlan = Column(String)
    subnet = Column(String)


class VcenterVM(Base):
    __tablename__ = "inventory_vms"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True, nullable=False)

    vm_name = Column(String, index=True)
    cluster = Column(String, index=True)
    power_state = Column(String)
    cpu_count = Column(Float)
    memory_mb = Column(Float)
    guest_os = Column(String)
    ip_addresses = Column(String)
