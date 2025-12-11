import React from "react";
import { useNavigate } from "react-router-dom";

type AssessmentStatus = "Not Started" | "In Progress" | "Completed" | "Error";

interface Assessment {
  id: string;
  name: string;
  client: string;
  environment: string;
  status: AssessmentStatus;
  lastUpdated: string;
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
  investigate: Math.round((readinessCounts.investigate / totalWorkloads) * 100),
};

export default function DashboardPage() {
  const navigate = useNavigate();

  const handleStart = () => navigate("/runs/new");
  const openAssessment = (id: string) => navigate(`/runs/${id}`);

  const activeCount = mockAssessments.filter(
    (a) => a.status === "In Progress"
  ).length;

  return (
    <div className="px-6 py-6 space-y-8">
      {/* Hero header */}
      <div className="border border-gray-200 bg-gradient-to-r from-gray-50 to-white rounded-lg shadow-sm px-6 py-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">
            Your cloud migration command center
          </h1>
          <p className="text-sm text-gray-600 mt-1 max-w-xl">
            Track assessments, ingestion, and cost modeling in one place. Use
            CloudReadyAI to turn raw infrastructure data into migration-ready
            plans.
          </p>
        </div>
        <div className="flex flex-col items-stretch sm:flex-row sm:items-center gap-3">
          <div className="text-xs text-gray-500 text-right sm:text-left">
            <div>Active assessments: {activeCount}</div>
            <div>Total clients: 2 · Portfolios: 3</div>
            <div>Workspace: dev</div>
          </div>
          <button
            onClick={handleStart}
            className="bg-blue-600 text-white px-4 py-2 rounded-md shadow hover:bg-blue-700 text-sm font-medium"
          >
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
        />
        <KpiCard
          label="Total assessments"
          value={String(mockAssessments.length)}
          sublabel="Historical and in-flight assessments"
        />
        <KpiCard
          label="Environment data collected"
          value="32 servers, 4 apps"
          sublabel="Latest ingestion across all environments"
        />
        <KpiCard
          label="Cost snapshots"
          value="0 snapshots"
          sublabel="Generate from any completed assessment"
        />
      </div>

      {/* Middle row: pipeline + insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Migration pipeline */}
        <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4">
          <h2 className="text-sm font-medium text-gray-900">
            Migration pipeline
          </h2>
          <p className="text-xs text-gray-600">
            See where your assessments sit in the end-to-end CloudReadyAI
            workflow.
          </p>

          {/* Simple progress bar */}
          <div className="mt-3">
            <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500"
                style={{ width: `${pipelineProgressPct}%` }}
              />
            </div>
            <p className="text-[11px] text-gray-500 mt-1">
              {completedOrActiveCount} of {pipelineStages.length} stages active
              or completed ({pipelineProgressPct}%)
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

        {/* Migration Insights Snapshot */}
        <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4">
          <h2 className="text-sm font-medium text-gray-900">
            Migration Insights Snapshot
          </h2>
          <p className="text-xs text-gray-600">
            Early view of how discovered workloads align to migration strategies.
            Values are illustrative until the Insights engine is fully wired.
          </p>

          {/* Top stats row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 my-4">
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

          {/* Migration Strategy Preview card */}
          <div className="border border-dashed border-gray-300 rounded-md px-5 py-4 text-xs text-gray-600">
            <p className="mb-2 text-sm font-medium text-gray-800">
              Migration Strategy Preview
            </p>

            <div className="flex flex-wrap items-center gap-4 mb-3">
              <StrategyLegend
                colorClass="bg-blue-500"
                label="Rehost"
                value={`${readinessCounts.rehost} workloads`}
              />
              <StrategyLegend
                colorClass="bg-green-500"
                label="Refactor"
                value={`${readinessCounts.refactor} workloads`}
              />
              <StrategyLegend
                colorClass="bg-yellow-400"
                label="Investigate"
                value={`${readinessCounts.investigate} workloads`}
              />
            </div>

            <div className="w-full h-3 rounded-full bg-gray-100 overflow-hidden flex">
              <div
                className="h-full bg-blue-500"
                style={{ width: `${readinessPercents.rehost}%` }}
              />
              <div
                className="h-full bg-green-500"
                style={{ width: `${readinessPercents.refactor}%` }}
              />
              <div
                className="h-full bg-yellow-400"
                style={{ width: `${readinessPercents.investigate}%` }}
              />
            </div>

            <p className="mt-2 text-[11px] text-gray-500">
              Distribution of workloads by proposed migration strategy. Detailed
              insights per workload group will be available in the Insights
              workspace.
            </p>
          </div>
        </div>
      </div>

      {/* Recent assessments + activity */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Recent assessments (2/3 width) */}
        <div className="xl:col-span-2 border border-gray-200 bg-white rounded-md shadow-sm">
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
            <span className="text-xs text-gray-500">
              Click any row to open
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <Th>Assessment</Th>
                  <Th>Client</Th>
                  <Th>Environment</Th>
                  <Th>Status</Th>
                  <Th align="right">Last updated</Th>
                </tr>
              </thead>
              <tbody>
                {mockAssessments.map((assessment) => (
                  <tr
                    key={assessment.id}
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => openAssessment(assessment.id)}
                  >
                    <Td>
                      <div className="flex flex-col">
                        <span className="text-gray-900">
                          {assessment.name}
                        </span>
                      </div>
                    </Td>
                    <Td>{assessment.client}</Td>
                    <Td>
                      <span className="inline-flex items-center gap-1">
                        <span className="h-2 w-2 rounded-full bg-gray-400" />
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
                      className="px-4 py-6 text-center text-sm text-gray-500"
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
              </tbody>
            </table>
          </div>
        </div>

        {/* Activity feed (1/3 width) */}
        <div className="border border-gray-200 bg-white rounded-md shadow-sm flex flex-col">
          <div className="px-4 py-3 border-b border-gray-200">
            <h2 className="text-sm font-medium text-gray-900">
              Recent activity
            </h2>
            <p className="text-xs text-gray-600">
              Key ingestion, analysis, and reporting events.
            </p>
          </div>
          <div className="px-4 py-3 space-y-3 text-sm flex-1">
            {mockActivity.map((item) => (
              <div key={item.id} className="flex items-start gap-2">
                <div className="mt-1 h-2 w-2 rounded-full bg-blue-500" />
                <div>
                  <p className="text-gray-800">{item.text}</p>
                  <p className="text-xs text-gray-500">{item.time}</p>
                </div>
              </div>
            ))}

            {mockActivity.length === 0 && (
              <p className="text-xs text-gray-500">
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

/* ---------- Small components ---------- */

function KpiCard(props: {
  label: string;
  value: string;
  sublabel?: string;
  highlight?: boolean;
}) {
  const { label, value, sublabel, highlight } = props;
  return (
    <div
      className={`border border-gray-200 rounded-md px-4 py-4 shadow-sm flex flex-col justify-between ${
        highlight ? "bg-blue-50" : "bg-white"
      }`}
    >
      <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">
        {label}
      </p>
      <p className="text-2xl font-semibold text-gray-900 mt-2">{value}</p>
      {sublabel && (
        <p className="text-xs text-gray-500 mt-1">{sublabel}</p>
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
      ? "bg-green-100 text-green-800"
      : status === "In Progress"
      ? "bg-blue-100 text-blue-800"
      : "bg-gray-100 text-gray-700";

  return (
    <li className="flex items-start gap-3">
      <div className="mt-1 h-2.5 w-2.5 rounded-full bg-blue-500" />
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-900">
            {label}
          </span>
          <span
            className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${statusBadge}`}
          >
            {status}
          </span>
        </div>
        <p className="text-xs text-gray-600 mt-0.5">{description}</p>
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
    <div className="border border-gray-200 rounded-md px-3 py-3 bg-gray-50">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-lg font-semibold text-gray-900 mt-1">
        {value}
      </p>
      {note && (
        <p className="text-[11px] text-gray-500 mt-0.5">{note}</p>
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
      <span className="text-xs font-semibold text-gray-800">
        {label}
      </span>
      <span className="text-[11px] text-gray-600">{value}</span>
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
      className={`px-4 py-2 text-xs font-medium text-gray-600 uppercase tracking-wide ${
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
      className={`px-4 py-2 text-sm text-gray-800 whitespace-nowrap ${
        align === "right" ? "text-right" : "text-left"
      }`}
    >
      {children}
    </td>
  );
}
