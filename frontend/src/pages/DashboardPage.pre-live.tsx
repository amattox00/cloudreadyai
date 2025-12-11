import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const RUNS_API_BASE = "/v1/run_registry";

type AssessmentStatus = "Not Started" | "In Progress" | "Completed" | "Error";

interface RunRecordApi {
  id: string;
  created_at: string;
  name: string;
  source: string;
  state: string;
  servers_ingested: number;
  storage_ingested: number;
  network_ingested: number;
}

interface AssessmentRow {
  id: string;
  name: string;
  client: string;
  environment: string;
  status: AssessmentStatus;
  lastUpdated: string;
}

const statusStyles: Record<AssessmentStatus, string> = {
  "Not Started": "bg-gray-200 text-gray-700",
  "In Progress": "bg-blue-200 text-blue-800",
  Completed: "bg-green-200 text-green-800",
  Error: "bg-red-200 text-red-800",
};

function mapStateToStatus(state: string): AssessmentStatus {
  switch (state) {
    case "created":
      return "Not Started";
    case "completed":
      return "Completed";
    case "error":
      return "Error";
    default:
      return "In Progress";
  }
}

export default function DashboardPage() {
  const navigate = useNavigate();

  const [runs, setRuns] = useState<RunRecordApi[]>([]);
  const [loadingRuns, setLoadingRuns] = useState<boolean>(true);
  const [runsError, setRunsError] = useState<string | null>(null);

  const [creatingRun, setCreatingRun] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const loadRuns = async () => {
      setLoadingRuns(true);
      setRunsError(null);
      try {
        const res = await fetch(RUNS_API_BASE);
        if (!res.ok) {
          if (res.status === 404) {
            // No runs yet is not really an error; treat as empty list
            if (!cancelled) {
              setRuns([]);
            }
            return;
          }
          throw new Error(`HTTP ${res.status}`);
        }

        const data: RunRecordApi[] = await res.json();
        if (!cancelled) {
          setRuns(data);
        }
      } catch (err: any) {
        console.error("Error loading runs for dashboard", err);
        if (!cancelled) {
          setRunsError(
            "Unable to load assessments for the dashboard. Some tiles may be incomplete."
          );
        }
      } finally {
        if (!cancelled) {
          setLoadingRuns(false);
        }
      }
    };

    loadRuns();

    return () => {
      cancelled = true;
    };
  }, []);

  const handleStartNewAssessment = async () => {
    if (creatingRun) return;
    setCreatingRun(true);
    setCreateError(null);

    try {
      const res = await fetch(RUNS_API_BASE, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: "New assessment",
          source: "Dashboard",
        }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data: RunRecordApi = await res.json();
      if (!data.id) {
        throw new Error("Backend did not return a run id.");
      }

      // Optimistically add to local runs list
      setRuns((prev) => [data, ...prev]);

      navigate(`/runs/${data.id}`);
    } catch (err) {
      console.error("Error creating run from Dashboard", err);
      setCreateError(
        "Unable to start a new assessment from the Dashboard. Please try again."
      );
    } finally {
      setCreatingRun(false);
    }
  };

  // Derived metrics
  const totalAssessments = runs.length;
  const activeAssessments = runs.filter(
    (r) => r.state !== "completed" && r.state !== "error"
  ).length;

  const totalServers = runs.reduce(
    (sum, r) => sum + (r.servers_ingested ?? 0),
    0
  );

  const primaryRun = runs[0] ?? null;

  const recentAssessments: AssessmentRow[] = runs
    .slice(0, 5)
    .map((r) => ({
      id: r.id,
      name: r.name || "Untitled assessment",
      client: r.source || "Unknown source",
      environment: "—", // will be wired to real env metadata later
      status: mapStateToStatus(r.state),
      lastUpdated: new Date(r.created_at).toLocaleString(),
    }));

  const serversSliceStatus =
    (primaryRun?.servers_ingested ?? 0) > 0 ? "Complete" : "Not Started";

  return (
    <div className="px-6 py-6 space-y-6">
      {/* Hero / Command center header */}
      <section className="border border-gray-200 rounded-xl overflow-hidden shadow-sm bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
        <div className="flex justify-between items-start px-6 py-5">
          <div>
            <div className="text-xs font-semibold tracking-wide uppercase opacity-80 mb-1">
              CLOUDREADYAI
            </div>
            <h1 className="text-2xl font-semibold">
              Your cloud migration command center
            </h1>
            <p className="text-sm text-blue-100 mt-2 max-w-2xl">
              Monitor assessments, ingestion, and cost modeling from a single
              workspace. Turn raw infrastructure data into migration-ready plans
              your clients can trust.
            </p>
          </div>

          <div className="flex flex-col items-end space-y-3">
            <div className="bg-white/10 rounded-lg px-4 py-3 text-xs leading-4 shadow-sm border border-white/20">
              <div className="font-semibold mb-1">Workspace snapshot</div>
              <div>Active assessments: {activeAssessments}</div>
              {/* These will be wired later once client/portfolio concepts exist */}
              <div>Total clients: 2 · Portfolios: 3</div>
              <div>Environment: dev</div>
            </div>

            <button
              onClick={handleStartNewAssessment}
              disabled={creatingRun}
              className={`px-4 py-2 rounded-md shadow text-sm font-medium ${
                creatingRun
                  ? "bg-blue-300 cursor-wait"
                  : "bg-white text-blue-700 hover:bg-blue-50"
              }`}
            >
              {creatingRun ? "Starting…" : "Start New Assessment"}
            </button>
            {createError && (
              <p className="text-xs text-red-200 max-w-xs text-right">
                {createError}
              </p>
            )}
          </div>
        </div>
      </section>

      {/* Top metric tiles */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Active assessments"
          value={activeAssessments}
          description="Currently in progress across your workspace."
        />
        <MetricCard
          title="Total assessments"
          value={totalAssessments}
          description="Historical and in-flight assessments."
          icon="folder"
        />
        <MetricCard
          title="Environment data collected"
          value={`${totalServers} servers, 0 apps`}
          description="Latest ingestion across all environments."
          icon="servers"
        />
        <MetricCard
          title="Cost snapshots"
          value={0}
          description="Generate from any completed assessment."
          icon="dollar"
        />
      </section>

      {/* Optional error message for runs */}
      {runsError && (
        <div className="border border-red-200 bg-red-50 text-red-700 rounded-md px-4 py-2 text-xs">
          {runsError}
        </div>
      )}

      {/* Engine health + Data readiness + Insights */}
      <section className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Left: Data readiness & pipeline stacked (2/3 width on xl) */}
        <div className="space-y-4 xl:col-span-2">
          {/* Engine health */}
          <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h2 className="text-sm font-medium text-gray-900">
                  Engine health
                </h2>
                <p className="text-xs text-gray-600">
                  Status of core CloudReadyAI engines powering ingestion,
                  analysis, diagrams, and reporting.
                </p>
              </div>
              <p className="text-xs text-gray-500">
                View details per assessment in the{" "}
                <span className="font-medium">Insights</span> and{" "}
                <span className="font-medium">Cost Modeling</span> workspaces.
              </p>
            </div>

            <div className="flex flex-wrap gap-2 text-xs">
              <EnginePill label="Ingestion engine" status="Healthy" color="ok" />
              <EnginePill
                label="Analysis engine"
                status="Waiting on data"
                color="warn"
              />
              <EnginePill
                label="Cost & TCO engine"
                status="Partial"
                color="partial"
              />
              <EnginePill
                label="Diagrams engine"
                status="Planned"
                color="planned"
              />
              <EnginePill
                label="Reporting engine"
                status="Planned"
                color="planned"
              />
            </div>
          </div>

          {/* Data readiness & coverage */}
          <div className="border border-gray-200 bg-white rounded-md shadow-sm">
            <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-medium text-gray-900">
                  Data Readiness & Coverage
                </h2>
                <p className="text-xs text-gray-600">
                  Completeness of your 10 ingestion slices across all active
                  assessments. Higher coverage unlocks better insights, diagrams,
                  and cost modeling.
                </p>
              </div>
              <div className="text-right text-xs text-gray-500">
                <div>
                  2 of 10 slices complete{" "}
                  <span className="text-gray-400">(20% coverage)</span>
                </div>
              </div>
            </div>

            <div className="px-4 py-3 border-b border-gray-100">
              <div className="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
                <div className="bg-emerald-500 h-1.5" style={{ width: "20%" }} />
              </div>
              <p className="mt-2 text-xs text-gray-600">
                Focus next on ingesting{" "}
                <span className="font-medium">
                  storage, databases, and applications
                </span>{" "}
                to unlock full analysis.
              </p>
            </div>

            {/* Slice table */}
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase tracking-wide">
                      Slice
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase tracking-wide">
                      Status
                    </th>
                    <th className="px-4 py-2 text-right text-xs font-medium text-gray-600 uppercase tracking-wide">
                      Items
                    </th>
                    <th className="px-4 py-2 text-right text-xs font-medium text-gray-600 uppercase tracking-wide">
                      Last updated
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <SliceRow
                    name="Servers"
                    status={serversSliceStatus}
                    items={primaryRun?.servers_ingested ?? 0}
                    lastUpdated={
                      primaryRun
                        ? new Date(
                            primaryRun.created_at
                          ).toLocaleDateString()
                        : "—"
                    }
                    highlight
                  />
                  <SliceRow
                    name="Storage volumes"
                    status="Not Started"
                    items={primaryRun?.storage_ingested ?? 0}
                    lastUpdated="—"
                  />
                  <SliceRow
                    name="Databases"
                    status="Not Started"
                    items={0}
                    lastUpdated="—"
                  />
                  <SliceRow
                    name="Applications"
                    status="Not Started"
                    items={0}
                    lastUpdated="—"
                  />
                  <SliceRow
                    name="Network devices"
                    status="Not Started"
                    items={primaryRun?.network_ingested ?? 0}
                    lastUpdated="—"
                  />
                  <SliceRow
                    name="Business metadata"
                    status="Partial"
                    items={0}
                    lastUpdated="Yesterday"
                  />
                  <SliceRow
                    name="Dependencies"
                    status="Not Started"
                    items={0}
                    lastUpdated="—"
                  />
                  <SliceRow
                    name="Performance metrics"
                    status="Not Started"
                    items={0}
                    lastUpdated="—"
                  />
                  <SliceRow
                    name="Cost & usage"
                    status="Not Started"
                    items={0}
                    lastUpdated="—"
                  />
                  <SliceRow
                    name="Security / compliance"
                    status="Not Started"
                    items={0}
                    lastUpdated="—"
                    isLast
                  />
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right: Migration insights snapshot */}
        <div className="space-y-4">
          <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4">
            <h2 className="text-sm font-medium text-gray-900 mb-1">
              Migration Insights Snapshot
            </h2>
            <p className="text-xs text-gray-600 mb-3">
              Early view of how workloads align to migration strategies. Values
              are illustrative until the Insights engine is fully wired.
            </p>

            <div className="grid grid-cols-3 gap-3 mb-4">
              <SnapshotTile label="Ready for rehost" value={48} />
              <SnapshotTile label="Ready for refactor" value={27} />
              <SnapshotTile label="Needs investigation" value={25} />
            </div>

            <div className="border border-dashed border-gray-300 rounded-md px-4 py-3">
              <h3 className="text-xs font-semibold text-gray-800 mb-2">
                Migration Strategy Preview
              </h3>
              <div className="flex items-center gap-3 mb-2 text-xs">
                <LegendDot className="bg-sky-500" />
                <span className="mr-1 font-medium">Rehost</span>
                <span className="text-gray-500">48 workloads</span>

                <LegendDot className="bg-emerald-500 ml-4" />
                <span className="mr-1 font-medium">Refactor</span>
                <span className="text-gray-500">27 workloads</span>

                <LegendDot className="bg-amber-400 ml-4" />
                <span className="mr-1 font-medium">Investigate</span>
                <span className="text-gray-500">25 workloads</span>
              </div>

              <div className="w-full bg-gray-100 rounded-full h-2 mb-2 overflow-hidden">
                <div className="flex h-2 w-full">
                  <div className="bg-sky-500" style={{ width: "48%" }} />
                  <div className="bg-emerald-500" style={{ width: "27%" }} />
                  <div className="bg-amber-400" style={{ width: "25%" }} />
                </div>
              </div>

              <p className="text-[11px] text-gray-500">
                Strategy mix based on discovered workloads. Drill into details
                in the{" "}
                <span className="font-medium text-gray-700">Insights</span>{" "}
                workspace as the engine comes online.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Bottom row: Recent assessments + Recent activity */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Recent assessments */}
        <div className="border border-gray-200 bg-white rounded-md shadow-sm">
          <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-medium text-gray-900">
                Recent assessments
              </h2>
              <p className="text-xs text-gray-600">
                Open an assessment to review ingestion details, insights, and
                reports.
              </p>
            </div>
            <p className="text-xs text-gray-500 hidden sm:block">
              Click any row to open
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase tracking-wide">
                    Assessment
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase tracking-wide">
                    Client
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase tracking-wide">
                    Environment
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase tracking-wide">
                    Status
                  </th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-600 uppercase tracking-wide">
                    Last updated
                  </th>
                </tr>
              </thead>
              <tbody>
                {recentAssessments.map((a) => (
                  <tr
                    key={a.id}
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => navigate(`/runs/${a.id}`)}
                  >
                    <td className="px-4 py-2 text-gray-900 whitespace-nowrap">
                      {a.name}
                    </td>
                    <td className="px-4 py-2 text-gray-800 whitespace-nowrap">
                      {a.client}
                    </td>
                    <td className="px-4 py-2 text-gray-800 whitespace-nowrap">
                      {a.environment}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap">
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          statusStyles[a.status]
                        }`}
                      >
                        {a.status}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-right text-gray-700 whitespace-nowrap">
                      {a.lastUpdated}
                    </td>
                  </tr>
                ))}

                {!loadingRuns && recentAssessments.length === 0 && (
                  <tr>
                    <td
                      colSpan={5}
                      className="px-4 py-6 text-center text-sm text-gray-500"
                    >
                      No assessments yet. Click{" "}
                      <button
                        onClick={handleStartNewAssessment}
                        className="text-blue-600 hover:underline"
                      >
                        Start New Assessment
                      </button>{" "}
                      to create your first one.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent activity (still mostly illustrative) */}
        <div className="border border-gray-200 bg-white rounded-md shadow-sm">
          <div className="px-4 py-3 border-b border-gray-200">
            <h2 className="text-sm font-medium text-gray-900">
              Recent activity
            </h2>
            <p className="text-xs text-gray-600">
              Key ingestion, analysis, and reporting events.
            </p>
          </div>

          <div className="px-4 py-4 space-y-3 text-sm">
            {primaryRun ? (
              <>
                <ActivityItem
                  title={`New assessment created: ${
                    primaryRun.name || "New assessment"
                  }`}
                  subtitle={new Date(
                    primaryRun.created_at
                  ).toLocaleString()}
                  tone="blue"
                />
                <ActivityItem
                  title="Initial server ingestion completed."
                  subtitle="Illustrative event – will be wired to ingestion logs."
                  tone="green"
                />
                <ActivityItem
                  title="Cost snapshot generation planned."
                  subtitle="Pending completion of TCO engine wiring."
                  tone="gray"
                />
              </>
            ) : (
              <p className="text-xs text-gray-500">
                Activity will appear here once you start your first assessment.
              </p>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}

/* ---------------------------------
   Small components
--------------------------------- */

function MetricCard({
  title,
  value,
  description,
  icon,
}: {
  title: string;
  value: number | string;
  description: string;
  icon?: "folder" | "servers" | "dollar";
}) {
  return (
    <div className="border border-gray-200 bg-white rounded-md px-4 py-4 shadow-sm flex items-center justify-between">
      <div>
        <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">
          {title}
        </p>
        <p className="text-xl font-semibold text-gray-900 mt-1">{value}</p>
        <p className="text-xs text-gray-600 mt-1">{description}</p>
      </div>
      {icon && (
        <div className="text-gray-300">
          {icon === "folder" && (
            <span className="text-2xl" aria-hidden="true">
              📁
            </span>
          )}
          {icon === "servers" && (
            <span className="text-2xl" aria-hidden="true">
              🖥️
            </span>
          )}
          {icon === "dollar" && (
            <span className="text-2xl" aria-hidden="true">
              💲
            </span>
          )}
        </div>
      )}
    </div>
  );
}

function EnginePill({
  label,
  status,
  color,
}: {
  label: string;
  status: string;
  color: "ok" | "warn" | "partial" | "planned";
}) {
  const colorClass =
    color === "ok"
      ? "bg-emerald-50 text-emerald-700 border-emerald-200"
      : color === "warn"
      ? "bg-amber-50 text-amber-700 border-amber-200"
      : color === "partial"
      ? "bg-blue-50 text-blue-700 border-blue-200"
      : "bg-gray-50 text-gray-700 border-gray-200";

  const dotClass =
    color === "ok"
      ? "bg-emerald-500"
      : color === "warn"
      ? "bg-amber-400"
      : color === "partial"
      ? "bg-blue-500"
      : "bg-gray-400";

  return (
    <span
      className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-[11px] border ${colorClass}`}
    >
      <span className={`w-2 h-2 rounded-full ${dotClass}`} />
      <span className="font-medium">{label}</span>
      <span className="text-gray-500">· {status}</span>
    </span>
  );
}

function SliceRow({
  name,
  status,
  items,
  lastUpdated,
  highlight,
  isLast,
}: {
  name: string;
  status: "Complete" | "Partial" | "Not Started";
  items: number;
  lastUpdated: string;
  highlight?: boolean;
  isLast?: boolean;
}) {
  const pillClass =
    status === "Complete"
      ? "bg-emerald-50 text-emerald-700 border-emerald-200"
      : status === "Partial"
      ? "bg-amber-50 text-amber-700 border-amber-200"
      : "bg-gray-50 text-gray-600 border-gray-200";

  return (
    <tr className={!isLast ? "border-b border-gray-100" : ""}>
      <td className="px-4 py-2 text-gray-900 whitespace-nowrap">
        <span className={highlight ? "font-semibold" : ""}>{name}</span>
      </td>
      <td className="px-4 py-2">
        <span
          className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] border ${pillClass}`}
        >
          {status}
        </span>
      </td>
      <td className="px-4 py-2 text-right text-gray-800 whitespace-nowrap">
        {items}
      </td>
      <td className="px-4 py-2 text-right text-gray-500 whitespace-nowrap text-xs">
        {lastUpdated}
      </td>
    </tr>
  );
}

function SnapshotTile({ label, value }: { label: string; value: number }) {
  return (
    <div className="border border-gray-200 rounded-md px-3 py-2 text-xs">
      <div className="text-gray-500">{label}</div>
      <div className="mt-1 text-lg font-semibold text-gray-900">{value}</div>
      <div className="text-[11px] text-gray-400">workloads</div>
    </div>
  );
}

function LegendDot({ className }: { className?: string }) {
  return (
    <span
      className={`inline-block w-2.5 h-2.5 rounded-full ${className ?? ""}`}
    />
  );
}

function ActivityItem({
  title,
  subtitle,
  tone,
}: {
  title: string;
  subtitle: string;
  tone: "blue" | "green" | "gray";
}) {
  const dotClass =
    tone === "blue"
      ? "bg-sky-500"
      : tone === "green"
      ? "bg-emerald-500"
      : "bg-gray-400";

  return (
    <div className="flex items-start gap-3">
      <span className={`mt-1 w-2 h-2 rounded-full ${dotClass}`} />
      <div>
        <div className="text-sm text-gray-900">{title}</div>
        <div className="text-xs text-gray-500">{subtitle}</div>
      </div>
    </div>
  );
}
