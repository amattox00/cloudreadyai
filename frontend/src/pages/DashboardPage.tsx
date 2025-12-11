import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listRuns, createRun, RunRecord } from "../api/runRegistry";

type BannerType = "error" | "info";

interface BannerState {
  type: BannerType;
  message: string;
}

function formatDate(value: string) {
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString();
}

function mapStateToLabel(state: RunRecord["state"]): string {
  switch (state) {
    case "created":
      return "Not Started";
    case "in_progress":
      return "In Progress";
    case "completed":
      return "Completed";
    case "error":
      return "Error";
    default:
      return state;
  }
}

const statusStyles: Record<string, string> = {
  "Not Started": "bg-gray-200 text-gray-700",
  "In Progress": "bg-blue-200 text-blue-800",
  Completed: "bg-green-200 text-green-800",
  Error: "bg-red-200 text-red-800",
};

export default function DashboardPage() {
  const navigate = useNavigate();

  const [runs, setRuns] = useState<RunRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [banner, setBanner] = useState<BannerState | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setBanner(null);
      try {
        const data = await listRuns();
        setRuns(data);
      } catch (err: any) {
        console.error("Dashboard run load failed", err);
        setBanner({
          type: "error",
          message: `Failed to load assessments: ${err.message || err}`,
        });
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleStart = async () => {
    try {
      setBanner(null);
      const run = await createRun("New assessment", "Dashboard");
      setRuns((prev) => [run, ...prev]);
      navigate(`/runs/${run.id}`);
    } catch (err: any) {
      console.error("Dashboard create run failed", err);
      setBanner({
        type: "error",
        message: `Failed to create run: ${err.message || err}`,
      });
    }
  };

  // Derived metrics from live data
  const totalAssessments = runs.length;
  const activeAssessments = runs.filter(
    (r) => r.state === "created" || r.state === "in_progress"
  ).length;
  const totalServers = runs.reduce(
    (acc, r) => acc + (r.servers_ingested || 0),
    0
  );

  // Simple slice coverage: 1 of 10 slices "complete" once servers > 0
  const totalSlices = 10;
  const completeSlices = totalServers > 0 ? 1 : 0;
  const coveragePct =
    totalSlices === 0 ? 0 : Math.round((completeSlices / totalSlices) * 100);

  const recentRuns = [...runs].sort((a, b) =>
    a.created_at < b.created_at ? 1 : -1
  ).slice(0, 5);

  return (
    <div className="px-6 py-6 space-y-6">
      {/* Error/info banner */}
      {banner && (
        <div
          className={`border px-4 py-2 rounded text-sm ${
            banner.type === "error"
              ? "bg-red-50 border-red-200 text-red-800"
              : "bg-blue-50 border-blue-200 text-blue-800"
          }`}
        >
          {banner.message}
        </div>
      )}

      {/* Command center hero */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl p-6 shadow flex items-center justify-between">
        <div>
          <div className="text-xs font-semibold uppercase tracking-wide opacity-80">
            CLOUDREADYA I
          </div>
          <h1 className="mt-1 text-2xl font-semibold">
            Your cloud migration command center
          </h1>
          <p className="mt-2 text-sm text-blue-100 max-w-2xl">
            Monitor assessments, ingestion, and cost modeling from a single
            workspace. Turn raw infrastructure data into migration-ready plans
            your clients can trust.
          </p>
        </div>

        <div className="flex items-center space-x-4">
          <div className="bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-xs shadow-sm">
            <div className="font-semibold mb-1">Workspace snapshot</div>
            <div className="space-y-0.5">
              <div>
                Active assessments:{" "}
                <span className="font-semibold">{activeAssessments}</span>
              </div>
              <div>
                Total assessments:{" "}
                <span className="font-semibold">{totalAssessments}</span>
              </div>
              <div>
                Env: <span className="font-semibold">dev</span>
              </div>
            </div>
          </div>

          <button
            onClick={handleStart}
            className="bg-white text-blue-700 px-4 py-2 rounded-md text-sm font-medium shadow hover:bg-blue-50"
          >
            Start New Assessment
          </button>
        </div>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Active assessments"
          value={activeAssessments.toString()}
          subtitle="Currently in progress across your workspace."
        />
        <MetricCard
          title="Total assessments"
          value={totalAssessments.toString()}
          subtitle="Historical and in-flight assessments."
          icon="folder"
        />
        <MetricCard
          title="Environment data collected"
          value={`${totalServers} servers, 0 apps`}
          subtitle="Latest ingestion across all environments."
          icon="server"
        />
        <MetricCard
          title="Cost snapshots"
          value="0 snapshots"
          subtitle="Generate from any completed assessment."
          icon="dollar"
        />
      </div>

      {/* Middle row: Engine health + Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Engine health */}
        <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-sm font-medium text-gray-900">
              Engine health
            </h2>
            <p className="text-xs text-gray-500">
              Status of core CloudReadyAI engines.
            </p>
          </div>

          <div className="flex flex-wrap gap-2 text-xs">
            <EnginePill label="Ingestion engine" status="Healthy" color="green" />
            <EnginePill
              label="Analysis engine"
              status="Planned"
              color="gray"
            />
            <EnginePill
              label="Cost & TCO engine"
              status="Partial"
              color="amber"
            />
            <EnginePill
              label="Diagrams engine"
              status="Planned"
              color="gray"
            />
            <EnginePill
              label="Reporting engine"
              status="Planned"
              color="gray"
            />
          </div>
        </div>

        {/* Migration Insights Snapshot (placeholder for Phase C) */}
        <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4">
          <h2 className="text-sm font-medium text-gray-900 mb-1">
            Migration Insights Snapshot
          </h2>
          <p className="text-xs text-gray-600 mb-4">
            Insights will summarize readiness, refactor candidates, and
            workloads that need investigation once the Insights engine is fully
            wired.
          </p>

          <div className="grid grid-cols-3 gap-3 text-center text-xs">
            <div className="border border-gray-100 rounded-md p-3">
              <div className="text-gray-500 mb-1">Ready for rehost</div>
              <div className="text-lg font-semibold text-gray-900">—</div>
              <div className="text-gray-400">workloads</div>
            </div>
            <div className="border border-gray-100 rounded-md p-3">
              <div className="text-gray-500 mb-1">Ready for refactor</div>
              <div className="text-lg font-semibold text-gray-900">—</div>
              <div className="text-gray-400">workloads</div>
            </div>
            <div className="border border-gray-100 rounded-md p-3">
              <div className="text-gray-500 mb-1">Needs investigation</div>
              <div className="text-lg font-semibold text-gray-900">—</div>
              <div className="text-gray-400">workloads</div>
            </div>
          </div>

          <div className="mt-4 border border-dashed border-gray-200 rounded-md p-3 text-xs text-gray-500">
            <div className="font-medium mb-1">
              Migration Strategy Preview
            </div>
            <p>
              Strategy mix will light up here once the Insights engine is wired.
              For now, use the <span className="font-semibold">Ingestion</span>{" "}
              and <span className="font-semibold">Cost Modeling</span> views
              for detailed drill-down.
            </p>
          </div>
        </div>
      </div>

      {/* Data readiness + Recent sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Data Readiness & Coverage */}
        <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h2 className="text-sm font-medium text-gray-900">
                Data Readiness & Coverage
              </h2>
              <p className="text-xs text-gray-600">
                Completeness of your 10 ingestion slices across all active
                assessments.
              </p>
            </div>
            <div className="text-xs text-gray-500">
              {completeSlices} of {totalSlices} slices complete (
              {coveragePct}% coverage)
            </div>
          </div>

          {/* progress bar */}
          <div className="w-full bg-gray-100 rounded-full h-1.5 mb-4">
            <div
              className="bg-emerald-500 h-1.5 rounded-full"
              style={{ width: `${coveragePct}%` }}
            />
          </div>

          <p className="text-xs text-gray-500 mb-3">
            Focus next on ingesting{" "}
            <span className="font-semibold">
              storage, databases, and applications
            </span>{" "}
            to unlock full analysis.
          </p>

          <div className="overflow-x-auto">
            <table className="min-w-full text-xs">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-3 py-2 text-left font-medium text-gray-600 uppercase tracking-wide">
                    Slice
                  </th>
                  <th className="px-3 py-2 text-left font-medium text-gray-600 uppercase tracking-wide">
                    Status
                  </th>
                  <th className="px-3 py-2 text-right font-medium text-gray-600 uppercase tracking-wide">
                    Items
                  </th>
                  <th className="px-3 py-2 text-right font-medium text-gray-600 uppercase tracking-wide">
                    Last updated
                  </th>
                </tr>
              </thead>
              <tbody>
                <SliceRow
                  name="Servers"
                  status={totalServers > 0 ? "Complete" : "Not Started"}
                  statusTone={totalServers > 0 ? "green" : "gray"}
                  items={totalServers}
                  updated={totalServers > 0 ? "Just now" : "—"}
                />
                <SliceRow
                  name="Storage volumes"
                  status="Not Started"
                  statusTone="gray"
                  items={0}
                  updated="—"
                />
                <SliceRow
                  name="Databases"
                  status="Not Started"
                  statusTone="gray"
                  items={0}
                  updated="—"
                />
                <SliceRow
                  name="Applications"
                  status="Not Started"
                  statusTone="gray"
                  items={0}
                  updated="—"
                />
                <SliceRow
                  name="Network devices"
                  status="Not Started"
                  statusTone="gray"
                  items={0}
                  updated="—"
                />
                <SliceRow
                  name="Business metadata"
                  status="Partial"
                  statusTone="amber"
                  items={0}
                  updated="Yesterday"
                />
                <SliceRow
                  name="Dependencies"
                  status="Not Started"
                  statusTone="gray"
                  items={0}
                  updated="—"
                />
                <SliceRow
                  name="Performance metrics"
                  status="Not Started"
                  statusTone="gray"
                  items={0}
                  updated="—"
                />
                <SliceRow
                  name="Cost & usage"
                  status="Not Started"
                  statusTone="gray"
                  items={0}
                  updated="—"
                />
                <SliceRow
                  name="Security / compliance"
                  status="Not Started"
                  statusTone="gray"
                  items={0}
                  updated="—"
                />
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent assessments + activity */}
        <div className="space-y-4">
          {/* Recent assessments */}
          <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4">
            <div className="flex items-center justify-between mb-2">
              <div>
                <h2 className="text-sm font-medium text-gray-900">
                  Recent assessments
                </h2>
                <p className="text-xs text-gray-600">
                  Open an assessment to review ingestion, insights, and
                  reports.
                </p>
              </div>
            </div>

            <div className="overflow-x-auto mt-2">
              <table className="min-w-full text-xs">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-3 py-2 text-left font-medium text-gray-600 uppercase tracking-wide">
                      Assessment
                    </th>
                    <th className="px-3 py-2 text-left font-medium text-gray-600 uppercase tracking-wide">
                      Client / Source
                    </th>
                    <th className="px-3 py-2 text-left font-medium text-gray-600 uppercase tracking-wide">
                      Status
                    </th>
                    <th className="px-3 py-2 text-right font-medium text-gray-600 uppercase tracking-wide">
                      Last updated
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {recentRuns.map((run) => {
                    const label = mapStateToLabel(run.state);
                    return (
                      <tr
                        key={run.id}
                        className="hover:bg-gray-50 cursor-pointer"
                        onClick={() => navigate(`/runs/${run.id}`)}
                      >
                        <td className="px-3 py-2 text-gray-900">
                          {run.name}
                        </td>
                        <td className="px-3 py-2 text-gray-700">
                          {run.source}
                        </td>
                        <td className="px-3 py-2">
                          <span
                            className={`px-2 py-0.5 rounded-full text-[11px] font-medium ${
                              statusStyles[label] ||
                              "bg-gray-200 text-gray-700"
                            }`}
                          >
                            {label}
                          </span>
                        </td>
                        <td className="px-3 py-2 text-right text-gray-600">
                          {formatDate(run.created_at)}
                        </td>
                      </tr>
                    );
                  })}

                  {!loading && recentRuns.length === 0 && (
                    <tr>
                      <td
                        colSpan={4}
                        className="px-3 py-4 text-center text-gray-500"
                      >
                        No assessments yet. Click{" "}
                        <button
                          onClick={handleStart}
                          className="text-blue-600 hover:underline"
                        >
                          Start New Assessment
                        </button>{" "}
                        to create your first one.
                      </td>
                    </tr>
                  )}

                  {loading && (
                    <tr>
                      <td
                        colSpan={4}
                        className="px-3 py-4 text-center text-gray-500"
                      >
                        Loading…
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Recent activity (placeholder for event stream) */}
          <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4">
            <h2 className="text-sm font-medium text-gray-900 mb-1">
              Recent activity
            </h2>
            <p className="text-xs text-gray-600 mb-3">
              Key ingestion, analysis, and reporting events. Live event stream
              will be wired in Phase C/D.
            </p>

            <ul className="space-y-2 text-xs">
              <li className="flex items-start space-x-2">
                <span className="mt-1 h-2 w-2 rounded-full bg-emerald-500" />
                <div>
                  <div className="text-gray-800">
                    CloudReadyAI workspace ready for assessments.
                  </div>
                  <div className="text-gray-400">Just now · system</div>
                </div>
              </li>
              <li className="flex items-start space-x-2">
                <span className="mt-1 h-2 w-2 rounded-full bg-gray-400" />
                <div>
                  <div className="text-gray-800">
                    Ingestion engine ready for CSV-based workloads.
                  </div>
                  <div className="text-gray-400">
                    Wiring to collectors scheduled for Phase B2/B3.
                  </div>
                </div>
              </li>
              <li className="flex items-start space-x-2">
                <span className="mt-1 h-2 w-2 rounded-full bg-gray-400" />
                <div>
                  <div className="text-gray-800">
                    Cost &amp; TCO engine partially configured.
                  </div>
                  <div className="text-gray-400">
                    AWS pricing sync and SKU cache planned.
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ------------------------------
   Small presentational components
------------------------------ */

function MetricCard({
  title,
  value,
  subtitle,
  icon,
}: {
  title: string;
  value: string;
  subtitle: string;
  icon?: "folder" | "server" | "dollar";
}) {
  return (
    <div className="border border-gray-200 bg-white rounded-md px-4 py-4 shadow-sm flex items-center justify-between">
      <div>
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
          {title}
        </p>
        <p className="text-lg font-semibold text-gray-900 mt-1">
          {value}
        </p>
        <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
      </div>
      {icon && (
        <div className="text-gray-300">
          {icon === "folder" && (
            <span className="text-2xl" aria-hidden="true">
              📁
            </span>
          )}
          {icon === "server" && (
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
  color: "green" | "gray" | "amber";
}) {
  const colorMap: Record<typeof color, string> = {
    green: "bg-emerald-100 text-emerald-800",
    gray: "bg-gray-100 text-gray-700",
    amber: "bg-amber-100 text-amber-800",
  };
  const dotMap: Record<typeof color, string> = {
    green: "bg-emerald-500",
    gray: "bg-gray-400",
    amber: "bg-amber-500",
  };
  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-full ${colorMap[color]}`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full mr-1 ${dotMap[color]}`}
      />
      <span className="font-medium mr-1">{label}</span>
      <span className="text-[11px] opacity-80">{status}</span>
    </span>
  );
}

function SliceRow({
  name,
  status,
  statusTone,
  items,
  updated,
}: {
  name: string;
  status: string;
  statusTone: "green" | "gray" | "amber";
  items: number;
  updated: string;
}) {
  const colorMap: Record<typeof statusTone, string> = {
    green: "bg-emerald-100 text-emerald-800",
    gray: "bg-gray-100 text-gray-700",
    amber: "bg-amber-100 text-amber-800",
  };
  return (
    <tr className="border-b border-gray-100 last:border-0">
      <td className="px-3 py-2 text-gray-800">{name}</td>
      <td className="px-3 py-2">
        <span
          className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium ${colorMap[statusTone]}`}
        >
          {status}
        </span>
      </td>
      <td className="px-3 py-2 text-right text-gray-800">{items}</td>
      <td className="px-3 py-2 text-right text-gray-500">
        {updated}
      </td>
    </tr>
  );
}
