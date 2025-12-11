import React, { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

type TabId =
  | "overview"
  | "ingestion"
  | "insights"
  | "diagrams"
  | "cost"
  | "reports";

type AssessmentStatus =
  | "Not Started"
  | "In Progress"
  | "Completed"
  | "Error";

interface AssessmentOverview {
  id: string;
  name: string;
  client: string;
  environment: string;
  status: AssessmentStatus;
  lastUpdated: string;
}

interface IngestionStats {
  servers: number;
  storageVolumes: number;
  databases: number;
  applications: number;
  networkDevices: number;
}

const mockAssessment: AssessmentOverview = {
  id: "run-001",
  name: "US-East Datacenter Migration",
  client: "ACME Corp",
  environment: "VMware · Production",
  status: "In Progress",
  lastUpdated: "5 minutes ago",
};

const mockIngestionStats: IngestionStats = {
  servers: 87,
  storageVolumes: 143,
  databases: 22,
  applications: 40,
  networkDevices: 15,
};

const statusStyles: Record<AssessmentStatus, string> = {
  "Not Started": "bg-gray-200 text-gray-700",
  "In Progress": "bg-blue-200 text-blue-800",
  Completed: "bg-green-200 text-green-800",
  Error: "bg-red-200 text-red-800",
};

export default function RunDetailPage() {
  const navigate = useNavigate();
  const { runId } = useParams<{ runId: string }>();
  const [activeTab, setActiveTab] = useState<TabId>("overview");

  const assessment = {
    ...mockAssessment,
    id: runId || mockAssessment.id,
  };

  const tabs: { id: TabId; label: string }[] = [
    { id: "overview", label: "Overview" },
    { id: "ingestion", label: "Ingestion" },
    { id: "insights", label: "Insights" },
    { id: "diagrams", label: "Diagrams" },
    { id: "cost", label: "Cost Modeling" },
    { id: "reports", label: "Reports" },
  ];

  const goBack = () => navigate("/runs");

  return (
    <div className="px-6 py-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <button
            onClick={goBack}
            className="text-xs text-blue-600 hover:underline mb-1"
          >
            ← Back to Assessments
          </button>
          <h1 className="text-xl font-semibold text-gray-900">
            {assessment.name}
          </h1>
          <p className="text-sm text-gray-600">
            Assessment ID:{" "}
            <span className="font-mono">{assessment.id}</span>
          </p>
        </div>

        <div className="text-right space-y-1">
          <div>
            <span
              className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${statusStyles[assessment.status]}`}
            >
              {assessment.status}
            </span>
          </div>
          <p className="text-xs text-gray-500">
            Last updated {assessment.lastUpdated}
          </p>
        </div>
      </div>

      {/* Top summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard title="Client" value={assessment.client} />
        <SummaryCard title="Environment" value={assessment.environment} />
        <SummaryCard title="Status" value={assessment.status} />
        <SummaryCard
          title="Assessment activity"
          value={`Last updated ${assessment.lastUpdated}`}
        />
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-6" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`whitespace-nowrap border-b-2 px-1 pb-2 text-sm font-medium ${
                activeTab === tab.id
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-600 hover:text-gray-800 hover:border-gray-300"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab content */}
      {activeTab === "overview" && (
        <OverviewTab
          assessment={assessment}
          ingestion={mockIngestionStats}
        />
      )}
      {activeTab === "ingestion" && (
        <IngestionTab stats={mockIngestionStats} />
      )}
      {activeTab === "insights" && (
        <PlaceholderTab title="Insights" />
      )}
      {activeTab === "diagrams" && (
        <PlaceholderTab title="Diagrams" />
      )}
      {activeTab === "cost" && (
        <PlaceholderTab title="Cost Modeling" />
      )}
      {activeTab === "reports" && (
        <PlaceholderTab title="Reports" />
      )}
    </div>
  );
}

/* ------------------------------
   Overview Tab
------------------------------ */

function OverviewTab({
  assessment,
  ingestion,
}: {
  assessment: AssessmentOverview;
  ingestion: IngestionStats;
}) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Left: Summary */}
      <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4 space-y-3">
        <h2 className="text-sm font-medium text-gray-900">
          Assessment summary
        </h2>
        <p className="text-xs text-gray-600">
          High-level details including client, environment, and ingestion
          coverage.
        </p>

        <dl className="mt-2 grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-sm">
          <div>
            <dt className="text-xs text-gray-500">Client</dt>
            <dd className="text-gray-900">
              {assessment.client}
            </dd>
          </div>

          <div>
            <dt className="text-xs text-gray-500">Environment</dt>
            <dd className="text-gray-900">
              {assessment.environment}
            </dd>
          </div>

          <div>
            <dt className="text-xs text-gray-500">Status</dt>
            <dd className="text-gray-900">
              {assessment.status}
            </dd>
          </div>

          <div>
            <dt className="text-xs text-gray-500">Last updated</dt>
            <dd className="text-gray-900">
              {assessment.lastUpdated}
            </dd>
          </div>
        </dl>
      </div>

      {/* Right: Ingestion summary */}
      <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4 space-y-3">
        <h2 className="text-sm font-medium text-gray-900">
          Ingestion coverage
        </h2>
        <p className="text-xs text-gray-600">
          Resource counts discovered for this assessment.
        </p>

        <dl className="mt-2 grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
          <SummaryStat
            label="Servers"
            value={ingestion.servers}
          />
          <SummaryStat
            label="Storage volumes"
            value={ingestion.storageVolumes}
          />
          <SummaryStat
            label="Databases"
            value={ingestion.databases}
          />
          <SummaryStat
            label="Applications"
            value={ingestion.applications}
          />
          <SummaryStat
            label="Network devices"
            value={ingestion.networkDevices}
          />
        </dl>
      </div>
    </div>
  );
}

/* ------------------------------
   Ingestion Tab (Upgraded!)
------------------------------ */

function IngestionTab({ stats }: { stats: IngestionStats }) {
  return (
    <div className="space-y-6">
      {/* Top summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <SummaryCard
          title="Servers ingested"
          value={String(stats.servers)}
        />
        <SummaryCard
          title="Storage volumes"
          value={String(stats.storageVolumes)}
        />
        <SummaryCard
          title="Databases"
          value={String(stats.databases)}
        />
        <SummaryCard
          title="Applications"
          value={String(stats.applications)}
        />
        <SummaryCard
          title="Network devices"
          value={String(stats.networkDevices)}
        />
      </div>

      {/* Chart row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard
          title="Ingestion status by resource type"
          description="Donut or bar charts showing resource mix across servers, storage, databases, applications, and network devices."
        />

        <ChartCard
          title="Utilization and trends"
          description="Time-series charts for CPU, memory, and storage utilization where available."
        />
      </div>

      {/* Chart row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard
          title="Top environments"
          description="Distribution of resources by OS, hypervisor, or platform."
        />

        <ChartCard
          title="Geographic distribution"
          description="Visualization of datacenter or region-based resource placement."
        />
      </div>

      {/* Resource breakdown table */}
      <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4">
        <h3 className="text-sm font-medium text-gray-900 mb-2">
          Resource breakdown
        </h3>
        <p className="text-xs text-gray-600 mb-4">
          High-level counts for all discovered resource categories.
        </p>

        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase tracking-wide">
                  Resource type
                </th>
                <th className="px-4 py-2 text-right text-xs font-medium text-gray-600 uppercase tracking-wide">
                  Count
                </th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase tracking-wide">
                  Notes
                </th>
              </tr>
            </thead>

            <tbody>
              <TableRow
                name="Servers"
                count={stats.servers}
                note="Physical and virtual compute instances."
              />
              <TableRow
                name="Storage volumes"
                count={stats.storageVolumes}
                note="Attached disks, LUNs, and storage objects."
              />
              <TableRow
                name="Databases"
                count={stats.databases}
                note="Database instances and schemas."
              />
              <TableRow
                name="Applications"
                count={stats.applications}
                note="Workload objects and grouped business apps."
              />
              <TableRow
                name="Network devices"
                count={stats.networkDevices}
                note="Switches, firewalls, and network appliances."
                last
              />
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

/* ------------------------------
   Shared Components
------------------------------ */

function SummaryCard({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div className="border border-gray-200 bg-white rounded-md px-4 py-4 shadow-sm">
      <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">
        {title}
      </p>
      <p className="text-lg font-semibold text-gray-900 mt-1">
        {value}
      </p>
    </div>
  );
}

function SummaryStat({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div>
      <dt className="text-xs text-gray-500">{label}</dt>
      <dd className="text-sm font-medium text-gray-900">
        {value}
      </dd>
    </div>
  );
}

function ChartCard({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4">
      <h3 className="text-sm font-medium text-gray-900 mb-2">
        {title}
      </h3>
      <p className="text-xs text-gray-600 mb-4">{description}</p>
      <div className="h-48 border border-dashed border-gray-300 rounded flex items-center justify-center text-xs text-gray-400">
        Chart placeholder
      </div>
    </div>
  );
}

function TableRow({
  name,
  count,
  note,
  last = false,
}: {
  name: string;
  count: number;
  note: string;
  last?: boolean;
}) {
  return (
    <tr className={!last ? "border-b border-gray-100" : ""}>
      <td className="px-4 py-2 text-gray-800">{name}</td>
      <td className="px-4 py-2 text-right text-gray-800">
        {count}
      </td>
      <td className="px-4 py-2 text-gray-600 text-xs">{note}</td>
    </tr>
  );
}
