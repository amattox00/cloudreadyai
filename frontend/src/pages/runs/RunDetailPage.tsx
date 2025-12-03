import React, { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { RunWorkloadsTab } from "../../components/runs/RunWorkloadsTab";
import {
  generateAllReports,
  getReportsPackageUrl,
} from "../../api/reports";

type TabId = "overview" | "workloads" | "reports";

export default function RunDetailPage() {
  const { runId } = useParams<{ runId: string }>();
  const [activeTab, setActiveTab] = useState<TabId>("overview");

  const [isGeneratingReports, setIsGeneratingReports] = useState(false);
  const [lastGeneratedAt, setLastGeneratedAt] = useState<string | null>(null);
  const [reportError, setReportError] = useState<string | null>(null);

  if (!runId) {
    return (
      <div className="p-6">
        <p className="text-sm text-red-600">
          No run ID provided in route. Go back to{" "}
          <Link to="/runs" className="text-blue-600 underline">
            Runs
          </Link>
          .
        </p>
      </div>
    );
  }

  async function handleGenerateReports() {
    if (!runId) return;

    setIsGeneratingReports(true);
    setReportError(null);

    try {
      await generateAllReports(runId);
      setLastGeneratedAt(new Date().toLocaleString());
    } catch (err: any) {
      console.error("Failed to generate reports", err);
      setReportError(err?.message ?? "Failed to generate reports.");
      alert("Failed to generate reports. Check console/logs for details.");
    } finally {
      setIsGeneratingReports(false);
    }
  }

  return (
    <div className="p-6 space-y-4">
      {/* Header / breadcrumb */}
      <div className="flex items-center justify-between gap-2">
        <div className="space-y-1">
          <div className="text-xs text-gray-500">
            <Link to="/runs" className="text-blue-600 hover:underline">
              Runs
            </Link>{" "}
            / <span className="text-gray-600">Run Detail</span>
          </div>
          <h1 className="text-xl font-semibold">Run Details</h1>
          <p className="text-sm text-gray-500">Run ID: {runId}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-4 text-sm">
          <button
            className={`px-3 py-2 border-b-2 ${
              activeTab === "overview"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
            onClick={() => setActiveTab("overview")}
          >
            Overview
          </button>
          <button
            className={`px-3 py-2 border-b-2 ${
              activeTab === "workloads"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
            onClick={() => setActiveTab("workloads")}
          >
            Workloads
          </button>
          <button
            className={`px-3 py-2 border-b-2 ${
              activeTab === "reports"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
            onClick={() => setActiveTab("reports")}
          >
            Reports
          </button>
        </nav>
      </div>

      {/* Tab content */}
      {activeTab === "overview" && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold">Overview</h2>
          <p className="text-sm text-gray-600">
            This is a placeholder overview for run{" "}
            <span className="font-mono">{runId}</span>.
          </p>
          <p className="text-sm text-gray-500">
            Later we can display summary metrics here (server counts, storage
            totals, TCO highlights, etc.). For now, use the{" "}
            <strong>Workloads</strong> tab to see the inferred application
            workloads for this assessment, and the <strong>Reports</strong> tab
            to generate client-ready deliverables.
          </p>
        </div>
      )}

      {activeTab === "workloads" && <RunWorkloadsTab runId={runId} />}

      {activeTab === "reports" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Reports</h2>
            <button
              onClick={handleGenerateReports}
              disabled={isGeneratingReports}
              className="px-3 py-1.5 text-sm font-medium rounded-md bg-purple-600 text-white disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {isGeneratingReports ? "Generating..." : "Generate All Reports"}
            </button>
          </div>

          <p className="text-sm text-gray-600">
            Generate a full CloudReadyAI assessment package for this run,
            including executive summary, technical assessment, and target cloud
            architecture in both PDF and Word formats.
          </p>

          {lastGeneratedAt && (
            <p className="text-xs text-gray-500">
              Last generated: {lastGeneratedAt}
            </p>
          )}

          {reportError && (
            <p className="text-xs text-red-600">Error: {reportError}</p>
          )}

          <div className="border border-gray-200 rounded-lg p-4 bg-white shadow-sm">
            <h3 className="text-sm font-semibold text-gray-800 mb-1">
              Download Assessment Package
            </h3>
            <p className="text-xs text-gray-600 mb-2">
              This ZIP file includes all generated reports for this run:
              Summary, Technical Assessment, Target Architecture, plus source
              document formats.
            </p>
            <a
              href={getReportsPackageUrl(runId)}
              className="inline-flex items-center text-sm font-medium text-purple-700 hover:underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              Download CloudReadyAI Assessment Package (ZIP)
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
