import React from "react";
import { Link } from "react-router-dom";

type AssessmentStatus = "Not Started" | "In Progress" | "Completed";

interface PortfolioAssessment {
  id: string;
  name: string;
  client: string;
  environment: string;
  status: AssessmentStatus;
  coveragePct: number;
  lastUpdated: string;
  servers: number;
  applications: number;
  databases: number;
}

interface PortfolioSlice {
  id: string;
  label: string;
  status: "complete" | "partial" | "not_started";
  items: number;
  lastUpdated: string | null;
}

interface StrategyBreakdown {
  label: string;
  colorClass: string;
  workloads: number;
}

// ----------------------
// Mock portfolio data
// ----------------------

// Same three runs we’ve been using elsewhere
const mockAssessments: PortfolioAssessment[] = [
  {
    id: "run-001",
    name: "US-East Datacenter Migration",
    client: "ACME Corp",
    environment: "VMware · Production",
    status: "In Progress",
    coveragePct: 20,
    lastUpdated: "5 minutes ago",
    servers: 87,
    applications: 24,
    databases: 12,
  },
  {
    id: "run-002",
    name: "Finance Apps Modernization",
    client: "ACME Corp",
    environment: "Hybrid · Non-Prod",
    status: "Completed",
    coveragePct: 78,
    lastUpdated: "1 day ago",
    servers: 52,
    applications: 12,
    databases: 7,
  },
  {
    id: "run-003",
    name: "Legacy Workloads Review",
    client: "Global Manufacturing",
    environment: "Windows · Production",
    status: "Not Started",
    coveragePct: 0,
    lastUpdated: "2 days ago",
    servers: 35,
    applications: 4,
    databases: 3,
  },
];

// Slice-level portfolio coverage (rolled up / mocked)
const mockSlices: PortfolioSlice[] = [
  {
    id: "servers",
    label: "Servers",
    status: "complete",
    items: 174,
    lastUpdated: "Today",
  },
  {
    id: "storage",
    label: "Storage volumes",
    status: "complete",
    items: 143,
    lastUpdated: "Today",
  },
  {
    id: "databases",
    label: "Databases",
    status: "partial",
    items: 22,
    lastUpdated: "Today",
  },
  {
    id: "applications",
    label: "Applications",
    status: "partial",
    items: 40,
    lastUpdated: "Yesterday",
  },
  {
    id: "network",
    label: "Network devices",
    status: "not_started",
    items: 15,
    lastUpdated: "Yesterday",
  },
  {
    id: "business_metadata",
    label: "Business metadata",
    status: "not_started",
    items: 0,
    lastUpdated: null,
  },
  {
    id: "dependencies",
    label: "Dependencies",
    status: "not_started",
    items: 0,
    lastUpdated: null,
  },
  {
    id: "os_software",
    label: "OS & software",
    status: "not_started",
    items: 0,
    lastUpdated: null,
  },
  {
    id: "utilization",
    label: "Utilization",
    status: "not_started",
    items: 0,
    lastUpdated: null,
  },
  {
    id: "licensing",
    label: "Licensing",
    status: "not_started",
    items: 0,
    lastUpdated: null,
  },
];

const mockStrategyBreakdown: StrategyBreakdown[] = [
  {
    label: "Rehost",
    colorClass: "bg-sky-500",
    workloads: 48,
  },
  {
    label: "Refactor",
    colorClass: "bg-emerald-500",
    workloads: 27,
  },
  {
    label: "Investigate",
    colorClass: "bg-amber-500",
    workloads: 25,
  },
];

// ----------------------
// Derived metrics
// ----------------------

const totalAssessments = mockAssessments.length;
const totalClients = new Set(mockAssessments.map((a) => a.client)).size;
const totalServers = mockAssessments.reduce(
  (sum, a) => sum + a.servers,
  0
);
const totalApplications = mockAssessments.reduce(
  (sum, a) => sum + a.applications,
  0
);
const totalDatabases = mockAssessments.reduce(
  (sum, a) => sum + a.databases,
  0
);
const averageCoverage =
  mockAssessments.reduce((sum, a) => sum + a.coveragePct, 0) /
  Math.max(mockAssessments.length, 1);

const completeSlices = mockSlices.filter(
  (s) => s.status === "complete"
).length;
const partialSlices = mockSlices.filter(
  (s) => s.status === "partial"
).length;
const notStartedSlices = mockSlices.filter(
  (s) => s.status === "not_started"
).length;

// ----------------------
// Page component
// ----------------------

export default function PortfolioPage() {
  return (
    <div className="px-6 py-6 space-y-6">
      {/* Header / hero */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">
            Portfolio Overview
          </h1>
          <p className="mt-1 text-sm text-slate-600 max-w-2xl">
            Cross-assessment view of your discovered environments, workloads,
            and migration insights. Use this workspace to spot patterns and
            prioritize where to focus next.
          </p>
        </div>

        <div className="border border-slate-200 rounded-xl bg-white shadow-sm px-4 py-3 text-xs text-slate-600 min-w-[220px]">
          <div className="font-semibold text-slate-900 mb-1">
            Portfolio Snapshot
          </div>
          <div className="flex justify-between">
            <span>Total assessments</span>
            <span className="font-semibold text-slate-900">
              {totalAssessments}
            </span>
          </div>
          <div className="flex justify-between">
            <span>Clients</span>
            <span className="font-semibold text-slate-900">
              {totalClients}
            </span>
          </div>
          <div className="flex justify-between">
            <span>Avg. coverage</span>
            <span className="font-semibold text-slate-900">
              {Math.round(averageCoverage)}%
            </span>
          </div>
        </div>
      </div>

      {/* Snapshot cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <SnapshotCard
          title="Total assessments"
          value={String(totalAssessments)}
          subtitle="In-flight and completed assessments"
        />
        <SnapshotCard
          title="Clients"
          value={String(totalClients)}
          subtitle="Unique client organizations"
        />
        <SnapshotCard
          title="Workloads discovered"
          value={`${totalServers} servers · ${totalApplications} apps`}
          subtitle={`${totalDatabases} databases`}
        />
        <SnapshotCard
          title="Average ingestion coverage"
          value={`${Math.round(averageCoverage)}%`}
          subtitle="Across all ingestion slices"
        />
      </div>

      {/* Coverage + Strategy row */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Portfolio Coverage card */}
        <div className="border border-slate-200 bg-white rounded-xl shadow-sm p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-slate-900">
                Portfolio Coverage
              </h2>
              <p className="text-xs text-slate-600">
                Completeness of your 10 ingestion slices across all
                assessments.
              </p>
            </div>
            <div className="text-xs text-slate-600 text-right">
              <div>
                <span className="font-semibold text-emerald-600">
                  {completeSlices}
                </span>{" "}
                complete
              </div>
              <div>
                <span className="font-semibold text-amber-600">
                  {partialSlices}
                </span>{" "}
                partial
              </div>
              <div>
                <span className="font-semibold text-slate-600">
                  {notStartedSlices}
                </span>{" "}
                not started
              </div>
            </div>
          </div>

          {/* Simple coverage bar */}
          <div className="mt-1 h-2 rounded-full bg-slate-100 overflow-hidden flex">
            <div
              className="bg-emerald-500"
              style={{
                width: `${(completeSlices / mockSlices.length) * 100}%`,
              }}
            />
            <div
              className="bg-amber-400"
              style={{
                width: `${(partialSlices / mockSlices.length) * 100}%`,
              }}
            />
            <div
              className="bg-slate-300"
              style={{
                width: `${
                  (notStartedSlices / mockSlices.length) * 100
                }%`,
              }}
            />
          </div>

          {/* Slice table */}
          <div className="mt-3 border border-slate-200 rounded-lg overflow-hidden">
            <table className="min-w-full text-xs">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-3 py-2 text-left font-medium text-slate-600 uppercase tracking-wide">
                    Slice
                  </th>
                  <th className="px-3 py-2 text-left font-medium text-slate-600 uppercase tracking-wide">
                    Status
                  </th>
                  <th className="px-3 py-2 text-right font-medium text-slate-600 uppercase tracking-wide">
                    Items
                  </th>
                  <th className="px-3 py-2 text-left font-medium text-slate-600 uppercase tracking-wide">
                    Last updated
                  </th>
                </tr>
              </thead>
              <tbody>
                {mockSlices.map((slice, idx) => (
                  <tr
                    key={slice.id}
                    className={idx % 2 === 0 ? "bg-white" : "bg-slate-50/70"}
                  >
                    <td className="px-3 py-2 text-slate-900">
                      {slice.label}
                    </td>
                    <td className="px-3 py-2">
                      <SliceStatusBadge status={slice.status} />
                    </td>
                    <td className="px-3 py-2 text-right text-slate-900">
                      {slice.items}
                    </td>
                    <td className="px-3 py-2 text-slate-500">
                      {slice.lastUpdated ?? "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Migration strategy snapshot */}
        <div className="border border-slate-200 bg-white rounded-xl shadow-sm p-4 space-y-4">
          <h2 className="text-sm font-semibold text-slate-900">
            Migration Insights Snapshot
          </h2>
          <p className="text-xs text-slate-600">
            Illustrative mix of migration strategies across all workloads.
            Values are mocked until the Insights engine is fully wired.
          </p>

          {/* Strategy legend */}
          <div className="flex flex-wrap gap-3 text-[11px] text-slate-700">
            {mockStrategyBreakdown.map((s) => (
              <span
                key={s.label}
                className="inline-flex items-center gap-1"
              >
                <span
                  className={`h-2 w-2 rounded-full ${s.colorClass}`}
                />
                <span>{s.label}</span>
                <span className="text-slate-400">
                  · {s.workloads} workloads
                </span>
              </span>
            ))}
          </div>

          {/* Strategy bar */}
          <div className="mt-2 h-3 rounded-full bg-slate-100 overflow-hidden flex">
            {mockStrategyBreakdown.map((s) => (
              <div
                key={s.label}
                className={s.colorClass}
                style={{
                  width: `${
                    (s.workloads /
                      mockStrategyBreakdown.reduce(
                        (sum, x) => sum + x.workloads,
                        0
                      )) *
                    100
                  }%`,
                }}
              />
            ))}
          </div>

          <p className="text-[11px] text-slate-600">
            Strategy mix based on discovered workloads. Drill into
            individual assessments to see per-workload strategy and
            readiness details.
          </p>
        </div>
      </div>

      {/* Assessments table */}
      <div className="border border-slate-200 bg-white rounded-xl shadow-sm p-4">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="text-sm font-semibold text-slate-900">
              Assessments
            </h2>
            <p className="text-xs text-slate-600">
              Click any row to open the detailed ingestion, insights, and
              cost modeling view.
            </p>
          </div>
          <div className="text-[11px] text-slate-500">
            {totalAssessments} assessments in this workspace
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full text-xs">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-3 py-2 text-left font-medium text-slate-600 uppercase tracking-wide">
                  Assessment
                </th>
                <th className="px-3 py-2 text-left font-medium text-slate-600 uppercase tracking-wide">
                  Client
                </th>
                <th className="px-3 py-2 text-left font-medium text-slate-600 uppercase tracking-wide">
                  Environment
                </th>
                <th className="px-3 py-2 text-left font-medium text-slate-600 uppercase tracking-wide">
                  Status
                </th>
                <th className="px-3 py-2 text-left font-medium text-slate-600 uppercase tracking-wide">
                  Coverage
                </th>
                <th className="px-3 py-2 text-right font-medium text-slate-600 uppercase tracking-wide">
                  Last updated
                </th>
              </tr>
            </thead>
            <tbody>
              {mockAssessments.map((a, idx) => (
                <tr
                  key={a.id}
                  className={`${
                    idx % 2 === 0 ? "bg-white" : "bg-slate-50/80"
                  } hover:bg-sky-50 cursor-pointer`}
                >
                  <td className="px-3 py-2 text-sky-700 font-medium">
                    <Link to={`/runs/${a.id}`}>{a.name}</Link>
                  </td>
                  <td className="px-3 py-2 text-slate-900">
                    {a.client}
                  </td>
                  <td className="px-3 py-2 text-slate-900">
                    {a.environment}
                  </td>
                  <td className="px-3 py-2">
                    <AssessmentStatusBadge status={a.status} />
                  </td>
                  <td className="px-3 py-2">
                    <CoveragePill coverage={a.coveragePct} />
                  </td>
                  <td className="px-3 py-2 text-right text-slate-500">
                    {a.lastUpdated}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ----------------------
// Small presentational components
// ----------------------

function SnapshotCard(props: {
  title: string;
  value: string;
  subtitle?: string;
}) {
  const { title, value, subtitle } = props;
  return (
    <div className="border border-slate-200 bg-white rounded-xl px-4 py-4 shadow-sm">
      <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">
        {title}
      </p>
      <p className="mt-1 text-lg font-semibold text-slate-900">
        {value}
      </p>
      {subtitle && (
        <p className="mt-1 text-[11px] text-slate-500">{subtitle}</p>
      )}
    </div>
  );
}

function SliceStatusBadge({
  status,
}: {
  status: PortfolioSlice["status"];
}) {
  let label = "";
  let bg = "";
  let dot = "";

  switch (status) {
    case "complete":
      label = "Complete";
      bg = "bg-emerald-50 border border-emerald-100 text-emerald-700";
      dot = "bg-emerald-500";
      break;
    case "partial":
      label = "Partial";
      bg = "bg-amber-50 border border-amber-100 text-amber-700";
      dot = "bg-amber-500";
      break;
    default:
      label = "Not Started";
      bg = "bg-slate-50 border border-slate-200 text-slate-700";
      dot = "bg-slate-400";
  }

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium ${bg}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${dot}`} />
      <span>{label}</span>
    </span>
  );
}

function AssessmentStatusBadge({ status }: { status: AssessmentStatus }) {
  let bg = "";
  let text = "";

  switch (status) {
    case "Completed":
      bg = "bg-emerald-50 text-emerald-700 border border-emerald-100";
      text = "Completed";
      break;
    case "In Progress":
      bg = "bg-sky-50 text-sky-700 border border-sky-100";
      text = "In Progress";
      break;
    default:
      bg = "bg-slate-50 text-slate-700 border border-slate-200";
      text = "Not Started";
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium ${bg}`}
    >
      {text}
    </span>
  );
}

function CoveragePill({ coverage }: { coverage: number }) {
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 flex-1 rounded-full bg-slate-100 overflow-hidden">
        <div
          className="h-1.5 rounded-full bg-sky-500"
          style={{ width: `${coverage}%` }}
        />
      </div>
      <span className="text-[11px] text-slate-700 font-medium w-10 text-right">
        {coverage}%
      </span>
    </div>
  );
}
