import React, { useEffect, useState } from "react";
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

const statusStyles: Record<AssessmentStatus, string> = {
  "Not Started": "bg-gray-200 text-gray-700",
  "In Progress": "bg-blue-200 text-blue-800",
  Completed: "bg-green-200 text-green-800",
  Error: "bg-red-200 text-red-800",
};

// Backend base for run registry
const RUNS_API_BASE = "/v1/run_registry"; // adjust if you later mount backend under /api

export default function RunsPage() {
  const navigate = useNavigate();

  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [listError, setListError] = useState<string | null>(null);

  const [creating, setCreating] = useState<boolean>(false);
  const [createError, setCreateError] = useState<string | null>(null);

  // Map backend state -> UI status pill
  const mapStateToStatus = (state: string): AssessmentStatus => {
    switch (state) {
      case "created":
        return "Not Started";
      case "completed":
        return "Completed";
      case "error":
        return "Error";
      // if you later add "ingesting", "analysis", etc., they will fall here:
      default:
        return "In Progress";
    }
  };

  // Load runs from backend
  useEffect(() => {
    let cancelled = false;

    const loadRuns = async () => {
      setLoading(true);
      setListError(null);
      try {
        const res = await fetch(RUNS_API_BASE);
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        const data: RunRecordApi[] = await res.json();

        if (cancelled) return;

        const mapped: Assessment[] = data.map((r) => ({
          id: r.id,
          name: r.name || "Untitled assessment",
          // For now, we don't have a real client/environment in RunRecord.
          // We use 'source' as a stand-in for client, and leave environment blank.
          client: r.source || "Unknown source",
          environment: "—",
          status: mapStateToStatus(r.state),
          lastUpdated: new Date(r.created_at).toLocaleString(),
        }));

        setAssessments(mapped);
      } catch (err) {
        console.error("Error loading runs", err);
        if (!cancelled) {
          setListError("Unable to load assessments. Please try again.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadRuns();

    return () => {
      cancelled = true;
    };
  }, []);

  // Start new assessment → POST to backend, then navigate to /runs/:id
  const handleStart = async () => {
    if (creating) return;
    setCreating(true);
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
        throw new Error("Backend did not return an id for the new run.");
      }

      // Navigate to the new run detail page
      navigate(`/runs/${data.id}`);
    } catch (err) {
      console.error("Error creating run", err);
      setCreateError(
        "Could not start a new assessment. Please try again."
      );
    } finally {
      setCreating(false);
    }
  };

  const openAssessment = (id: string) => navigate(`/runs/${id}`);

  const activeCount = assessments.filter(
    (a) => a.status === "In Progress"
  ).length;

  return (
    <div className="px-6 py-6 space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">
            Assessments
          </h1>
          <p className="text-sm text-gray-600">
            View and manage all migration assessments in CloudReadyAI.
          </p>
        </div>

        <div className="flex flex-col items-end gap-1">
          <button
            onClick={handleStart}
            disabled={creating}
            className="bg-blue-600 text-white px-4 py-2 rounded-md shadow hover:bg-blue-700 text-sm font-medium disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {creating ? "Creating..." : "Start New Assessment"}
          </button>
          {createError && (
            <p className="text-xs text-red-600">{createError}</p>
          )}
        </div>
      </div>

      {/* Summary panel */}
      <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4 flex justify-between items-center">
        <div>
          <h2 className="text-sm font-medium text-gray-900">
            Assessment overview
          </h2>
          <p className="text-xs text-gray-600">
            Track the status of each migration assessment, including names,
            sources, and last activity.
          </p>
        </div>
        <div className="text-right text-xs text-gray-500">
          <div>Total assessments: {assessments.length}</div>
          <div>Active (In Progress): {activeCount}</div>
        </div>
      </div>

      {/* Error message for list */}
      {listError && (
        <div className="border border-red-200 bg-red-50 text-red-700 text-sm rounded-md px-3 py-2">
          {listError}
        </div>
      )}

      {/* Assessments table */}
      <div className="border border-gray-200 bg-white rounded-md shadow-sm">
        <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-sm font-medium text-gray-900">
            All assessments
          </h2>
          {/* Placeholder for future filters */}
          <span className="text-xs text-gray-500">
            Filters and search coming soon
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <TableHeader>Assessment</TableHeader>
                <TableHeader>Source</TableHeader>
                <TableHeader>Environment</TableHeader>
                <TableHeader>Status</TableHeader>
                <TableHeader align="right">Last updated</TableHeader>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td
                    colSpan={5}
                    className="px-4 py-6 text-center text-sm text-gray-500"
                  >
                    Loading assessments…
                  </td>
                </tr>
              )}

              {!loading && assessments.length === 0 && !listError && (
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

              {!loading &&
                assessments.map((assessment) => (
                  <tr
                    key={assessment.id}
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => openAssessment(assessment.id)}
                  >
                    <TableCell>{assessment.name}</TableCell>
                    <TableCell>{assessment.client}</TableCell>
                    <TableCell>{assessment.environment}</TableCell>
                    <TableCell>
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          statusStyles[assessment.status]
                        }`}
                      >
                        {assessment.status}
                      </span>
                    </TableCell>
                    <TableCell align="right">
                      {assessment.lastUpdated}
                    </TableCell>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>
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
