import React from "react";
import { useNavigate } from "react-router-dom";

type AssessmentStatus = "Not Started" | "In Progress" | "Completed" | "Error";
type SliceStatus = "Not Started" | "Partial" | "Complete";

interface Assessment {
  id: string;
  name: string;
  client: string;
  environment: string;
  status: AssessmentStatus;
  lastUpdated: string;
}

interface IngestionSlice {
  id: string;
  label: string;
  status: SliceStatus;
  items: number;
  updated: string | null;
}

const mockAssessments: Assessment[] = [
  {
    id: "run-001",
    name: "US-East Datacenter Migration",
    client: "ACME Corp",
    environment: "VMware · Production",
    status: "In Progress",
    lastUpdated: "5 minutes ago",
  },
  {
    id: "run-002",
    name: "Finance Apps Modernization",
    client: "ACME Corp",
    environment: "Hybrid · Non-Prod",
    status: "Completed",
    lastUpdated: "1 day ago",
  },
  {
    id: "run-003",
    name: "Legacy Workloads Review",
    client: "Global Manufacturing",
    environment: "Windows · Production",
    status: "Not Started",
    lastUpdated: "2 days ago",
  },
];

const statusStyles: Record<AssessmentStatus, string> = {
  "Not Started": "bg-gray-200 text-gray-700",
  "In Progress": "bg-blue-200 text-blue-800",
  Completed: "bg-green-200 text-green-800",
  Error: "bg-red-200 text-red-800",
};

const mockActivity = [
  {
    id: 1,
    time: "5 minutes ago",
    text: "Ingestion completed for US-East Datacenter Migration.",
  },
  {
    id: 2,
    time: "2 hours ago",
    text: "New assessment created: Legacy Workloads Review.",
  },
  {
    id: 3,
    time: "Yesterday",
    text: "Cost snapshot generated for Finance Apps Modernization.",
  },
];

const pipelineStages = [
  {
    label: "1. Ingest environment data",
    status: "In Progress" as const,
    description:
      "Connect collectors or upload CSVs for servers, storage, databases, and apps.",
  },
  {
    label: "2. Analyze workloads & readiness",
    status: "Planned" as const,
    description: "Score migration readiness and surface risks per workload.",
  },
  {
    label: "3. Design target architectures",
    status: "Planned" as const,
    description: "Generate AWS, Azure, and GCP reference architectures.",
  },
  {
    label: "4. Model cloud cost scenarios",
    status: "Planned" as const,
    description: "Compare on-prem vs cloud TCO with optimization options.",
  },
  {
    label: "5. Export executive reports",
    status: "Planned" as const,
    description: "Produce client-ready migration decks and deliverables.",
  },
];

const completedOrActiveCount = pipelineStages.filter(
  (s) => s.status === "In Progress" || s.status === "Completed"
).length;
const pipelineProgressPct = Math.round(
  (completedOrActiveCount / pipelineStages.length) * 100
);

/** Mock migration strategy counts for the snapshot */
const readinessCounts = {
  rehost: 48,
  refactor: 27,
  investigate: 25,
};
const totalWorkloads =
  readinessCounts.rehost +
  readinessCounts.refactor +
  readinessCounts.investigate;

const readinessPercents = {
  rehost: Math.round((readinessCounts.rehost / totalWorkloads) * 100),
  refactor: Math.round((readinessCounts.refactor / totalWorkloads) * 100),
  investigate: Math.round(
    (readinessCounts.investigate / totalWorkloads) * 100
  ),
};

/** Mock 10-slice data readiness model */
const ingestionSlices: IngestionSlice[] = [
  {
    id: "servers",
    label: "Servers",
    status: "Complete",
    items: 87,
    updated: "5 minutes ago",
  },
  {
    id: "storage",
    label: "Storage volumes",
    status: "Not Started",
    items: 0,
    updated: null,
  },
  {
    id: "databases",
    label: "Databases",
    status: "Not Started",
    items: 0,
    updated: null,
  },
  {
    id: "applications",
    label: "Applications",
    status: "Not Started",
    items: 0,
    updated: null,
  },
  {
    id: "network",
    label: "Network devices",
    status: "Not Started",
    items: 0,
    updated: null,
  },
  {
    id: "business",
    label: "Business metadata",
    status: "Partial",
    items: 2,
    updated: "Yesterday",
  },
  {
    id: "dependencies",
    label: "Dependencies",
    status: "Not Started",
    items: 0,
    updated: null,
  },
  {
    id: "os",
    label: "OS & software inventory",
    status: "Complete",
    items: 87,
    updated: "5 minutes ago",
  },
  {
    id: "licensing",
    label: "Licensing",
    status: "Not Started",
    items: 0,
    updated: null,
  },
  {
    id: "utilization",
    label: "Utilization & performance",
    status: "Not Started",
    items: 0,
    updated: null,
  },
];

const sliceStatusStyles: Record<SliceStatus, string> = {
  "Not Started": "bg-slate-100 text-slate-700",
  Partial: "bg-amber-100 text-amber-800",
  Complete: "bg-emerald-100 text-emerald-800",
};

const completedSlices = ingestionSlices.filter(
  (s) => s.status === "Complete"
).length;
const readinessPct = Math.round(
  (completedSlices / ingestionSlices.length) * 100
);

export default function DashboardPage() {
  const navigate = useNavigate();

  const handleStart = () => navigate("/runs/new");
  const openAssessment = (id: string) => navigate(`/runs/${id}`);

  const activeCount = mockAssessments.filter(
    (a) => a.status === "In Progress"
  ).length;

  return (
    <div className="px-6 py-6 space-y-8 bg-slate-50/40 min-h-screen">
      {/* Hero / masthead */}
      <div className="rounded-2xl bg-gradient-to-r from-sky-600 via-blue-600 to-indigo-600 text-white shadow-md px-6 py-6 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div className="space-y-2">
          <p className="text-xs font-semibold tracking-[0.18em] uppercase text-sky-100">
            CloudReadyAI
          </p>
          <h1 className="text-2xl md:text-3xl font-semibold">
            Your cloud migration command center
          </h1>
          <p className="text-sm md:text-base text-sky-100/90 max-w-xl">
            Monitor assessments, ingestion, and cost modeling from a single
            workspace. Turn raw infrastructure data into migration-ready plans
            your clients can trust.
          </p>
        </div>

        <div className="flex flex-col items-stretch sm:flex-row sm:items-center gap-4">
          <div className="px-4 py-3 rounded-xl bg-slate-950/40 border border-slate-900/40 text-xs leading-tight shadow-sm min-w-[190px]">
            <p className="font-semibold text-sky-100">Workspace snapshot</p>
            <div className="mt-2 space-y-1 text-sky-100/90">
              <p>Active assessments: {activeCount}</p>
              <p>Total clients: 2 · Portfolios: 3</p>
              <p>Environment: dev</p>
            </div>
          </div>
          <button
            onClick={handleStart}
            className="bg-white text-slate-900 px-5 py-2.5 rounded-lg shadow-md hover:bg-slate-50 text-sm font-semibold whitespace-nowrap flex items-center gap-2"
          >
            <span className="inline-block h-2 w-2 rounded-full bg-emerald-500" />
            Start New Assessment
          </button>
        </div>
      </div>

      {/* KPI tiles */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Active assessments"
          value={String(activeCount)}
          sublabel="Currently in progress across your workspace"
          highlight
          icon="▶"
        />
        <KpiCard
          label="Total assessments"
          value={String(mockAssessments.length)}
          sublabel="Historical and in-flight assessments"
          icon="📁"
        />
        <KpiCard
          label="Environment data collected"
          value="32 servers, 4 apps"
          sublabel="Latest ingestion across all environments"
          icon="🖥"
        />
        <KpiCard
          label="Cost snapshots"
          value="0 snapshots"
          sublabel="Generate from any completed assessment"
          icon="💲"
        />
      </div>

      {/* NEW: Data Readiness & Coverage (full width) */}
      <DataReadinessSection />

      {/* Middle row: assessment pipeline + insights */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Assessment pipeline & health (2/3) */}
        <div className="xl:col-span-2 space-y-4">
          <div className="border border-slate-200 bg-white rounded-xl shadow-sm p-4">
            <div className="flex items-center justify-between mb-1">
              <h2 className="text-sm font-semibold text-slate-900">
                Assessment pipeline
              </h2>
              <span className="text-[11px] text-slate-500">
                Guided migration workflow
              </span>
            </div>
            <p className="text-xs text-slate-600">
              See where your assessments sit in the CloudReadyAI migration
              pipeline.
            </p>

            <div className="mt-3">
              <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-sky-500"
                  style={{ width: `${pipelineProgressPct}%` }}
                />
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                {completedOrActiveCount} of {pipelineStages.length} stages
                active or completed ({pipelineProgressPct}%)
              </p>
            </div>

            <ol className="mt-4 space-y-3 text-sm">
              {pipelineStages.map((stage) => (
                <PipelineStep
                  key={stage.label}
                  label={stage.label}
                  status={stage.status}
                  description={stage.description}
                />
              ))}
            </ol>
          </div>
        </div>

        {/* Insights column (1/3) */}
        <div className="space-y-4">
          {/* Snapshot */}
          <div className="border border-slate-200 bg-white rounded-xl shadow-sm p-4 space-y-3">
            <div>
              <h2 className="text-sm font-semibold text-slate-900">
                Migration Insights Snapshot
              </h2>
              <p className="text-xs text-slate-600">
                Illustrative view of how workloads align to migration
                strategies. Live values will come from the Insights engine.
              </p>
              <p className="text-[11px] text-slate-500 mt-1">
                Based on {readinessCounts.rehost +
                  readinessCounts.refactor +
                  readinessCounts.investigate}{" "}
                workloads discovered so far.
              </p>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <InsightStat
                label="Ready for rehost"
                value={`${readinessCounts.rehost}`}
                note="workloads"
              />
              <InsightStat
                label="Ready for refactor"
                value={`${readinessCounts.refactor}`}
                note="workloads"
              />
              <InsightStat
                label="Needs investigation"
                value={`${readinessCounts.investigate}`}
                note="workloads"
              />
            </div>
          </div>

          {/* Strategy preview */}
          <div className="border border-dashed border-slate-300 bg-slate-50 rounded-xl p-4 shadow-sm">
            <p className="mb-3 text-sm font-semibold text-slate-900">
              Migration Strategy Preview
            </p>

            <div className="flex flex-col gap-2 mb-3">
              <StrategyLegend
                colorClass="bg-sky-500"
                label="Rehost"
                value={`${readinessCounts.rehost} workloads`}
              />
              <StrategyLegend
                colorClass="bg-emerald-500"
                label="Refactor"
                value={`${readinessCounts.refactor} workloads`}
              />
              <StrategyLegend
                colorClass="bg-amber-400"
                label="Investigate"
                value={`${readinessCounts.investigate} workloads`}
              />
            </div>

            <div className="w-full h-3 rounded-full bg-slate-100 overflow-hidden flex">
              <div
                className="h-full bg-sky-500"
                style={{ width: `${readinessPercents.rehost}%` }}
              />
              <div
                className="h-full bg-emerald-500"
                style={{ width: `${readinessPercents.refactor}%` }}
              />
              <div
                className="h-full bg-amber-400"
                style={{ width: `${readinessPercents.investigate}%` }}
              />
            </div>

            <p className="mt-2 text-[11px] text-slate-500 leading-snug">
              Strategy mix based on discovered workloads. Drill into details in
              the <span className="font-medium">Insights</span> workspace as
              the engine comes online.
            </p>
          </div>
        </div>
      </div>

      {/* Bottom row: assessments + activity */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Assessments table */}
        <div className="xl:col-span-2 border border-slate-200 bg-white rounded-xl shadow-sm">
          <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-slate-900">
                Recent assessments
              </h2>
              <p className="text-xs text-slate-600">
                Open an assessment to review ingestion, insights, and reports.
              </p>
            </div>
            <span className="text-xs text-slate-500">
              Click any row to open
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <Th>Assessment</Th>
                  <Th>Client</Th>
                  <Th>Environment</Th>
                  <Th>Status</Th>
                  <Th align="right">Last updated</Th>
                </tr>
              </thead>
              <tbody>
                {mockAssessments.map((assessment, idx) => (
                  <tr
                    key={assessment.id}
                    className={`cursor-pointer ${
                      idx % 2 === 0
                        ? "bg-white hover:bg-slate-50"
                        : "bg-slate-50/40 hover:bg-slate-100"
                    }`}
                    onClick={() => openAssessment(assessment.id)}
                  >
                    <Td>
                      <span className="text-slate-900">
                        {assessment.name}
                      </span>
                    </Td>
                    <Td>{assessment.client}</Td>
                    <Td>
                      <span className="inline-flex items-center gap-1">
                        <span className="h-2 w-2 rounded-full bg-slate-400" />
                        <span>{assessment.environment}</span>
                      </span>
                    </Td>
                    <Td>
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          statusStyles[assessment.status]
                        }`}
                      >
                        {assessment.status}
                      </span>
                    </Td>
                    <Td align="right">{assessment.lastUpdated}</Td>
                  </tr>
                ))}

                {mockAssessments.length === 0 && (
                  <tr>
                    <td
                      colSpan={5}
                      className="px-4 py-6 text-center text-sm text-slate-500"
                    >
                      No assessments yet. Click{" "}
                      <button
                        onClick={handleStart}
                        className="text-sky-600 hover:underline"
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

        {/* Activity feed */}
        <div className="border border-slate-200 bg-white rounded-xl shadow-sm flex flex-col">
          <div className="px-4 py-3 border-b border-slate-200">
            <h2 className="text-sm font-semibold text-slate-900">
              Recent activity
            </h2>
            <p className="text-xs text-slate-600">
              Key ingestion, analysis, and reporting events.
            </p>
          </div>
          <div className="px-4 py-3 space-y-3 text-sm flex-1">
            {mockActivity.map((item) => (
              <div key={item.id} className="flex items-start gap-2">
                <div className="mt-1 h-2.5 w-2.5 rounded-full bg-sky-500" />
                <div>
                  <p className="text-slate-800">{item.text}</p>
                  <p className="text-xs text-slate-500">{item.time}</p>
                </div>
              </div>
            ))}

            {mockActivity.length === 0 && (
              <p className="text-xs text-slate-500">
                No recent activity yet. Ingestion runs, diagrams, and report
                exports will appear here.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ---------- New section: Data Readiness & Coverage ---------- */

function DataReadinessSection() {
  return (
    <div className="border border-slate-200 bg-white rounded-xl shadow-sm p-4 space-y-4">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">
            Data Readiness & Coverage
          </h2>
          <p className="text-xs text-slate-600">
            Completeness of your 10 ingestion slices across all active
            assessments. Higher coverage unlocks better insights, diagrams,
            and cost modeling.
          </p>
        </div>
        <div className="text-xs text-slate-600">
          <span className="font-semibold text-slate-900">
            {completedSlices} of {ingestionSlices.length} slices complete
          </span>{" "}
          <span className="text-slate-500">({readinessPct}% coverage)</span>
        </div>
      </div>

      <div>
        <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-emerald-500"
            style={{ width: `${readinessPct}%` }}
          />
        </div>
        <p className="text-[11px] text-slate-500 mt-1">
          Focus next on ingesting{" "}
          <span className="font-medium">
            storage, databases, and applications
          </span>{" "}
          to unlock full analysis.
        </p>
      </div>

      <div className="overflow-x-auto">
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
            {ingestionSlices.map((slice, idx) => (
              <tr
                key={slice.id}
                className={
                  idx % 2 === 0
                    ? "bg-white"
                    : "bg-slate-50/60"
                }
              >
                <td className="px-3 py-2 text-slate-800 whitespace-nowrap">
                  {slice.label}
                </td>
                <td className="px-3 py-2 whitespace-nowrap">
                  <span
                    className={`px-2 py-0.5 rounded-full text-[11px] font-medium ${
                      sliceStatusStyles[slice.status]
                    }`}
                  >
                    {slice.status}
                  </span>
                </td>
                <td className="px-3 py-2 text-right text-slate-800 whitespace-nowrap">
                  {slice.items}
                </td>
                <td className="px-3 py-2 text-slate-500 whitespace-nowrap">
                  {slice.updated ?? "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ---------- Small components ---------- */

function KpiCard(props: {
  label: string;
  value: string;
  sublabel?: string;
  highlight?: boolean;
  icon?: string;
}) {
  const { label, value, sublabel, highlight, icon } = props;
  return (
    <div
      className={`border border-slate-200 rounded-xl px-4 py-4 shadow-sm flex flex-col justify-between ${
        highlight ? "bg-sky-50" : "bg-white"
      }`}
    >
      <div className="flex items-center justify-between">
        <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">
          {label}
        </p>
        {icon && (
          <span className="text-lg" aria-hidden="true">
            {icon}
          </span>
        )}
      </div>
      <p className="text-2xl font-semibold text-slate-900 mt-2">{value}</p>
      {sublabel && (
        <p className="text-xs text-slate-500 mt-1 leading-snug">
          {sublabel}
        </p>
      )}
    </div>
  );
}

function PipelineStep(props: {
  label: string;
  status: "In Progress" | "Planned" | "Completed";
  description: string;
}) {
  const { label, status, description } = props;

  const statusBadge =
    status === "Completed"
      ? "bg-emerald-100 text-emerald-800"
      : status === "In Progress"
      ? "bg-sky-100 text-sky-800"
      : "bg-slate-100 text-slate-700";

  return (
    <li className="flex items-start gap-3">
      <div className="mt-1 h-2.5 w-2.5 rounded-full bg-sky-500" />
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-slate-900">
            {label}
          </span>
          <span
            className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${statusBadge}`}
          >
            {status}
          </span>
        </div>
        <p className="text-xs text-slate-600 mt-0.5 leading-snug">
          {description}
        </p>
      </div>
    </li>
  );
}

function InsightStat(props: {
  label: string;
  value: string;
  note?: string;
}) {
  const { label, value, note } = props;
  return (
    <div className="border border-slate-200 rounded-lg px-3 py-3 bg-slate-50">
      <p className="text-[11px] text-slate-500">{label}</p>
      <p className="text-xl font-semibold text-slate-900 mt-1">
        {value}
      </p>
      {note && (
        <p className="text-[11px] text-slate-500 mt-0.5">{note}</p>
      )}
    </div>
  );
}

function StrategyLegend({
  colorClass,
  label,
  value,
}: {
  colorClass: string;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center gap-2">
      <span className={`w-3.5 h-3.5 rounded-sm ${colorClass}`} />
      <span className="text-xs font-semibold text-slate-900">
        {label}
      </span>
      <span className="text-[11px] text-slate-600">{value}</span>
    </div>
  );
}

function Th({
  children,
  align = "left",
}: {
  children: React.ReactNode;
  align?: "left" | "right";
}) {
  return (
    <th
      className={`px-4 py-2 text-xs font-medium text-slate-600 uppercase tracking-wide ${
        align === "right" ? "text-right" : "text-left"
      }`}
    >
      {children}
    </th>
  );
}

function Td({
  children,
  align = "left",
}: {
  children: React.ReactNode;
  align?: "left" | "right";
}) {
  return (
    <td
      className={`px-4 py-2 text-sm text-slate-800 whitespace-nowrap ${
        align === "right" ? "text-right" : "text-left"
      }`}
    >
      {children}
    </td>
  );
}
