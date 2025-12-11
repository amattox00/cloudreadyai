import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  listRuns,
  createRun,
  deleteRun,
  RunRecord,
} from "../api/runRegistry";

type BannerType = "error" | "info";

interface BannerState {
  type: BannerType;
  message: string;
}

type AssessmentStatus = "Not Started" | "In Progress" | "Completed" | "Error";

const statusStyles: Record<AssessmentStatus, string> = {
  "Not Started": "bg-gray-200 text-gray-700",
  "In Progress": "bg-blue-200 text-blue-800",
  Completed: "bg-green-200 text-green-800",
  Error: "bg-red-200 text-red-800",
};

function mapStateToLabel(state: RunRecord["state"]): AssessmentStatus {
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
      return "Not Started";
  }
}

function formatDate(value: string) {
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString();
}

export default function RunsPage() {
  const navigate = useNavigate();

  const [runs, setRuns] = useState<RunRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [banner, setBanner] = useState<BannerState | null>(null);
  const [creating, setCreating] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setBanner(null);
      try {
        const data = await listRuns();
        // newest first
        data.sort((a, b) =>
          a.created_at < b.created_at ? 1 : -1
        );
        setRuns(data);
      } catch (err: any) {
        console.error("Failed to load assessments", err);
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
      setCreating(true);
      const run = await createRun("New assessment", "Dashboard");
      setRuns((prev) => [run, ...prev]);
      navigate(`/runs/${run.id}`);
    } catch (err: any) {
      console.error("Failed to create assessment", err);
      setBanner({
        type: "error",
        message: `Failed to create assessment: ${err.message || err}`,
      });
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (run: RunRecord) => {
    const confirmDelete = window.confirm(
      `Delete assessment "${run.name}"? This cannot be undone.`
    );
    if (!confirmDelete) return;

    try {
      setBanner(null);
      setDeletingId(run.id);
      await deleteRun(run.id);
      setRuns((prev) => prev.filter((r) => r.id !== run.id));
    } catch (err: any) {
      console.error("Failed to delete assessment", err);
      setBanner({
        type: "error",
        message: `Failed to delete assessment: ${err.message || err}`,
      });
    } finally {
      setDeletingId(null);
    }
  };

  const openAssessment = (id: string) => navigate(`/runs/${id}`);

  const totalAssessments = runs.length;
  const activeAssessments = runs.filter(
    (r) => r.state === "created" || r.state === "in_progress"
  ).length;

  return (
    <div className="px-6 py-6 space-y-6">
      {/* Banner */}
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

        <button
          onClick={handleStart}
          disabled={creating}
          className={`px-4 py-2 rounded-md shadow text-sm font-medium ${
            creating
              ? "bg-blue-300 text-white cursor-wait"
              : "bg-blue-600 text-white hover:bg-blue-700"
          }`}
        >
          {creating ? "Creating…" : "Start New Assessment"}
        </button>
      </div>

      {/* Summary panel */}
      <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4 flex justify-between items-center">
        <div>
          <h2 className="text-sm font-medium text-gray-900">
            Assessment overview
          </h2>
          <p className="text-xs text-gray-600">
            Track the status of each migration assessment, including source,
            environments, and last activity.
          </p>
        </div>
        <div className="text-right text-xs text-gray-500">
          <div>Total assessments: {totalAssessments}</div>
          <div>Active: {activeAssessments}</div>
        </div>
      </div>

      {/* Assessments table */}
      <div className="border border-gray-200 bg-white rounded-md shadow-sm">
        <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-sm font-medium text-gray-900">
            All assessments
          </h2>
          <span className="text-xs text-gray-500">
            Filters and search coming soon
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <TableHeader>Assessment</TableHeader>
                <TableHeader>Client / Source</TableHeader>
                <TableHeader>Environment</TableHeader>
                <TableHeader>Status</TableHeader>
                <TableHeader align="right">Last updated</TableHeader>
                <TableHeader align="right">Actions</TableHeader>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td
                    colSpan={6}
                    className="px-4 py-6 text-center text-sm text-gray-500"
                  >
                    Loading…
                  </td>
                </tr>
              )}

              {!loading && runs.length === 0 && (
                <tr>
                  <td
                    colSpan={6}
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

              {runs.map((run) => {
                const label = mapStateToLabel(run.state);
                return (
                  <tr
                    key={run.id}
                    className="hover:bg-gray-50"
                  >
                    <TableCell
                      onClick={() => openAssessment(run.id)}
                      className="cursor-pointer text-blue-700 hover:underline"
                    >
                      {run.name}
                    </TableCell>
                    <TableCell>{run.source}</TableCell>
                    <TableCell>—</TableCell>
                    <TableCell>
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          statusStyles[label]
                        }`}
                      >
                        {label}
                      </span>
                    </TableCell>
                    <TableCell align="right">
                      {formatDate(run.created_at)}
                    </TableCell>
                    <TableCell align="right">
                      <button
                        onClick={() => handleDelete(run)}
                        disabled={deletingId === run.id}
                        className={`text-xs px-2 py-1 rounded border ${
                          deletingId === run.id
                            ? "border-gray-300 text-gray-400 cursor-wait"
                            : "border-red-200 text-red-600 hover:bg-red-50"
                        }`}
                      >
                        {deletingId === run.id ? "Deleting…" : "Delete"}
                      </button>
                    </TableCell>
                  </tr>
                );
              })}
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
      className={`px-4 py-2 text-xs font-medium text-gray-600 uppercase tracking-wide ${
        align === "right" ? "text-right" : "text-left"
      }`}
    >
      {children}
    </th>
  );
}

function TableCell({
  children,
  align = "left",
  className = "",
  onClick,
}: {
  children: React.ReactNode;
  align?: "left" | "right";
  className?: string;
  onClick?: () => void;
}) {
  return (
    <td
      onClick={onClick}
      className={`px-4 py-2 text-sm text-gray-800 whitespace-nowrap ${
        align === "right" ? "text-right" : "text-left"
      } ${className}`}
    >
      {children}
    </td>
  );
}

