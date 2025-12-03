"""add analysis tables

Revision ID: d426ff6be5d9
Revises: d0b6b63c9ca3
Create Date: 2025-11-28 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d426ff6be5d9"
down_revision = "d0b6b63c9ca3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # analysis_runs
    # ------------------------------------------------------------------
    op.create_table(
        "analysis_runs",
        sa.Column("run_id", sa.String(), primary_key=True),
        sa.Column("status", sa.String(), nullable=False, server_default="PENDING"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("summary", sa.JSON(), nullable=True),
    )
    op.create_index("ix_analysis_runs_run_id", "analysis_runs", ["run_id"], unique=False)

    # ------------------------------------------------------------------
    # server_profiles
    # ------------------------------------------------------------------
    op.create_table(
        "server_profiles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("run_id", sa.String, nullable=False),
        sa.Column("server_id", sa.String, nullable=False),
        sa.Column("role", sa.String, nullable=True),
        sa.Column("cpu_usage", sa.Float, nullable=True),
        sa.Column("ram_usage", sa.Float, nullable=True),
        sa.Column("storage_usage", sa.Float, nullable=True),
        sa.Column("os", sa.String, nullable=True),
        sa.Column("environment", sa.String, nullable=True),
    )
    op.create_index("ix_server_profiles_id", "server_profiles", ["id"], unique=False)
    op.create_index("ix_server_profiles_run_id", "server_profiles", ["run_id"], unique=False)
    op.create_index("ix_server_profiles_server_id", "server_profiles", ["server_id"], unique=False)

    # ------------------------------------------------------------------
    # app_profiles
    # ------------------------------------------------------------------
    op.create_table(
        "app_profiles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("run_id", sa.String, nullable=False),
        sa.Column("server_id", sa.String, nullable=False),
        sa.Column("app_name", sa.String, nullable=False),
        sa.Column("dependency_count", sa.Integer, nullable=False, server_default="0"),
    )
    op.create_index("ix_app_profiles_id", "app_profiles", ["id"], unique=False)
    op.create_index("ix_app_profiles_run_id", "app_profiles", ["run_id"], unique=False)
    op.create_index("ix_app_profiles_server_id", "app_profiles", ["server_id"], unique=False)

    # ------------------------------------------------------------------
    # dependency_links
    # ------------------------------------------------------------------
    op.create_table(
        "dependency_links",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("run_id", sa.String, nullable=False),
        sa.Column("source_server", sa.String, nullable=False),
        sa.Column("target_server", sa.String, nullable=False),
        sa.Column("protocol", sa.String, nullable=True),
        sa.Column("port", sa.Integer, nullable=True),
    )
    op.create_index("ix_dependency_links_id", "dependency_links", ["id"], unique=False)
    op.create_index("ix_dependency_links_run_id", "dependency_links", ["run_id"], unique=False)

    # ------------------------------------------------------------------
    # rightsizing_results
    # ------------------------------------------------------------------
    op.create_table(
        "rightsizing_results",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("run_id", sa.String, nullable=False),
        sa.Column("server_id", sa.String, nullable=False),
        sa.Column("current_vcpu", sa.Integer, nullable=True),
        sa.Column("recommended_vcpu", sa.Integer, nullable=True),
        sa.Column("current_ram", sa.Float, nullable=True),
        sa.Column("recommended_ram", sa.Float, nullable=True),
        sa.Column("current_storage", sa.Float, nullable=True),
        sa.Column("recommended_storage", sa.Float, nullable=True),
    )
    op.create_index("ix_rightsizing_results_id", "rightsizing_results", ["id"], unique=False)
    op.create_index("ix_rightsizing_results_run_id", "rightsizing_results", ["run_id"], unique=False)

    # ------------------------------------------------------------------
    # placement_results
    # ------------------------------------------------------------------
    op.create_table(
        "placement_results",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("run_id", sa.String, nullable=False),
        sa.Column("server_id", sa.String, nullable=False),
        sa.Column("recommended_cloud", sa.String, nullable=True),
        sa.Column("instance_type", sa.String, nullable=True),
        sa.Column("monthly_cost", sa.Float, nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
    )
    op.create_index("ix_placement_results_id", "placement_results", ["id"], unique=False)
    op.create_index("ix_placement_results_run_id", "placement_results", ["run_id"], unique=False)

    # ------------------------------------------------------------------
    # risk_flags
    # ------------------------------------------------------------------
    op.create_table(
        "risk_flags",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("run_id", sa.String, nullable=False),
        sa.Column("server_id", sa.String, nullable=False),
        sa.Column("risk_type", sa.String, nullable=False),
        sa.Column("severity", sa.String, nullable=True),
        sa.Column("message", sa.String, nullable=True),
    )
    op.create_index("ix_risk_flags_id", "risk_flags", ["id"], unique=False)
    op.create_index("ix_risk_flags_run_id", "risk_flags", ["run_id"], unique=False)


def downgrade() -> None:
    # Drop in reverse order of creation
    op.drop_index("ix_risk_flags_run_id", table_name="risk_flags")
    op.drop_index("ix_risk_flags_id", table_name="risk_flags")
    op.drop_table("risk_flags")

    op.drop_index("ix_placement_results_run_id", table_name="placement_results")
    op.drop_index("ix_placement_results_id", table_name="placement_results")
    op.drop_table("placement_results")

    op.drop_index("ix_rightsizing_results_run_id", table_name="rightsizing_results")
    op.drop_index("ix_rightsizing_results_id", table_name="rightsizing_results")
    op.drop_table("rightsizing_results")

    op.drop_index("ix_dependency_links_run_id", table_name="dependency_links")
    op.drop_index("ix_dependency_links_id", table_name="dependency_links")
    op.drop_table("dependency_links")

    op.drop_index("ix_app_profiles_server_id", table_name="app_profiles")
    op.drop_index("ix_app_profiles_run_id", table_name="app_profiles")
    op.drop_index("ix_app_profiles_id", table_name="app_profiles")
    op.drop_table("app_profiles")

    op.drop_index("ix_server_profiles_server_id", table_name="server_profiles")
    op.drop_index("ix_server_profiles_run_id", table_name="server_profiles")
    op.drop_index("ix_server_profiles_id", table_name="server_profiles")
    op.drop_table("server_profiles")

    op.drop_index("ix_analysis_runs_run_id", table_name="analysis_runs")
    op.drop_table("analysis_runs")
