import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

/**
 * Types that mirror backend responses.
 * Adjust field names if your actual API uses different keys.
 */

interface RunListItem {
  run_id: string;
  created_at?: string;
  status?: string;
  description?: string | null;
}

interface RunRegistryResponse {
  runs: RunListItem[];
}

interface RunSummaryV2 {
  run_id: string;
  coverage_grade?: string | null;
  coverage_score?: number | null;

  // Ingestion slice counts – adjust names if needed to match API
  servers_count?: number | null;
  storage_count?: number | null;
  network_count?: number | null;
  databases_count?: number | null;
  applications_count?: number | null;
  business_metadata_count?: number | null;
  app_dependencies_count?: number | null;
  os_metadata_count?: number | null;
  licensing_count?: number | null;
  utilization_count?: number | null;

  ingestion_status?: string | null;
}

interface ServerV2 {
  hostname: string;
  os?: string | null;
  environment?: string | null;
  vcpus?: number | null;
  memory_gb?: number | null;
  storage_gb?: number | null;
}

interface RunServersV2Response {
  run_id: string;
  total_servers: number;
  servers: ServerV2[];
}

const RunsPage: React.FC = () => {
  // Run registry
  const [runs, setRuns] = useState<RunListItem[]>([]);
  const [isLoadingRuns, setIsLoadingRuns] = useState(false);
  const [runsError, setRunsError] = useState<string | null>(null);

  // Selected run
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);

  // Run summary (v2)
  const [runSummary, setRunSummary] = useState<RunSummaryV2 | null>(null);
  const [isLoadingSummary, setIsLoadingSummary] = useState(false);
  const [summaryError, setSummaryError] = useState<string | null>(null);

  // Servers (v2) for the selected run (Step 2 + Step 3)
  const [serversV2, setServersV2] = useState<ServerV2[] | null>(null);
  const [serversV2Count, setServersV2Count] = useState<number | null>(null);
  const [isLoadingServersV2, setIsLoadingServersV2] = useState(false);
  const [serversV2Error, setServersV2Error] = useState<string | null>(null);

  /**
   * Helper: API base path.
   * If your frontend already uses `/api/...` everywhere, set API_BASE = "/api".
   * If it talks directly to FastAPI on same origin, leave it as "".
   */
const API_BASE = "http://3.151.80.236:8000";

  // Load run registry
  useEffect(() => {
    setIsLoadingRuns(true);
    setRunsError(null);

    fetch(`${API_BASE}/run_registry`)
      .then(async (res) => {
        if (!res.ok) {
          const text = await res.text();
          throw new Error(text || `Failed to load runs (status ${res.status})`);
        }
        return res.json();
      })
      .then((data: RunRegistryResponse) => {
        setRuns(data.runs || []);
        if (!selectedRunId && data.runs && data.runs.length > 0) {
          setSelectedRunId(data.runs[0].run_id);
        }
      })
      .catch((err) => {
        console.error("Error loading run registry", err);
        setRunsError("Failed to load runs.");
      })
      .finally(() => {
        setIsLoadingRuns(false);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load run summary (v2) when selectedRunId changes
  useEffect(() => {
    if (!selectedRunId) {
      setRunSummary(null);
      setSummaryError(null);
      return;
    }

    setIsLoadingSummary(true);
    setSummaryError(null);

    fetch(`${API_BASE}/run_summary_v2/${selectedRunId}`)
      .then(async (res) => {
        if (!res.ok) {
          const text = await res.text();
          throw new Error(
            text || `Failed to load run summary (status ${res.status})`
          );
        }
        return res.json();
      })
      .then((data: RunSummaryV2) => {
        setRunSummary(data);
      })
      .catch((err) => {
        console.error("Error loading run summary v2", selectedRunId, err);
        setSummaryError("Failed to load run summary for this run.");
      })
      .finally(() => {
        setIsLoadingSummary(false);
      });
  }, [API_BASE, selectedRunId]);

  // Load servers (v2) when selectedRunId changes (Step 2)
  useEffect(() => {
    if (!selectedRunId) {
      setServersV2(null);
      setServersV2Count(null);
      setServersV2Error(null);
      return;
    }

    setIsLoadingServersV2(true);
    setServersV2Error(null);

    fetch(`${API_BASE}/v2/run_details/${selectedRunId}/servers`)
      .then(async (res) => {
        if (!res.ok) {
          if (res.status === 404) {
            // No v2 servers for this run – perfectly fine for legacy runs.
            setServersV2([]);
            setServersV2Count(0);
            return;
          }
          const text = await res.text();
          throw new Error(
            text || `Failed to load v2 servers (status ${res.status})`
          );
        }
        return res.json();
      })
      .then((data: RunServersV2Response | undefined) => {
        if (!data) return;
        setServersV2(data.servers);
        setServersV2Count(data.total_servers);
      })
      .catch((err) => {
        console.error("Error loading v2 servers for run", selectedRunId, err);
        setServersV2Error("Failed to load v2 servers for this run.");
      })
      .finally(() => {
        setIsLoadingServersV2(false);
      });
  }, [API_BASE, selectedRunId]);

  // Derived metrics for Run Details tile (Step 3: use v2 servers if available)
  const legacyServersCount = runSummary?.servers_count ?? 0;
  const effectiveServersCount =
    serversV2Count && serversV2Count > 0 ? serversV2Count : legacyServersCount;
  const serversMissing = effectiveServersCount === 0;

  const storageCount = runSummary?.storage_count ?? 0;
  const storageMissing = storageCount === 0;

  const networkCount = runSummary?.network_count ?? 0;
  const networkMissing = networkCount === 0;

  const databasesCount = runSummary?.databases_count ?? 0;
  const databasesMissing = databasesCount === 0;

  const applicationsCount = runSummary?.applications_count ?? 0;
  const applicationsMissing = applicationsCount === 0;

  const businessMetadataCount = runSummary?.business_metadata_count ?? 0;
  const businessMetadataMissing = businessMetadataCount === 0;

  const appDependenciesCount = runSummary?.app_dependencies_count ?? 0;
  const appDependenciesMissing = appDependenciesCount === 0;

  const osMetadataCount = runSummary?.os_metadata_count ?? 0;
  const osMetadataMissing = osMetadataCount === 0;

  const licensingCount = runSummary?.licensing_count ?? 0;
  const licensingMissing = licensingCount === 0;

  const utilizationCount = runSummary?.utilization_count ?? 0;
  const utilizationMissing = utilizationCount === 0;

  const coverageGrade = runSummary?.coverage_grade ?? "N/A";
  const coverageScore = runSummary?.coverage_score ?? null;
  const ingestionStatus = runSummary?.ingestion_status ?? "Unknown";

  const handleRunClick = (run: RunListItem) => {
    setSelectedRunId(run.run_id);
  };

  return (
    <div className="p-6 space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Runs</h1>
          <p className="text-sm text-gray-600">
            View ingestion runs, coverage, and details for your assessments.
          </p>
        </div>
        <div className="flex gap-3">
          <Link
            to="/"
            className="px-3 py-1.5 text-sm border rounded-md hover:bg-gray-50"
          >
            Back to Dashboard
          </Link>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Left: Runs table */}
        <section className="lg:col-span-2 border rounded-lg bg-white shadow-sm">
          <div className="px-4 py-3 border-b flex items-center justify-between">
            <h2 className="text-lg font-semibold">Run Registry</h2>
            {isLoadingRuns && (
              <span className="text-xs text-gray-500">Loading runs...</span>
            )}
          </div>
          {runsError && (
            <div className="px-4 py-2 text-sm text-red-600">{runsError}</div>
          )}
          {!isLoadingRuns && runs.length === 0 && !runsError && (
            <div className="px-4 py-4 text-sm text-gray-500">
              No runs found yet. Ingest some data to see runs here.
            </div>
          )}
          {runs.length > 0 && (
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-3 py-2 text-left font-medium">Run ID</th>
                    <th className="px-3 py-2 text-left font-medium">
                      Created At
                    </th>
                    <th className="px-3 py-2 text-left font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {runs.map((run) => {
                    const isSelected = run.run_id === selectedRunId;
                    return (
                      <tr
                        key={run.run_id}
                        className={`border-t cursor-pointer ${
                          isSelected ? "bg-blue-50" : "hover:bg-gray-50"
                        }`}
                        onClick={() => handleRunClick(run)}
                      >
                        <td className="px-3 py-2">{run.run_id}</td>
                        <td className="px-3 py-2 text-gray-600">
                          {run.created_at ?? "-"}
                        </td>
                        <td className="px-3 py-2 text-gray-600">
                          {run.status ?? "-"}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* Right: Run Details tile with 10 slices */}
        <section className="border rounded-lg bg-white shadow-sm">
          <div className="px-4 py-3 border-b">
            <h2 className="text-lg font-semibold">Run Details</h2>
          </div>
          <div className="px-4 py-3 space-y-3 text-sm">
            {!selectedRunId && (
              <p className="text-gray-500">
                Select a run from the left to view details.
              </p>
            )}

            {selectedRunId && (
              <>
                <div className="flex justify-between">
                  <span className="font-medium">Coverage grade</span>
                  <span className="text-gray-800">
                    {coverageGrade}
                    {coverageScore !== null && ` (${coverageScore}%)`}
                  </span>
                </div>

                <div className="flex justify-between">
                  <span className="font-medium">Run ID</span>
                  <span className="text-gray-800">{selectedRunId}</span>
                </div>

                <div className="flex justify-between">
                  <span className="font-medium">Ingestion status</span>
                  <span className="text-gray-800">{ingestionStatus}</span>
                </div>

                {isLoadingSummary && (
                  <p className="text-xs text-gray-500">
                    Loading run summary...
                  </p>
                )}
                {summaryError && (
                  <p className="text-xs text-red-600">{summaryError}</p>
                )}

                {/* 10 ingestion slices */}
                <div className="pt-2 border-t mt-2 space-y-1">
                  <p className="text-xs font-semibold text-gray-500">
                    Ingestion coverage
                  </p>

                  {/* Servers (using v2-aware count) */}
                  <div className="flex justify-between">
                    <span>Servers</span>
                    <span className="text-xs text-gray-700">
                      {serversMissing ? "• Missing" : "• Present"} | Count:{" "}
                      {effectiveServersCount}
                    </span>
                  </div>

                  {/* Storage */}
                  <div className="flex justify-between">
                    <span>Storage</span>
                    <span className="text-xs text-gray-700">
                      {storageMissing ? "• Missing" : "• Present"} | Count:{" "}
                      {storageCount}
                    </span>
                  </div>

                  {/* Network */}
                  <div className="flex justify-between">
                    <span>Network</span>
                    <span className="text-xs text-gray-700">
                      {networkMissing ? "• Missing" : "• Present"} | Count:{" "}
                      {networkCount}
                    </span>
                  </div>

                  {/* Databases */}
                  <div className="flex justify-between">
                    <span>Databases</span>
                    <span className="text-xs text-gray-700">
                      {databasesMissing ? "• Missing" : "• Present"} | Count:{" "}
                      {databasesCount}
                    </span>
                  </div>

                  {/* Applications */}
                  <div className="flex justify-between">
                    <span>Applications</span>
                    <span className="text-xs text-gray-700">
                      {applicationsMissing ? "• Missing" : "• Present"} | Count:{" "}
                      {applicationsCount}
                    </span>
                  </div>

                  {/* Business metadata */}
                  <div className="flex justify-between">
                    <span>Business metadata</span>
                    <span className="text-xs text-gray-700">
                      {businessMetadataMissing ? "• Missing" : "• Present"} |
                      Count: {businessMetadataCount}
                    </span>
                  </div>

                  {/* App dependencies */}
                  <div className="flex justify-between">
                    <span>App dependencies</span>
                    <span className="text-xs text-gray-700">
                      {appDependenciesMissing ? "• Missing" : "• Present"} |
                      Count: {appDependenciesCount}
                    </span>
                  </div>

                  {/* OS metadata */}
                  <div className="flex justify-between">
                    <span>OS metadata</span>
                    <span className="text-xs text-gray-700">
                      {osMetadataMissing ? "• Missing" : "• Present"} | Count:{" "}
                      {osMetadataCount}
                    </span>
                  </div>

                  {/* Licensing */}
                  <div className="flex justify-between">
                    <span>Licensing</span>
                    <span className="text-xs text-gray-700">
                      {licensingMissing ? "• Missing" : "• Present"} | Count:{" "}
                      {licensingCount}
                    </span>
                  </div>

                  {/* Utilization snapshot */}
                  <div className="flex justify-between">
                    <span>Utilization snapshot</span>
                    <span className="text-xs text-gray-700">
                      {utilizationMissing ? "• Missing" : "• Present"} | Count:{" "}
                      {utilizationCount}
                    </span>
                  </div>
                </div>
              </>
            )}
          </div>
        </section>
      </div>

      {/* Step 2: Servers (v2) section – fully separate from Run Details tile */}
      <section className="border rounded-lg bg-white shadow-sm mt-4">
        <div className="px-4 py-3 border-b flex items-center justify-between">
          <h2 className="text-lg font-semibold">Servers (v2)</h2>
          {selectedRunId && serversV2Count !== null && (
            <span className="text-xs text-gray-600">
              {serversV2Count} servers ingested via v2 pipeline for run{" "}
              <span className="font-mono">{selectedRunId}</span>
            </span>
          )}
        </div>
        <div className="px-4 py-3 text-sm">
          {!selectedRunId && (
            <p className="text-gray-500">
              Select a run above to view v2 server inventory.
            </p>
          )}

          {selectedRunId && isLoadingServersV2 && (
            <p className="text-gray-500">Loading v2 servers...</p>
          )}

          {selectedRunId && serversV2Error && (
            <p className="text-red-600">{serversV2Error}</p>
          )}

          {selectedRunId &&
            !isLoadingServersV2 &&
            serversV2 &&
            serversV2.length === 0 &&
            !serversV2Error && (
              <p className="text-gray-500">
                No v2 servers found for this run. This run may be using the
                legacy ingestion path or has not ingested server data yet.
              </p>
            )}

          {selectedRunId &&
            !isLoadingServersV2 &&
            serversV2 &&
            serversV2.length > 0 && (
              <div className="overflow-x-auto border rounded-md">
                <table className="min-w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 py-2 text-left font-medium">
                        Hostname
                      </th>
                      <th className="px-3 py-2 text-left font-medium">OS</th>
                      <th className="px-3 py-2 text-left font-medium">
                        Environment
                      </th>
                      <th className="px-3 py-2 text-left font-medium">vCPUs</th>
                      <th className="px-3 py-2 text-left font-medium">
                        Memory (GB)
                      </th>
                      <th className="px-3 py-2 text-left font-medium">
                        Storage (GB)
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {serversV2.map((s) => (
                      <tr key={s.hostname} className="border-t">
                        <td className="px-3 py-2">{s.hostname}</td>
                        <td className="px-3 py-2">{s.os ?? "-"}</td>
                        <td className="px-3 py-2">
                          {s.environment ?? "-"}
                        </td>
                        <td className="px-3 py-2">{s.vcpus ?? "-"}</td>
                        <td className="px-3 py-2">{s.memory_gb ?? "-"}</td>
                        <td className="px-3 py-2">{s.storage_gb ?? "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
        </div>
      </section>
    </div>
  );
};

export default RunsPage;
