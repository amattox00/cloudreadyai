from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
import os
import json
import csv
from datetime import datetime

from sqlalchemy import create_engine
import psycopg2
from psycopg2.extras import execute_values

# -----------------------------
# CONFIGURATION
# -----------------------------

INGESTION_ROOT = "/home/ec2-user/cloudreadyai/backend/data/ingestion"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/cloudready",
)

engine = create_engine(DATABASE_URL, future=True)

router = APIRouter(prefix="/v1/runs", tags=["runs"])


# -----------------------------
# UTILITY FUNCTIONS
# -----------------------------

def ensure_run_dir(run_id: str) -> str:
    """Ensure ingestion run directory exists."""
    path = os.path.join(INGESTION_ROOT, run_id)
    os.makedirs(path, exist_ok=True)
    return path


def load_status(run_id: str):
    """Load on-disk status.json for run."""
    status_path = os.path.join(INGESTION_ROOT, run_id, "status.json")
    if os.path.exists(status_path):
        with open(status_path, "r") as f:
            return json.load(f)
    return {"run_id": run_id, "state": "empty", "files": []}


def save_status(run_id: str, state: str, files: Optional[List[str]] = None):
    """Save status.json for a run."""
    if files is None:
        files = []

    run_dir = ensure_run_dir(run_id)
    status_path = os.path.join(run_dir, "status.json")

    data = {
        "run_id": run_id,
        "state": state,
        "files": files,
        "updated_at": datetime.utcnow().isoformat(),
    }

    with open(status_path, "w") as f:
        json.dump(data, f, indent=2)

    return data


# -----------------------------
# API MODELS
# -----------------------------

class CreateRunResponse(BaseModel):
    run_id: str
    state: str = "created"


class UploadResponse(BaseModel):
    run_id: str
    filename: str
    state: str


class RunStatusResponse(BaseModel):
    run_id: str
    state: str
    files: List[str]


class ServersPreviewResponse(BaseModel):
    run_id: str
    file: str
    rows: List[dict]


class ServersIngestResponse(BaseModel):
    run_id: str
    file: str
    inserted: int
    state: str

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
import os
import json
import csv
from datetime import datetime

from sqlalchemy import create_engine, text

# -----------------------------
# Configuration
# -----------------------------

# Where uploaded ingestion files live on disk
INGESTION_ROOT = "/home/ec2-user/cloudreadyai/backend/data/ingestion"

# Database URL – environment variable or default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/cloudready",
)

engine = create_engine(DATABASE_URL, future=True)

router = APIRouter(prefix="/v1/runs", tags=["runs"])


# -----------------------------
# Utility functions
# -----------------------------

def ensure_run_dir(run_id: str) -> str:
    """Ensure directory exists for a run."""
    path = os.path.join(INGESTION_ROOT, run_id)
    os.makedirs(path, exist_ok=True)
    return path


def load_status(run_id: str):
    """Load status.json for local tracking."""
    status_path = os.path.join(INGESTION_ROOT, run_id, "status.json")
    if os.path.exists(status_path):
        with open(status_path, "r") as f:
            return json.load(f)
    return {"run_id": run_id, "state": "empty", "files": []}


def save_status(run_id: str, state: str, files: Optional[List[str]] = None):
    """Write status.json."""
    if files is None:
        files = []

    run_dir = ensure_run_dir(run_id)
    status_path = os.path.join(run_dir, "status.json")

    data = {
        "run_id": run_id,
        "state": state,
        "files": files,
        "updated_at": datetime.utcnow().isoformat(),
    }

    with open(status_path, "w") as f:
        json.dump(data, f, indent=2)

    return data


# -----------------------------
# API MODELS
# -----------------------------

class CreateRunResponse(BaseModel):
    run_id: str
    state: str = "created"


class UploadResponse(BaseModel):
    run_id: str
    filename: str
    state: str


class RunStatusResponse(BaseModel):
    run_id: str
    state: str
    files: List[str]


class ServersPreviewResponse(BaseModel):
    run_id: str
    file: str
    rows: List[dict]


class ServersIngestResponse(BaseModel):
    run_id: str
    file: str
    inserted: int
    state: str


# -----------------------------
# ROUTES
# -----------------------------

@router.post("", response_model=CreateRunResponse)
def create_run():
    """
    Create a new ingestion run.
    Inserts into ingestion_runs table (status column, NOT state).
    Also prepares local folder + status.json for file uploads.
    """

    run_id = f"run-{uuid.uuid4().hex[:8]}"

    # Insert into DB
    try:
        import psycopg2

        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            database="cloudready"
        )
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO ingestion_runs (run_id, status)
            VALUES (%s, %s)
        """, (run_id, "created"))

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create run in DB: {e}"
        )

    # Create local run directory & status.json
    ensure_run_dir(run_id)
    save_status(run_id, "created", [])

    return CreateRunResponse(run_id=run_id, state="created")


# -----------------------------------
# Upload File
# -----------------------------------

@router.post("/{run_id}/upload", response_model=UploadResponse)
async def upload_file(run_id: str, file: UploadFile = File(...)):
    """Upload CSV/JSON file for an ingestion run."""

    # Validate run directory
    run_dir = ensure_run_dir(run_id)

    # Write file
    dest_path = os.path.join(run_dir, file.filename)
    with open(dest_path, "wb") as f:
        f.write(await file.read())

    # Update status.json
    status = load_status(run_id)
    files = status.get("files", [])
    if file.filename not in files:
        files.append(file.filename)

    save_status(run_id, "uploaded", files)

    return UploadResponse(
        run_id=run_id,
        filename=file.filename,
        state="uploaded"
    )


# -----------------------------------
# Run Status
# -----------------------------------

@router.get("/{run_id}/status", response_model=RunStatusResponse)
def run_status(run_id: str):
    """Return ingestion run status."""
    status = load_status(run_id)
    return RunStatusResponse(**status)


# -----------------------------------
# Preview Server CSV
# -----------------------------------

@router.get("/{run_id}/preview/servers", response_model=ServersPreviewResponse)
def preview_servers(run_id: str, limit: int = 100):
    """Preview first 100 rows of server inventory."""

    run_dir = ensure_run_dir(run_id)
    candidates = [f for f in os.listdir(run_dir) if f.endswith(".csv")]

    if not candidates:
        raise HTTPException(status_code=400, detail="No CSV files found for this run.")

    # Prefer file with "server" in name
    servers_file = next((f for f in candidates if "server" in f.lower()), candidates[0])
    csv_path = os.path.join(run_dir, servers_file)

    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Servers CSV file not found.")

    rows = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            if idx >= limit:
                break

            rows.append({
                "hostname": row.get("hostname"),
                "cpu_cores": int(row.get("cpu_cores") or 0),
                "ram_gb": float(row.get("ram_gb") or 0.0),
                "environment": row.get("environment"),
            })

    return ServersPreviewResponse(
        run_id=run_id,
        file=servers_file,
        rows=rows
    )


# -----------------------------------
# Ingest servers into DB
# -----------------------------------

@router.post("/{run_id}/ingest/servers", response_model=ServersIngestResponse)
def ingest_servers(run_id: str):
    """Insert parsed server rows into servers table."""

    import psycopg2
    from psycopg2.extras import execute_values

    status = load_status(run_id)
    files = status.get("files", [])
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded for this run.")

    # First uploaded file only
    file_name = files[0]
    run_dir = ensure_run_dir(run_id)
    path = os.path.join(run_dir, file_name)

    # Parse CSV
    rows = []
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        raise HTTPException(status_code=400, detail="CSV contains no rows.")

    insert_rows = []
    for r in rows:
        insert_rows.append(
            (
                f"srv-{uuid.uuid4().hex[:12]}",  # server_id
                run_id,
                r.get("hostname"),
                int(r.get("cpu_cores") or 0),
                float(r.get("ram_gb") or 0.0),
                r.get("environment"),
            )
        )

    # Insert into DB
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            database="cloudready"
        )
        cur = conn.cursor()

        sql = """
        INSERT INTO servers (server_id, run_id, hostname, cpu_cores, ram_gb, environment)
        VALUES %s
        """

        execute_values(cur, sql, insert_rows)

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to insert into servers table: {e}"
        )

    # Update run status
    save_status(run_id, "ingested_servers", files)

    return ServersIngestResponse(
        run_id=run_id,
        file=file_name,
        inserted=len(insert_rows),
        state="ingested_servers"
    )
