"""
Server ingestion normalization utilities.

Goal:
- Make ingested server records cleaner and more predictable.
- Avoid blowing up analysis / diagrams / TCO when values are null / weird.
- Standardize OS, environment, and role fields.

This module is intentionally dependency-light and defensive:
- No FastAPI, no SQLAlchemy, no Pydantic imports.
- Takes plain dicts and returns cleaned dicts + a list of warning strings.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple, Optional
import logging
import re

logger = logging.getLogger(__name__)


# ---- OS Normalization Maps -------------------------------------------------

WINDOWS_KEYWORDS = [
    "win", "windows", "w2k", "w2000", "windows server"
]

LINUX_KEYWORDS = [
    "linux", "rhel", "red hat", "redhat", "ubuntu", "centos",
    "suse", "sles", "oracle linux", "amazon linux", "debian"
]

AIX_KEYWORDS = ["aix"]
SOLARIS_KEYWORDS = ["solaris", "sunos"]
HPUX_KEYWORDS = ["hpux", "hp-ux"]


# ---- Environment Normalization Maps ----------------------------------------

ENV_MAP = {
    # prod
    "prod": "prod",
    "production": "prod",
    "prd": "prod",
    "live": "prod",

    # non-prod
    "nonprod": "nonprod",
    "non-prod": "nonprod",
    "non production": "nonprod",

    # dev
    "dev": "dev",
    "development": "dev",

    # test / qa / uat / stage
    "test": "test",
    "tst": "test",
    "qa": "qa",
    "quality assurance": "qa",
    "uat": "uat",
    "user acceptance": "uat",
    "stage": "staging",
    "staging": "staging",

    # dr / backup
    "dr": "dr",
    "disaster recovery": "dr",
    "backup": "dr",
    "bcp": "dr",

    # sandbox / lab
    "sandbox": "sandbox",
    "lab": "sandbox",
    "training": "sandbox",
}


# ---- Role Normalization Maps -----------------------------------------------

ROLE_MAP = {
    # app
    "app": "app",
    "application": "app",
    "middleware": "app",
    "weblogic": "app",
    "jboss": "app",
    "was": "app",
    "websphere": "app",
    "tomcat": "app",
    "glassfish": "app",

    # web
    "web": "web",
    "webserver": "web",
    "web server": "web",
    "apache": "web",
    "httpd": "web",
    "nginx": "web",
    "iis": "web",

    # db
    "db": "db",
    "database": "db",
    "sql": "db",
    "mssql": "db",
    "sql server": "db",
    "mysql": "db",
    "postgres": "db",
    "postgresql": "db",
    "oracle": "db",
    "db2": "db",
    "sybase": "db",
    "rds": "db",

    # file / storage
    "file": "file",
    "fileserver": "file",
    "file server": "file",
    "nas": "file",
    "cifs": "file",
    "smb": "file",

    # domain controllers
    "dc": "domain_controller",
    "domain controller": "domain_controller",
    "active directory": "domain_controller",
    "ad": "domain_controller",

    # batch / job
    "batch": "batch",
    "scheduler": "batch",
    "autosys": "batch",
    "control-m": "batch",
}


# ---- Helper parsing utilities ----------------------------------------------

_DIGITS_RE = re.compile(r"(-?\d+(\.\d+)?)")


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _extract_number(value: Any) -> Optional[float]:
    """
    Try to extract a numeric value from strings like:
      "4", "4 vCPU", "16 GB", "0.5", "0.5 TB", etc.
    Returns float or None.
    """
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    match = _DIGITS_RE.search(text)
    if not match:
        return None

    try:
        return float(match.group(1))
    except ValueError:
        return None


def _normalize_hostname(hostname: Any) -> Optional[str]:
    text = _safe_str(hostname)
    if not text:
        return None

    # Very conservative: lower-case, strip spaces.
    # (If you want to strip domain suffixes later, do it here.)
    text = text.strip()
    return text or None


# ---- OS normalization -------------------------------------------------------

def _detect_os_family_and_name(raw_os: Any) -> Tuple[str, str]:
    """
    Given a raw OS string, try to infer:
    - os_family: windows | linux | aix | solaris | hpux | unknown
    - os_name: a cleaner, human-friendly label like "Windows Server 2012 R2"

    If we cannot figure it out, we return ("unknown", raw_trimmed) or ("unknown", "").
    """
    raw = _safe_str(raw_os)
    if not raw:
        return "unknown", ""

    lower = raw.lower()

    # Windows
    if any(k in lower for k in WINDOWS_KEYWORDS):
        # Very basic version detection just on year markers
        if "2012" in lower:
            if "r2" in lower:
                return "windows", "Windows Server 2012 R2"
            return "windows", "Windows Server 2012"
        if "2016" in lower:
            return "windows", "Windows Server 2016"
        if "2019" in lower:
            return "windows", "Windows Server 2019"
        if "2022" in lower:
            return "windows", "Windows Server 2022"
        if "2008" in lower:
            return "windows", "Windows Server 2008"
        if "2003" in lower:
            return "windows", "Windows Server 2003"
        # Fallback
        return "windows", "Windows Server (unspecified)"

    # Linux
    if any(k in lower for k in LINUX_KEYWORDS):
        # Try to tag major distro
        if "red hat" in lower or "redhat" in lower or "rhel" in lower:
            return "linux", "Red Hat Enterprise Linux"
        if "ubuntu" in lower:
            return "linux", "Ubuntu Linux"
        if "centos" in lower:
            return "linux", "CentOS Linux"
        if "suse" in lower or "sles" in lower:
            return "linux", "SUSE Linux"
        if "oracle" in lower:
            return "linux", "Oracle Linux"
        if "amazon" in lower:
            return "linux", "Amazon Linux"
        if "debian" in lower:
            return "linux", "Debian Linux"
        return "linux", "Linux (unspecified)"

    # AIX
    if any(k in lower for k in AIX_KEYWORDS):
        return "aix", "IBM AIX"

    # Solaris
    if any(k in lower for k in SOLARIS_KEYWORDS):
        return "solaris", "Oracle Solaris"

    # HP-UX
    if any(k in lower for k in HPUX_KEYWORDS):
        return "hpux", "HP-UX"

    # Unknown
    return "unknown", raw.strip()


# ---- Environment normalization ---------------------------------------------

def _normalize_environment(env: Any) -> Tuple[str, Optional[str]]:
    """
    Normalize environment to one of:
      prod, nonprod, dev, test, qa, uat, staging, dr, sandbox, unknown

    Returns (normalized_env, warning_message_or_None).
    """
    raw = _safe_str(env)
    if not raw:
        return "unknown", "environment missing"

    lower = raw.lower().strip()

    # Try direct match first
    if lower in ENV_MAP:
        return ENV_MAP[lower], None

    # Try some heuristic matching:
    # "prod1", "prod-east", etc.
    for key, normalized in ENV_MAP.items():
        if key in lower:
            return normalized, None

    # Nothing matched
    return "unknown", f"unrecognized environment value '{raw}'"


# ---- Role normalization -----------------------------------------------------

def _normalize_role(role: Any) -> Tuple[str, Optional[str]]:
    """
    Normalize role to one of:
      app, web, db, file, domain_controller, batch, unknown

    Returns (normalized_role, warning_message_or_None).
    """
    raw = _safe_str(role)
    if not raw:
        return "unknown", "role missing"

    lower = raw.lower().strip()

    # Try direct match
    if lower in ROLE_MAP:
        return ROLE_MAP[lower], None

    # Try heuristic: any known key appears in the string
    for key, normalized in ROLE_MAP.items():
        if key in lower:
            return normalized, None

    # Nothing matched
    return "unknown", f"unrecognized role value '{raw}'"


# ---- Public entrypoint ------------------------------------------------------

def normalize_server_record(
    record: Dict[str, Any]
) -> Tuple[Dict[str, Any], List[str]]:
    """
    Normalize a single server record dict.

    This function:
    - Does NOT mutate the input dict; it returns a shallow copy.
    - Normalizes:
        - hostname
        - os_family / os_name (using `os_name` or `os` fields if present)
        - environment
        - role
        - cpu_count (int-ish)
        - memory_gb (float-ish)
        - total_storage_gb (float-ish)
    - Returns (cleaned_record, warnings_list).

    It is intentionally tolerant:
    - If fields are missing, it leaves them as-is or sets them to None.
    - It NEVER raises exceptions for bad data.
    """

    cleaned: Dict[str, Any] = dict(record)  # shallow copy
    warnings: List[str] = []

    # Hostname
    hostname_val = (
        record.get("hostname")
        or record.get("host_name")
        or record.get("server_name")
    )
    normalized_hostname = _normalize_hostname(hostname_val)
    cleaned["hostname"] = normalized_hostname
    if hostname_val and not normalized_hostname:
        warnings.append(f"hostname '{hostname_val}' could not be normalized")
    if not hostname_val:
        warnings.append("hostname missing")

    # OS
    raw_os = record.get("os_name") or record.get("os") or record.get("operating_system")
    os_family, os_name = _detect_os_family_and_name(raw_os)
    cleaned["os_family"] = os_family
    cleaned["os_name"] = os_name
    if os_family == "unknown":
        if raw_os:
            warnings.append(f"unrecognized OS value '{raw_os}'")
        else:
            warnings.append("OS value missing")

    # Environment
    env_val = record.get("environment") or record.get("env")
    normalized_env, env_warning = _normalize_environment(env_val)
    cleaned["environment"] = normalized_env
    if env_warning:
        warnings.append(env_warning)

    # Role
    role_val = record.get("role") or record.get("server_role")
    normalized_role, role_warning = _normalize_role(role_val)
    cleaned["role"] = normalized_role
    if role_warning:
        warnings.append(role_warning)

    # CPU count
    cpu_val = record.get("cpu_count") or record.get("cpus") or record.get("vcpus")
    cpu_num = _extract_number(cpu_val)
    if cpu_num is not None:
        cleaned["cpu_count"] = int(round(cpu_num))
    else:
        # Only warn if they gave us *something* bad
        if cpu_val not in (None, ""):
            warnings.append(f"could not parse cpu_count from '{cpu_val}'")

    # Memory (GB)
    mem_val = record.get("memory_gb") or record.get("ram_gb") or record.get("memory")
    mem_num = _extract_number(mem_val)
    if mem_num is not None:
        cleaned["memory_gb"] = round(mem_num, 2)
    else:
        if mem_val not in (None, ""):
            warnings.append(f"could not parse memory_gb from '{mem_val}'")

    # Storage (total GB)
    storage_val = (
        record.get("total_storage_gb")
        or record.get("storage_gb")
        or record.get("disk_gb")
        or record.get("storage")
    )
    storage_num = _extract_number(storage_val)
    if storage_num is not None:
        cleaned["total_storage_gb"] = round(storage_num, 2)
    else:
        if storage_val not in (None, ""):
            warnings.append(f"could not parse total_storage_gb from '{storage_val}'")

    # Log warnings here so they show up in backend logs, but still return them
    if warnings:
        logger.info(
            "Server normalization warnings for hostname=%s: %s",
            cleaned.get("hostname"),
            "; ".join(warnings),
        )

    return cleaned, warnings
