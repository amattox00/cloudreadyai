import React, { useEffect, useRef, useState } from "react";

type SliceStatus = "not_started" | "partial" | "complete" | "error";

interface IngestionSlice {
  id: string;           // e.g. "servers"
  label: string;        // e.g. "Servers"
  status: SliceStatus;
  items: number;
  lastUpdated: string | null;
  error?: string | null;
}

interface RunIngestionTabProps {
  runId: string;
}

/**
 * RunIngestionTab
 *
 * UI for managing ingestion for a single assessment (run).
 * Shows all 10 slices, their status, and allows CSV uploads per slice.
 */
const RunIngestionTab: React.FC<RunIngestionTabProps> = ({ runId }) => {
  const [slices, setSlices] = useState<IngestionSlice[] | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [uploadingSliceId, setUploadingSliceId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Hidden file input so we can trigger uploads from a button
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [pendingSliceId, setPendingSliceId] = useState<string | null>(null);

  // ⚠️ Adjust these endpoints to match your backend
  const API_BASE = "/api";

  // Fetch current ingestion summary for this run
  const loadSlices = async () => {
    try {
      setLoading(true);
      setError(null);

      // Example: GET /api/runs/{runId}/ingestion/summary
      const res = await fetch(
        `${API_BASE}/runs/${encodeURIComponent(runId)}/ingestion/summary`
      );

      if (!res.ok) {
        throw new Error(`Failed to load ingestion summary (${res.status})`);
      }

      const data = await res.json();

      // Expecting something like:
      // {
      //   slices: [
      //     { id: "servers", label: "Servers", status: "complete", items: 87, last_updated: "..." },
      //     ...
      //   ]
      // }
      const mapped: IngestionSlice[] = data.slices.map((s: any) => ({
        id: s.id,
        label: s.label,
        status: s.status as SliceStatus,
        items: s.items ?? 0,
        lastUpdated: s.last_updated ?? null,
        error: s.error ?? null,
      }));

      setSlices(mapped);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to load ingestion summary.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSlices();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [runId]);

  // Handle "Upload CSV" button click → fire hidden file input
  const handleUploadClick = (sliceId: string) => {
    setPendingSliceId(sliceId);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
      fileInputRef.current.click();
    }
  };

  // Handle actual file selection and upload
  const handleFileChange: React.ChangeEventHandler<HTMLInputElement> = async (
    event
  ) => {
    const file = event.target.files?.[0];
    if (!file || !pendingSliceId) return;

    try {
      setUploadingSliceId(pendingSliceId);
      setError(null);

      const formData = new FormData();
      formData.append("file", file);
      formData.append("slice_id", pendingSliceId);

      // Example: POST /api/runs/{runId}/ingestion/upload
      // Backend should read slice_id and treat file as CSV.
      const res = await fetch(
        `${API_BASE}/runs/${encodeURIComponent(runId)}/ingestion/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!res.ok) {
        const body = await res.json().catch(() => null);
        const msg =
          body?.detail || `Upload failed for slice "${pendingSliceId}".`;
        throw new Error(msg);
      }

      // Optionally inspect response for counts/errors
      await loadSlices();
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Upload failed.");
    } finally {
      setUploadingSliceId(null);
      setPendingSliceId(null);
    }
  };

  const friendlyStatus = (status: SliceStatus): string => {
    switch (status) {
      case "complete":
        return "Complete";
      case "partial":
        return "Partial";
      case "error":
        return "Error";
      default:
        return "Not Started";
    }
  };

  const statusBadgeClasses = (status: SliceStatus): string => {
    switch (status) {
      case "complete":
        return "bg-emerald-50 text-emerald-700 border border-emerald-100";
      case "partial":
        return "bg-amber-50 text-amber-700 border border-amber-100";
      case "error":
        return "bg-rose-50 text-rose-700 border border-rose-100";
      default:
        return "bg-slate-50 text-slate-700 border border-slate-200";
    }
  };

  const statusDotClasses = (status: SliceStatus): string => {
    switch (status) {
      case "complete":
        return "bg-emerald-500";
      case "partial":
        return "bg-amber-500";
      case "error":
        return "bg-rose-500";
      default:
        return "bg-slate-400";
    }
  };

  return (
    <div className="space-y-4">
      {/* Hidden file input for uploads */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv,text/csv"
        className="hidden"
        onChange={handleFileChange}
      />

      <div>
        <h2 className="text-sm font-semibold text-slate-900">
          Ingestion overview
        </h2>
        <p className="text-xs text-slate-600 max-w-2xl">
          Upload CSVs for each data slice or connect collectors. The more slices
          you ingest, the richer your insights, diagrams, and cost models will
          be.
        </p>
      </div>

      {error && (
        <div className="text-xs text-rose-700 bg-rose-50 border border-rose-100 rounded-md px-3 py-2">
          {error}
        </div>
      )}

      <div className="border border-slate-200 bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="px-4 py-2 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="text-xs font-semibold text-slate-900 uppercase tracking-wide">
              Ingestion slices
            </h3>
            <p className="text-[11px] text-slate-600">
              Status by slice for this assessment.
            </p>
          </div>
          {loading && (
            <span className="text-[11px] text-slate-500">
              Refreshing status…
            </span>
          )}
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full text-xs">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-4 py-2 text-left font-medium text-slate-600 uppercase tracking-wide">
                  Slice
                </th>
                <th className="px-4 py-2 text-left font-medium text-slate-600 uppercase tracking-wide">
                  Status
                </th>
                <th className="px-4 py-2 text-right font-medium text-slate-600 uppercase tracking-wide">
                  Items
                </th>
                <th className="px-4 py-2 text-left font-medium text-slate-600 uppercase tracking-wide">
                  Last updated
                </th>
                <th className="px-4 py-2 text-right font-medium text-slate-600 uppercase tracking-wide">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {slices?.map((slice, idx) => (
                <tr
                  key={slice.id}
                  className={idx % 2 === 0 ? "bg-white" : "bg-slate-50/80"}
                >
                  <td className="px-4 py-2 whitespace-nowrap text-slate-900">
                    {slice.label}
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full ${statusBadgeClasses(
                        slice.status
                      )}`}
                    >
                      <span
                        className={`h-1.5 w-1.5 rounded-full ${statusDotClasses(
                          slice.status
                        )}`}
                      />
                      <span className="text-[11px] font-medium">
                        {friendlyStatus(slice.status)}
                      </span>
                    </span>
                    {slice.error && (
                      <div className="mt-1 text-[11px] text-rose-600">
                        {slice.error}
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-2 text-right whitespace-nowrap text-slate-900">
                    {slice.items}
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap text-slate-500">
                    {slice.lastUpdated ?? "—"}
                  </td>
                  <td className="px-4 py-2 text-right whitespace-nowrap">
                    <button
                      type="button"
                      onClick={() => handleUploadClick(slice.id)}
                      className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-[11px] font-medium bg-sky-50 text-sky-700 border border-sky-100 hover:bg-sky-100"
                      disabled={uploadingSliceId === slice.id}
                    >
                      {uploadingSliceId === slice.id ? (
                        <span>Uploading…</span>
                      ) : (
                        <>
                          <span>Upload CSV</span>
                        </>
                      )}
                    </button>
                  </td>
                </tr>
              ))}

              {!loading && (!slices || slices.length === 0) && (
                <tr>
                  <td
                    colSpan={5}
                    className="px-4 py-6 text-center text-[13px] text-slate-500"
                  >
                    No ingestion slices found for this assessment yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default RunIngestionTab;
