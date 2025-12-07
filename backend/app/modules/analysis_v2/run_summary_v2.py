from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.ingestion_run_v2 import IngestionRunV2
from app.models.inventory_server_v2 import InventoryServerV2
from app.models.inventory_storage_v2 import InventoryStorageV2
from app.models.inventory_database_v2 import InventoryDatabaseV2
from app.models.inventory_application_v2 import InventoryApplicationV2
from app.models.inventory_dependency_v2 import InventoryDependencyV2
from app.models.inventory_network_v2 import InventoryNetworkV2
from app.models.inventory_os_software_v2 import InventoryOsSoftwareV2
from app.models.inventory_business_v2 import InventoryBusinessV2
from app.models.inventory_utilization_v2 import InventoryUtilizationV2
from app.models.inventory_license_v2 import InventoryLicenseV2


# ---------------------------
# Core summary models
# ---------------------------


class RunTotals(BaseModel):
    assets_ingested: int


class RunSlices(BaseModel):
    servers: int = 0
    storage: int = 0
    databases: int = 0
    applications: int = 0
    dependencies: int = 0
    networks: int = 0
    business: int = 0
    licenses: int = 0
    utilization: int = 0
    os_software: int = 0


class RScoreDimension(BaseModel):
    name: str
    score: int
    weight: float
    rationale: str


class RScore(BaseModel):
    overall_score: int
    overall_grade: str
    dimensions: List[RScoreDimension]


class RunSummaryV2(BaseModel):
    run_id: str
    status: str
    name: Optional[str]
    created_at: Optional[datetime]
    totals: RunTotals
    slices: RunSlices
    r_score: RScore
    flags: List[str] = []


# ---------------------------
# R-Score helpers
# ---------------------------


def _grade_from_score(score: int) -> str:
    """
    Map numeric score (0-100) to a letter grade.
    Calibrated to match the examples you've already seen:
      - 12 -> F
      - 50 -> D
      - 84 -> B
    """
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 65:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def compute_r_score_v2(slices: RunSlices) -> RScore:
    """
    Very lightweight R-Score v2:
      - Data Coverage: how many slices are populated (out of 10)
      - Dependency Clarity: dependencies per application
      - Utilization Insight: utilization points per server
    """

    # --- Data Coverage (how many slices have at least one record) ---
    slice_values = slices.model_dump()
    non_zero_slices = sum(1 for v in slice_values.values() if v > 0)
    coverage_ratio = non_zero_slices / 10.0
    data_coverage_score = int(round(coverage_ratio * 100))

    data_coverage_dim = RScoreDimension(
        name="Data Coverage",
        score=data_coverage_score,
        weight=0.4,
        rationale=f"{non_zero_slices} of 10 data slices have at least one record for this run.",
    )

    # --- Dependency Clarity (dependencies relative to applications) ---
    if slices.applications > 0:
        dep_ratio = min(1.0, slices.dependencies / float(slices.applications))
        dependency_clarity_score = int(round(dep_ratio * 100))
    else:
        dependency_clarity_score = 0

    dependency_clarity_dim = RScoreDimension(
        name="Dependency Clarity",
        score=dependency_clarity_score,
        weight=0.3,
        rationale=(
            "Higher scores indicate more explicit application dependencies "
            "relative to the number of applications."
        ),
    )

    # --- Utilization Insight (utilization datapoints per server) ---
    if slices.servers > 0:
        util_ratio = min(1.0, slices.utilization / float(slices.servers))
        utilization_insight_score = int(round(util_ratio * 100))
    else:
        utilization_insight_score = 0

    utilization_insight_dim = RScoreDimension(
        name="Utilization Insight",
        score=utilization_insight_score,
        weight=0.3,
        rationale=(
            "Higher scores indicate more utilization datapoints "
            "relative to the number of servers discovered."
        ),
    )

    # --- Overall score (weighted) ---
    overall = (
        data_coverage_dim.score * data_coverage_dim.weight
        + dependency_clarity_dim.score * dependency_clarity_dim.weight
        + utilization_insight_dim.score * utilization_insight_dim.weight
    )
    overall_score = int(round(overall))
    overall_grade = _grade_from_score(overall_score)

    return RScore(
        overall_score=overall_score,
        overall_grade=overall_grade,
        dimensions=[
            data_coverage_dim,
            dependency_clarity_dim,
            utilization_insight_dim,
        ],
    )


# ---------------------------
# Flags helpers
# ---------------------------


def compute_flags_v2(slices: RunSlices) -> List[str]:
    """
    Produce a small set of human-readable flags that describe
    data quality / coverage concerns for this run.
    """
    flags: List[str] = []

    # 1) Servers but no app / business context
    if slices.servers > 0 and slices.applications == 0 and slices.business == 0:
        flags.append("SERVERS_WITHOUT_APP_OR_BUSINESS_CONTEXT")

    # 2) Servers but no utilization
    if slices.servers > 0 and slices.utilization == 0:
        flags.append("NO_UTILIZATION_DATA")

    # 3) Apps but no dependencies
    if slices.applications > 0 and slices.dependencies == 0:
        flags.append("NO_DEPENDENCIES_PROVIDED")

    # 4) Infra/deps but no network topology
    if (slices.servers > 0 or slices.dependencies > 0) and slices.networks == 0:
        flags.append("NO_NETWORK_TOPOLOGY")

    # 5) Very limited overall coverage (few slices populated)
    non_zero_slices = sum(1 for v in slices.model_dump().values() if v > 0)
    if non_zero_slices <= 3:
        flags.append("LIMITED_DATA_COVERAGE")

    return flags


# ---------------------------
# Main summary function
# ---------------------------


def summarize_run_v2(run_id: str, db: Session) -> RunSummaryV2:
    """
    Roll up all v2 ingestion slices + basic R-Score + flags
    for a single run_id.
    """

    # --- Ingestion run row (if present) ---
    run_row: Optional[IngestionRunV2] = (
        db.query(IngestionRunV2)
        .filter(IngestionRunV2.run_id == run_id)
        .one_or_none()
    )

    status = run_row.status if run_row and getattr(run_row, "status", None) else "created"
    name = getattr(run_row, "name", None) if run_row is not None else None
    created_at = getattr(run_row, "created_at", None) if run_row is not None else None

    # --- Slice counts ---
    servers_count = db.query(func.count(InventoryServerV2.id)).filter(
        InventoryServerV2.run_id == run_id
    ).scalar() or 0

    storage_count = db.query(func.count(InventoryStorageV2.id)).filter(
        InventoryStorageV2.run_id == run_id
    ).scalar() or 0

    databases_count = db.query(func.count(InventoryDatabaseV2.id)).filter(
        InventoryDatabaseV2.run_id == run_id
    ).scalar() or 0

    applications_count = db.query(func.count(InventoryApplicationV2.id)).filter(
        InventoryApplicationV2.run_id == run_id
    ).scalar() or 0

    dependencies_count = db.query(func.count(InventoryDependencyV2.id)).filter(
        InventoryDependencyV2.run_id == run_id
    ).scalar() or 0

    networks_count = db.query(func.count(InventoryNetworkV2.id)).filter(
        InventoryNetworkV2.run_id == run_id
    ).scalar() or 0

    business_count = db.query(func.count(InventoryBusinessV2.id)).filter(
        InventoryBusinessV2.run_id == run_id
    ).scalar() or 0

    licenses_count = db.query(func.count(InventoryLicenseV2.id)).filter(
        InventoryLicenseV2.run_id == run_id
    ).scalar() or 0

    utilization_count = db.query(func.count(InventoryUtilizationV2.id)).filter(
        InventoryUtilizationV2.run_id == run_id
    ).scalar() or 0

    os_software_count = db.query(func.count(InventoryOsSoftwareV2.id)).filter(
        InventoryOsSoftwareV2.run_id == run_id
    ).scalar() or 0

    # --- Build slices & totals ---
    slices = RunSlices(
        servers=servers_count,
        storage=storage_count,
        databases=databases_count,
        applications=applications_count,
        dependencies=dependencies_count,
        networks=networks_count,
        business=business_count,
        licenses=licenses_count,
        utilization=utilization_count,
        os_software=os_software_count,
    )

    assets_ingested = (
        servers_count
        + storage_count
        + databases_count
        + applications_count
        + dependencies_count
        + networks_count
        + business_count
        + licenses_count
        + utilization_count
        + os_software_count
    )

    # --- Compute R-Score + flags ---
    r_score = compute_r_score_v2(slices)
    flags = compute_flags_v2(slices)

    # --- Final summary DTO ---
    return RunSummaryV2(
        run_id=run_id,
        status=status,
        name=name,
        created_at=created_at,
        totals=RunTotals(assets_ingested=assets_ingested),
        slices=slices,
        r_score=r_score,
        flags=flags,
    )
