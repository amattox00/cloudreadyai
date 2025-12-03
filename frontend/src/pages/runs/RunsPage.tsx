import React, { useEffect, useState } from "react";

type RunItem = {
  id: string;
  label?: string;
  created_at?: string;
  status?: string;
};

export default function RunsPage() {
  const [runs, setRuns] = useState<RunItem[]>([]);
  const [selectedRun, setSelectedRun] = useState<RunItem | null>(null);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  // In future phases these will be populated from /v1/runs/<id>/summary + /analysis
  const [summaryText, setSummaryText] = useState<string>(
    "Select a run on the left to view summary. This will use /v1/runs/<id>/summary in Phase B3/C."
  );
  const [analysisText, setAnalysisText] = useState<string>(
    "Select a run on the left to view analysis. This will use /v1/runs/<id>/analysis in Phase C."
  );

  useEffect(() => {
    async function loadRuns() {
      setIsLoadingHistory(true);
      setHistoryError(null);

      try {
        const res = await fetch("/v1/runs");

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }

        // The backend might not be returning JSON yet; guard the parse.
        let data: any;
        try {
          data = await res.json();
        } catch (err) {
          console.error("Failed to parse /v1/runs as JSON:", err);
          throw new Error(
            "Backend returned a non-JSON response. This is expected if /v1/runs is not wired yet."
          );
        }

        const items: RunItem[] = Array.isArray(data)
          ? data
          : Array.isArray(data?.items)
          ? data.items
          : [];

        setRuns(items);
      } catch (err: any) {
        console.error("Error loading run history:", err);
        setHistoryError(
          err?.message ||
            "Unable to load run history. This may be expected in dev while /v1/runs is still being wired up."
        );
      } finally {
        setIsLoadingHistory(false);
      }
    }

    loadRuns();
  }, []);

  function handleSelect(run: RunItem) {
    setSelectedRun(run);

    // For now, just show descriptive placeholders.
    const label = run.label || run.id;
    setSummaryText(
      `Summary for run "${label}" will appear here once /v1/runs/${run.id}/summary is connected.`
    );
    setAnalysisText(
      `Analysis for run "${label}" will appear here once /v1/runs/${run.id}/analysis is connected.`
    );
  }

  return (
    <div className="space-y-6">
      <div className="panel p-4">
        <h1 className="text-2xl font-semibold mb-1">Runs</h1>
        <p className="text-sm text-[var(--text-muted)]">
          Each run represents a single CloudReadyAI assessment. This surfaces
          Phase B ingestion and Phase C analysis for a given run.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Run history list */}
        <section className="panel p-4 lg:col-span-1">
          <h2 className="text-lg font-semibold mb-2">Run History</h2>

          {isLoadingHistory && (
            <p className="text-sm text-[var(--text-muted)]">
              Loading runs from <code>/v1/runs</code>…
            </p>
          )}

          {historyError && (
            <p className="text-sm text-red-600 whitespace-pre-line">
              {historyError}
            </p>
          )}

          {!isLoadingHistory && !historyError && runs.length === 0 && (
            <p className="text-sm text-[var(--text-muted)]">
              No runs found yet. Once ingestion jobs are executed, they will
              appear here.
            </p>
          )}

          <ul className="mt-3 space-y-1">
            {runs.map((run) => {
              const isActive = selectedRun && selectedRun.id === run.id;
              return (
                <li key={run.id}>
                  <button
                    type="button"
                    onClick={() => handleSelect(run)}
                    className={`w-full text-left px-3 py-2 rounded-md border ${
                      isActive
                        ? "bg-accent text-white"
                        : "bg-white hover-bg-accent-ghost"
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-medium">
                        {run.label || run.id}
                      </span>
                      {run.status && (
                        <span className="text-xs text-[var(--text-muted)]">
                          {run.status}
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-[var(--text-muted)] mt-0.5">
                      ID: {run.id}
                      {run.created_at ? ` • ${run.created_at}` : null}
                    </div>
                  </button>
                </li>
              );
            })}
          </ul>
        </section>

        {/* Details / Summary / Analysis */}
        <div className="lg:col-span-2 space-y-4">
          <section className="panel p-4">
            <h2 className="text-lg font-semibold mb-2">Run Details</h2>
            {selectedRun ? (
              <div className="space-y-1 text-sm">
                <div>
                  <span className="font-semibold">ID:</span> {selectedRun.id}
                </div>
                {selectedRun.label && (
                  <div>
                    <span className="font-semibold">Label:</span>{" "}
                    {selectedRun.label}
                  </div>
                )}
                {selectedRun.status && (
                  <div>
                    <span className="font-semibold">Status:</span>{" "}
                    {selectedRun.status}
                  </div>
                )}
                {selectedRun.created_at && (
                  <div>
                    <span className="font-semibold">Created:</span>{" "}
                    {selectedRun.created_at}
                  </div>
                )}
                <p className="text-xs text-[var(--text-muted)] mt-2">
                  In later phases this card will surface additional metadata
                  from the run record (e.g., ingestion sources, environment,
                  scenario tags).
                </p>
              </div>
            ) : (
              <p className="text-sm text-[var(--text-muted)]">
                Select a run on the left to inspect its details.
              </p>
            )}
          </section>

          <section className="panel p-4">
            <h2 className="text-lg font-semibold mb-2">Summary</h2>
            <p className="text-sm whitespace-pre-line">{summaryText}</p>
          </section>

          <section className="panel p-4">
            <h2 className="text-lg font-semibold mb-2">Analysis</h2>
            <p className="text-sm whitespace-pre-line">{analysisText}</p>
          </section>
        </div>
      </div>
    </div>
  );
}
