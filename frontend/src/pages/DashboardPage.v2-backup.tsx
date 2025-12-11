import React from "react";
import { useNavigate } from "react-router-dom";

type AssessmentStatus = "Not Started" | "In Progress" | "Completed" | "Error";

interface Assessment {
  id: string;
  name: string;
  environment: string;
  status: AssessmentStatus;
  lastUpdated: string;
}

const mockAssessments: Assessment[] = [
  {
    id: "run-001",
    name: "US-East Datacenter Migration",
    environment: "VMware · Production",
    status: "In Progress",
    lastUpdated: "5 minutes ago",
  },
  {
    id: "run-002",
    name: "Finance Apps Modernization",
    environment: "Hybrid · Non-Prod",
    status: "Completed",
    lastUpdated: "1 day ago",
  },
  {
    id: "run-003",
    name: "Legacy Workloads Review",
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

export default function DashboardPage() {
  const navigate = useNavigate();

  const handleStart = () => navigate("/runs/new");

  const openAssessment = (id: string) => navigate(`/runs/${id}`);

  return (
    <div className="px-6 py-6 space-y-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">
            CloudReadyAI Dashboard
          </h1>
          <p className="text-sm text-gray-600">
            Your cloud migration assessment workspace
          </p>
        </div>

        <button
          onClick={handleStart}
          className="bg-blue-600 text-white px-4 py-2 rounded-md shadow hover:bg-blue-700 text-sm font-medium"
        >
          Start New Assessment
        </button>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Active Assessments" value="1" />
        <MetricCard title="Total Assessments" value="3" />
        <MetricCard title="Environment Data Collected" value="32 servers, 4 apps" />
        <MetricCard title="Latest Cost Snapshot" value="Not generated yet" />
      </div>

      {/* Recent Assessments */}
      <div className="border border-gray-200 bg-white shadow-sm rounded-md">
        <div className="px-4 py-3 border-b border-gray-200">
          <h2 className="text-sm font-medium text-gray-800">Recent Assessments</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <TableHeader>Assessment Name</TableHeader>
                <TableHeader>Environment</TableHeader>
                <TableHeader>Status</TableHeader>
                <TableHeader align="right">Last Updated</TableHeader>
              </tr>
            </thead>

            <tbody>
              {mockAssessments.map((assessment) => (
                <tr
                  key={assessment.id}
                  className="hover:bg-gray-50 cursor-pointer"
                  onClick={() => openAssessment(assessment.id)}
                >
                  <TableCell>{assessment.name}</TableCell>
                  <TableCell>{assessment.environment}</TableCell>
                  <TableCell>
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusStyles[assessment.status]}`}
                    >
                      {assessment.status}
                    </span>
                  </TableCell>
                  <TableCell align="right">{assessment.lastUpdated}</TableCell>
                </tr>
              ))}

              {mockAssessments.length === 0 && (
                <tr>
                  <td
                    colSpan={4}
                    className="px-4 py-6 text-center text-gray-500 text-sm"
                  >
                    No assessments yet. Click{" "}
                    <button
                      onClick={handleStart}
                      className="text-blue-600 hover:underline"
                    >
                      Start New Assessment
                    </button>{" "}
                    to begin.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Migration Journey */}
      <div className="border border-gray-200 bg-white rounded-md shadow-sm">
        <div className="px-4 py-3 border-b border-gray-200">
          <h2 className="text-sm font-medium text-gray-800">Your Migration Journey</h2>
          <p className="text-xs text-gray-600">
            Follow this guided process to complete your cloud migration assessment.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 p-4">
          <JourneyStep
            step={1}
            title="Import Environment Data"
            text="Upload CSVs or integrate collectors to gather infrastructure inventory."
          />
          <JourneyStep
            step={2}
            title="Review Assessment Summary"
            text="Confirm environment details and validate discovered resources."
          />
          <JourneyStep
            step={3}
            title="Generate Workload Insights"
            text="Explore readiness scoring, dependencies, and migration groupings."
          />
          <JourneyStep
            step={4}
            title="Review Cloud Cost Model"
            text="Compare AWS, Azure, and GCP cost scenarios."
          />
          <JourneyStep
            step={5}
            title="Download Executive Report"
            text="Export your migration plan, diagrams, and recommendations."
          />
        </div>
      </div>
    </div>
  );
}

/* Reusable Components */
function MetricCard({ title, value }: { title: string; value: string }) {
  return (
    <div className="border border-gray-200 bg-white rounded-md px-4 py-4 shadow-sm">
      <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">
        {title}
      </p>
      <p className="text-lg font-semibold text-gray-900 mt-1">{value}</p>
    </div>
  );
}

function TableHeader({
  children,
  align = "left",
}: {
  children: React.ReactNode;
  align?: "left" | "right";
}) {
  return (
    <th
      className={`px-4 py-2 text-xs font-medium text-gray-600 uppercase tracking-wide text-${align}`}
    >
      {children}
    </th>
  );
}

function TableCell({
  children,
  align = "left",
}: {
  children: React.ReactNode;
  align?: "left" | "right";
}) {
  return (
    <td
      className={`px-4 py-2 text-sm text-gray-800 text-${align} whitespace-nowrap`}
    >
      {children}
    </td>
  );
}

function JourneyStep({
  step,
  title,
  text,
}: {
  step: number;
  title: string;
  text: string;
}) {
  return (
    <div className="border border-gray-200 rounded-md bg-gray-50 p-4 shadow-sm">
      <div className="flex items-center gap-2 mb-2">
        <span className="h-6 w-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-semibold">
          {step}
        </span>
        <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
      </div>
      <p className="text-xs text-gray-600">{text}</p>
    </div>
  );
}
