import React, { useRef, useState } from "react";

type SliceStatus = "not_started" | "partial" | "complete";

interface IngestionSlice {
  id: string;           // e.g. "servers"
  label: string;        // e.g. "Servers"
  status: SliceStatus;
  items: number;
  lastUpdated: string | null;
}

interface RunIngestionTabProps {
  runId: string;
}

/**
 * RunIngestionTab (mocked version for UI)
 *
 * For now this is a purely frontend component:
 * - No API calls
 * - Shows all 10 slices
 * - "Upload CSV" simulates a successful upload and updates the UI
 *
 * Later, we can wire this to real endpoints without changing the structure.
 */
const RunIngestionTab: React.FC<RunIngestionTabProps> = ({ runId }) => {
  const [slices, setSlices] = useState<IngestionSlice[]>([
    { id: "servers", label: "Servers", status: "complete", items: 87, lastUpdated: "5 minutes ago" },
    { id: "storage_volumes", label: "Storage volumes", status: "not_started", items: 0, lastUpdated: null },
    { id: "databases", label: "Databases", status: "not_started", items: 0, lastUpdated: null },
    { id: "applications", label: "Applications", status: "not_started", items: 0, lastUpdated: null },
    { id: "network_devices", label: "Network devices", status: "not_started", items: 0, lastUpdated: null },
    { id: "business_metadata", label: "Business metadata", status: "partial", items: 12, lastUpdated: "Yesterday" },
    { id: "dependencies", label: "Dependencies", status: "not_started", items: 0, lastUpdated: null },
    { id: "os_software", label: "OS & software", status: "not_started", items: 0, lastUpdated: null },
    { id: "utilization", label: "Utilization", status: "not_started", items: 0, lastUpdated: null },
    { id: "licensing", label: "Licensing", status: "not_started", items: 0, lastUpdated: null },
  ]);

  const [uploadingSliceId, setUploadingSliceId] = useState<string | null>(null);

  // Hidden file input
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [pendingSliceId, setPendingSliceId] = useState<string | null>(null);

  const handleUploadClick = (sliceId: string) => {
    setPendingSliceId(sliceId);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
      fileInputRef.current.click();
    }
  };

  const handleFileChange: React.ChangeEventHandler<HTMLInputElement> = async (
    event
  ) => {
    const file = event.target.files?.[0];
    if (!file || !pendingSliceId) return;

    setUploadingSliceId(pendingSliceId);

    // Simulate a short delay + success. No backend calls yet.
    setTimeout(() => {
      setSlices((prev) =>
        prev.map((s) =>
          s.id === pendingSliceId
            ? {
                ...s,
                status: "complete",
                items: s.items === 0 ? 50 : s.items, // fake count
                lastUpdated: "Just now",
              }
            : s
        )
      );
      setUploadingSliceId(null);
      setPendingSliceId(null);
    }, 600);
  };

  const friendlyStatus = (status: SliceStatus): string => {
    switch (status) {
      case "complete":
        return "Complete";
      case "partial":
        return "Partial";
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
          you ingest, the richer your insights, diagrams, and cost models will be.
          (Run ID: <span className="font-mono">{runId}</span>)
        </p>
      </div>

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
              {slices.map((slice, idx) => (
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
                      className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-[11px] font-medium bg-sky-50 text-sky-700 border border-sky-100 hover:bg-sky-100 disabled:opacity-60"
                      disabled={uploadingSliceId === slice.id}
                    >
                      {uploadingSliceId === slice.id ? "Uploading…" : "Upload CSV"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default RunIngestionTab;
