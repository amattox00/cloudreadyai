import React, { ChangeEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

type TabId = "overview" | "ingestion" | "insights" | "diagrams" | "cost" | "reports";

type AssessmentStatus = "Not Started" | "In Progress" | "Completed" | "Error";

interface RunRecord {
  id: string;
  name: string;
  source: string;
  state: AssessmentStatus | string;
  created_at: string;

  // Counters from run registry
  servers_ingested?: number;
  storage_ingested?: number;
  network_ingested?: number;
  databases_ingested?: number;
  applications_ingested?: number;
  dependencies_ingested?: number;
}

type SliceKey = "servers" | "storage" | "databases" | "applications" | "dependencies";

interface UploadState {
  file?: File;
  uploading: boolean;
  error?: string | null;
  okMessage?: string | null;

  // last ingestion response payload (per slice)
  result?: any;
}

const initialUploadState: UploadState = {
  file: undefined,
  uploading: false,
  error: null,
  okMessage: null,
  result: null,
};

export default function RunDetailPage() {
  const navigate = useNavigate();
  const { runId } = useParams<{ runId: string }>();

  const [activeTab, setActiveTab] = useState<TabId>("ingestion");
  const [run, setRun] = useState<RunRecord | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [uploads, setUploads] = useState<Record<SliceKey, UploadState>>({
    servers: { ...initialUploadState },
    storage: { ...initialUploadState },
    databases: { ...initialUploadState },
    applications: { ...initialUploadState },
    dependencies: { ...initialUploadState },
  });

  const tabs: { id: TabId; label: string }[] = [
    { id: "overview", label: "Overview" },
    { id: "ingestion", label: "Ingestion" },
    { id: "insights", label: "Insights" },
    { id: "diagrams", label: "Diagrams" },
    { id: "cost", label: "Cost Modeling" },
    { id: "reports", label: "Reports" },
  ];

  const goBack = () => navigate("/runs");

  const fetchRun = async () => {
    if (!runId) {
      setError("Missing runId in route.");
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const res = await fetch(`/v1/run_registry/${encodeURIComponent(runId)}`);
      if (!res.ok) throw new Error(`Failed to load assessment (${res.status})`);
      const data: RunRecord = await res.json();
      setRun(data);
    } catch (err: any) {
      setError(err?.message || "Failed to load assessment details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchRun();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [runId]);

  const handleFileChange =
    (slice: SliceKey) =>
    (event: ChangeEvent<HTMLInputElement>) => {
      const file =
        event.target.files && event.target.files[0] ? event.target.files[0] : undefined;

      setUploads((prev) => ({
        ...prev,
        [slice]: {
          ...prev[slice],
          file,
          error: null,
          okMessage: null,
          // keep prior result until next upload
        },
      }));
    };

  const downloadTemplate = async (slice: SliceKey) => {
    try {
      const res = await fetch(`/v1/ingest/templates/${slice}/csv`);
      if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(`Template download failed (${res.status}): ${text}`);
      }

      const blob = await res.blob();

      let filename = `${slice}.template.csv`;
      const cd = res.headers.get("content-disposition") || "";
      const match = cd.match(/filename="?([^"]+)"?/i);
      if (match?.[1]) filename = match[1];

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      setUploads((prev) => ({
        ...prev,
        [slice]: {
          ...prev[slice],
          error: null,
        },
      }));
    } catch (err: any) {
      setUploads((prev) => ({
        ...prev,
        [slice]: {
          ...prev[slice],
          error: err?.message || "Failed to download template.",
        },
      }));
    }
  };

  const handleUpload = (slice: SliceKey) => async () => {
    if (!runId || !run) return;

    const current = uploads[slice];
    if (!current.file) {
      setUploads((prev) => ({
        ...prev,
        [slice]: { ...prev[slice], error: "Please choose a CSV file first." },
      }));
      return;
    }

    try {
      setUploads((prev) => ({
        ...prev,
        [slice]: {
          ...prev[slice],
          uploading: true,
          error: null,
          okMessage: null,
        },
      }));

      const formData = new FormData();
      formData.append("file", current.file);

      const res = await fetch(`/v1/ingest/${slice}?run_id=${encodeURIComponent(run.id)}`, {
        method: "POST",
        body: formData,
      });

      // Capture response body safely (text first, then JSON)
      const rawText = await res.text();
      let payload: any = {};
      try {
        payload = rawText ? JSON.parse(rawText) : {};
      } catch {
        payload = { raw: rawText };
      }

      if (!res.ok) {
        const msg = payload?.detail || payload?.message || rawText || `HTTP ${res.status}`;
        throw new Error(`Upload failed (${res.status}): ${msg}`);
      }

      // Many endpoints return { details: {...} } — prefer details but keep entire payload
      const details = payload?.details ?? payload;

      setUploads((prev) => ({
        ...prev,
        [slice]: {
          ...prev[slice],
          uploading: false,
          file: undefined,
          okMessage: details?.message || "Upload completed successfully.",
          result: details,
        },
      }));

      void fetchRun();
    } catch (err: any) {
      setUploads((prev) => ({
        ...prev,
        [slice]: {
          ...prev[slice],
          uploading: false,
          error: err?.message || "Failed to upload CSV for this slice.",
        },
      }));
    }
  };

  const formatDate = (value?: string) => {
    if (!value) return "—";
    try {
      return new Date(value).toLocaleString();
    } catch {
      return value;
    }
  };

  const statusBadgeClass = (() => {
    const status = (run?.state || "Not Started") as AssessmentStatus | string;
    switch (status) {
      case "In Progress":
        return "bg-blue-100 text-blue-800";
      case "Completed":
        return "bg-green-100 text-green-800";
      case "Error":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-700";
    }
  })();

  const serversIngested = run?.servers_ingested ?? 0;
  const storageIngested = run?.storage_ingested ?? 0;
  const databasesIngested = run?.databases_ingested ?? 0;
  const applicationsIngested = run?.applications_ingested ?? 0;
  const dependenciesIngested = run?.dependencies_ingested ?? 0;

  return (
    <div className="px-6 py-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <button onClick={goBack} className="text-xs text-blue-600 hover:underline mb-1">
            ← Back to Assessments
          </button>
          <h1 className="text-xl font-semibold text-gray-900">{run?.name || "New assessment"}</h1>
          <p className="text-sm text-gray-600">
            Assessment ID: <span className="font-mono">{run?.id || runId || "—"}</span>
          </p>
        </div>

        <div className="text-right space-y-1">
          <div>
            <span
              className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${statusBadgeClass}`}
            >
              {run?.state || "Not Started"}
            </span>
          </div>
          <p className="text-xs text-gray-500">Created {formatDate(run?.created_at)}</p>
        </div>
      </div>

      {/* Loading / error */}
      {loading && <div className="text-sm text-gray-500">Loading assessment...</div>}
      {!loading && error && (
        <div className="border border-red-200 bg-red-50 text-red-700 text-sm px-3 py-2 rounded">
          {error}
        </div>
      )}

      {/* Top summary cards */}
      {!loading && !error && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <SummaryCard title="Client / Source" value={run?.source || "Dashboard"} />
          <SummaryCard title="Environment" value="—" />
          <SummaryCard title="Status" value={run?.state || "Not Started"} />
          <SummaryCard title="Assessment activity" value={`Created ${formatDate(run?.created_at)}`} />
        </div>
      )}

      {/* Tabs */}
      {!loading && !error && (
        <>
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

          {activeTab === "overview" && <OverviewTab run={run} />}

          {activeTab === "ingestion" && (
            <IngestionTab
              serversIngested={serversIngested}
              storageIngested={storageIngested}
              databasesIngested={databasesIngested}
              applicationsIngested={applicationsIngested}
              dependenciesIngested={dependenciesIngested}
              uploads={uploads}
              onFileChange={handleFileChange}
              onUpload={handleUpload}
              onDownloadTemplate={(slice) => void downloadTemplate(slice)}
            />
          )}

          {activeTab !== "overview" && activeTab !== "ingestion" && (
            <PlaceholderTab
              title={(() => {
                switch (activeTab) {
                  case "insights":
                    return "Insights";
                  case "diagrams":
                    return "Diagrams";
                  case "cost":
                    return "Cost Modeling";
                  case "reports":
                    return "Reports";
                  default:
                    return "Section";
                }
              })()}
            />
          )}
        </>
      )}
    </div>
  );
}

/* ------------------------------
   Overview Tab
------------------------------ */

function OverviewTab({ run }: { run: RunRecord | null }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4 space-y-3">
        <h2 className="text-sm font-medium text-gray-900">Assessment summary</h2>
        <p className="text-xs text-gray-600">High-level details including source, status, and creation time.</p>

        <dl className="mt-2 grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-sm">
          <div>
            <dt className="text-xs text-gray-500">Client / Source</dt>
            <dd className="text-gray-900">{run?.source || "Dashboard"}</dd>
          </div>

          <div>
            <dt className="text-xs text-gray-500">Environment</dt>
            <dd className="text-gray-900">—</dd>
          </div>

          <div>
            <dt className="text-xs text-gray-500">Status</dt>
            <dd className="text-gray-900">{run?.state || "Not Started"}</dd>
          </div>

          <div>
            <dt className="text-xs text-gray-500">Created</dt>
            <dd className="text-gray-900">{run ? new Date(run.created_at).toLocaleString() : "—"}</dd>
          </div>
        </dl>
      </div>

      <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4 space-y-3">
        <h2 className="text-sm font-medium text-gray-900">Portfolio context</h2>
        <p className="text-xs text-gray-600">
          This section will eventually show how this assessment maps into your broader client portfolio, workloads,
          and migration plans.
        </p>
        <div className="border border-dashed border-gray-300 rounded-md h-32 flex items-center justify-center text-xs text-gray-400">
          Coming soon
        </div>
      </div>
    </div>
  );
}

/* ------------------------------
   Ingestion Tab
------------------------------ */

function IngestionTab({
  serversIngested,
  storageIngested,
  databasesIngested,
  applicationsIngested,
  dependenciesIngested,
  uploads,
  onFileChange,
  onUpload,
  onDownloadTemplate,
}: {
  serversIngested: number;
  storageIngested: number;
  databasesIngested: number;
  applicationsIngested: number;
  dependenciesIngested: number;
  uploads: Record<SliceKey, UploadState>;
  onFileChange: (slice: SliceKey) => (event: ChangeEvent<HTMLInputElement>) => void;
  onUpload: (slice: SliceKey) => () => void;
  onDownloadTemplate: (slice: SliceKey) => void;
}) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-5 gap-4">
        <SummaryCard title="Servers ingested" value={serversIngested.toString()} />
        <SummaryCard title="Storage volumes" value={storageIngested.toString()} />
        <SummaryCard title="Databases" value={databasesIngested.toString()} />
        <SummaryCard title="Applications" value={applicationsIngested.toString()} />
        <SummaryCard title="Dependencies" value={dependenciesIngested.toString()} />
      </div>

      <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4 space-y-4">
        <h3 className="text-sm font-medium text-gray-900">Ingestion overview</h3>
        <p className="text-xs text-gray-600">
          Upload CSV data for each slice in this assessment. Use Download template to ensure headers match guardrails.
        </p>

        <div className="space-y-3">
          <SliceUploadRow
            label="Servers CSV"
            description="Core compute inventory. Each row represents a server or VM."
            slice="servers"
            state={uploads.servers}
            onFileChange={onFileChange("servers")}
            onUpload={onUpload("servers")}
            onDownloadTemplate={() => onDownloadTemplate("servers")}
          />
          <SliceUploadRow
            label="Storage volumes CSV"
            description="Block / file storage objects, LUNs, and volumes."
            slice="storage"
            state={uploads.storage}
            onFileChange={onFileChange("storage")}
            onUpload={onUpload("storage")}
            onDownloadTemplate={() => onDownloadTemplate("storage")}
          />
          <SliceUploadRow
            label="Databases CSV"
            description="Database servers and logical databases / schemas."
            slice="databases"
            state={uploads.databases}
            onFileChange={onFileChange("databases")}
            onUpload={onUpload("databases")}
            onDownloadTemplate={() => onDownloadTemplate("databases")}
          />
          <SliceUploadRow
            label="Applications CSV"
            description="Logical application inventory, ownership, and dependency context."
            slice="applications"
            state={uploads.applications}
            onFileChange={onFileChange("applications")}
            onUpload={onUpload("applications")}
            onDownloadTemplate={() => onDownloadTemplate("applications")}
          />
          <SliceUploadRow
            label="Dependencies CSV"
            description="Application-to-application dependency edges (app_id → depends_on_app_id)."
            slice="dependencies"
            state={uploads.dependencies}
            onFileChange={onFileChange("dependencies")}
            onUpload={onUpload("dependencies")}
            onDownloadTemplate={() => onDownloadTemplate("dependencies")}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard
          title="Ingestion status by resource type"
          description="As more slices are ingested, this chart will show coverage across servers, storage, databases, applications, and dependencies."
        />
        <ChartCard title="Utilization and trends" description="Future view for CPU, memory, and storage utilization over time." />
      </div>
    </div>
  );
}

/* ------------------------------
   Shared small components
------------------------------ */

function SummaryCard({ title, value }: { title: string; value: string }) {
  return (
    <div className="border border-gray-200 bg-white rounded-md px-4 py-4 shadow-sm">
      <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">{title}</p>
      <p className="text-lg font-semibold text-gray-900 mt-1">{value}</p>
    </div>
  );
}

function extractList(val: any): string[] {
  if (!val) return [];
  if (Array.isArray(val)) return val.map((x) => String(x));
  return [String(val)];
}

function computeSliceStatus(result: any): {
  level: "blocked" | "warn" | "ok";
  label: string;
  summary?: string;
} {
  if (!result) return { level: "ok", label: "", summary: undefined };

  const blockers = extractList(result?.blockers);

  const guardrails = result?.guardrails;

  const missingRequired =
    extractList(guardrails?.missing_required).length > 0
      ? extractList(guardrails?.missing_required)
      : extractList(result?.missing_required_headers)
          .concat(extractList(result?.missing_required))
          .concat(extractList(result?.missing_required_fields));

  const warnings =
    extractList(guardrails?.warnings).length > 0
      ? extractList(guardrails?.warnings)
      : extractList(result?.warnings)
          .concat(extractList(result?.linkage_warnings))
          .concat(extractList(result?.warning_messages));

  const processed =
    typeof result?.rows_processed === "number"
      ? result.rows_processed
      : typeof result?.counts?.rows_processed === "number"
        ? result.counts.rows_processed
        : undefined;

  const ok =
    typeof result?.rows_successful === "number"
      ? result.rows_successful
      : typeof result?.counts?.rows_successful === "number"
        ? result.counts.rows_successful
        : undefined;

  const failed =
    typeof result?.rows_failed === "number"
      ? result.rows_failed
      : typeof result?.counts?.rows_failed === "number"
        ? result.counts.rows_failed
        : undefined;

  // Determine blocked
  const isBlocked =
    blockers.length > 0 ||
    (missingRequired.length > 0 && guardrails?.valid === false) ||
    String(result?.status || "").toLowerCase() === "blocked";

  if (isBlocked) {
    const missingSummary =
      missingRequired.length > 0 ? `Missing required: ${missingRequired.join(", ")}` : undefined;
    return { level: "blocked", label: "Blocked", summary: missingSummary };
  }

  // Accepted with warnings
  if (warnings.length > 0) {
    const base =
      processed !== undefined || ok !== undefined || failed !== undefined
        ? `Processed ${processed ?? "—"} • OK ${ok ?? "—"} • Failed ${failed ?? "—"}`
        : undefined;

    const summary = base ? `${base} • Warnings ${warnings.length}` : `Warnings ${warnings.length}`;
    return { level: "warn", label: "Accepted w/ warnings", summary };
  }

  // Accepted
  const okSummary =
    processed !== undefined || ok !== undefined || failed !== undefined
      ? `Processed ${processed ?? "—"} • OK ${ok ?? "—"} • Failed ${failed ?? "—"}`
      : undefined;

  return { level: "ok", label: "Accepted", summary: okSummary };
}

function StatusPill({ level, text }: { level: "blocked" | "warn" | "ok"; text: string }) {
  const cls =
    level === "blocked"
      ? "bg-red-50 text-red-700 border border-red-100"
      : level === "warn"
        ? "bg-amber-50 text-amber-800 border border-amber-100"
        : "bg-emerald-50 text-emerald-700 border border-emerald-100";

  const dot =
    level === "blocked" ? "bg-red-500" : level === "warn" ? "bg-amber-500" : "bg-emerald-500";

  return (
    <span className={`inline-flex items-center gap-2 px-2 py-0.5 rounded-full text-[11px] font-medium ${cls}`}>
      <span className={`h-2 w-2 rounded-full ${dot}`} />
      {text}
    </span>
  );
}

function SliceUploadRow({
  label,
  description,
  slice,
  state,
  onFileChange,
  onUpload,
  onDownloadTemplate,
}: {
  label: string;
  description: string;
  slice: SliceKey;
  state: UploadState;
  onFileChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onUpload: () => void;
  onDownloadTemplate: () => void;
}) {
  const s = computeSliceStatus(state.result);

  return (
    <div className="border border-gray-100 rounded-md px-3 py-3">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <p className="text-sm font-medium text-gray-900">{label}</p>
            {s.label ? <StatusPill level={s.level} text={s.label} /> : null}
          </div>

          <p className="text-xs text-gray-600">{description}</p>

          {s.summary ? <p className="text-xs text-gray-700">{s.summary}</p> : null}
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center gap-2">
          <input type="file" accept=".csv" onChange={onFileChange} className="block text-xs text-gray-700" />
          <button
            type="button"
            onClick={onDownloadTemplate}
            className="inline-flex justify-center items-center px-3 py-1.5 rounded-md text-xs font-medium text-gray-700 bg-white border border-gray-200 hover:bg-gray-50"
          >
            Download template
          </button>
          <button
            type="button"
            onClick={onUpload}
            disabled={state.uploading}
            className="inline-flex justify-center items-center px-3 py-1.5 rounded-md text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-60"
          >
            {state.uploading ? "Uploading..." : `Upload ${slice} CSV`}
          </button>
        </div>
      </div>

      {state.error && <p className="mt-1 text-xs text-red-600">{state.error}</p>}
      {state.okMessage && <p className="mt-1 text-xs text-green-600">{state.okMessage}</p>}

      {/* Ingestion Result Visibility */}
      {state.result && <IngestionResultPanel result={state.result} />}
    </div>
  );
}

function IngestionResultPanel({ result }: { result: any }) {
  // Extract common fields if present (defensive; never breaks if shape changes)
  const rowsProcessed = result?.rows_processed ?? result?.counts?.rows_processed;
  const rowsSuccessful = result?.rows_successful ?? result?.counts?.rows_successful;
  const rowsFailed = result?.rows_failed ?? result?.counts?.rows_failed;

  const guardrails = result?.guardrails;

  const missingRequired =
    extractList(guardrails?.missing_required).length > 0
      ? extractList(guardrails?.missing_required)
      : extractList(result?.missing_required_headers)
          .concat(extractList(result?.missing_required))
          .concat(extractList(result?.missing_required_fields));

  const unknownColumns =
    extractList(guardrails?.unknown_columns).length > 0
      ? extractList(guardrails?.unknown_columns)
      : extractList(result?.unknown_columns).concat(extractList(result?.unknown_headers));

  const aliasMappings =
    guardrails?.used_aliases && Object.keys(guardrails.used_aliases).length > 0
      ? guardrails.used_aliases
      : result?.alias_mappings ?? result?.aliases_used ?? result?.header_aliases_used;

  const warnings =
    extractList(guardrails?.warnings).length > 0
      ? extractList(guardrails?.warnings)
      : extractList(result?.warnings)
          .concat(extractList(result?.linkage_warnings))
          .concat(extractList(result?.warning_messages));

  const hasAnySummary =
    rowsProcessed !== undefined ||
    rowsSuccessful !== undefined ||
    rowsFailed !== undefined ||
    missingRequired.length > 0 ||
    unknownColumns.length > 0 ||
    aliasMappings ||
    warnings.length > 0;

  const json = (() => {
    try {
      return JSON.stringify(result, null, 2);
    } catch {
      return String(result);
    }
  })();

  return (
    <div className="mt-3 border border-gray-200 bg-gray-50 rounded-md p-3 space-y-2">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium text-gray-800">Ingestion details</p>
        <span className="text-[11px] text-gray-600">
          {rowsProcessed !== undefined ? `Processed ${rowsProcessed}` : "Details captured"}
          {rowsSuccessful !== undefined ? ` • OK ${rowsSuccessful}` : ""}
          {rowsFailed !== undefined ? ` • Failed ${rowsFailed}` : ""}
        </span>
      </div>

      {hasAnySummary && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-gray-700">
          {missingRequired.length > 0 && (
            <div>
              <p className="font-medium text-gray-800">Missing required</p>
              <ul className="list-disc ml-4">
                {missingRequired.slice(0, 20).map((x: any, i: number) => (
                  <li key={i}>{String(x)}</li>
                ))}
              </ul>
            </div>
          )}

          {unknownColumns.length > 0 && (
            <div>
              <p className="font-medium text-gray-800">Unknown columns</p>
              <ul className="list-disc ml-4">
                {unknownColumns.slice(0, 20).map((x: any, i: number) => (
                  <li key={i}>{String(x)}</li>
                ))}
              </ul>
            </div>
          )}

          {aliasMappings && (
            <div className="md:col-span-2">
              <p className="font-medium text-gray-800">Alias mappings used</p>
              <pre className="text-[11px] bg-white border border-gray-200 rounded p-2 overflow-auto max-h-40">
                {(() => {
                  try {
                    return JSON.stringify(aliasMappings, null, 2);
                  } catch {
                    return String(aliasMappings);
                  }
                })()}
              </pre>
            </div>
          )}

          {warnings.length > 0 && (
            <div className="md:col-span-2">
              <p className="font-medium text-gray-800">Warnings</p>
              <ul className="list-disc ml-4">
                {warnings.slice(0, 25).map((x: any, i: number) => (
                  <li key={i}>{String(x)}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <details className="mt-1">
        <summary className="cursor-pointer text-xs text-blue-700 hover:underline">Show raw JSON</summary>
        <pre className="text-[11px] bg-white border border-gray-200 rounded p-2 overflow-auto max-h-72 mt-2">
          {json}
        </pre>
      </details>
    </div>
  );
}

function ChartCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4">
      <h3 className="text-sm font-medium text-gray-900 mb-2">{title}</h3>
      <p className="text-xs text-gray-600 mb-4">{description}</p>
      <div className="h-48 border border-dashed border-gray-300 rounded flex items-center justify-center text-xs text-gray-400">
        Chart placeholder
      </div>
    </div>
  );
}

function PlaceholderTab({ title }: { title: string }) {
  return (
    <div className="border border-gray-200 bg-white rounded-md shadow-sm p-6 text-sm text-gray-600">
      {title} workspace wiring is planned for the MVP. The ingestion and run registry flows you just validated will feed
      this section.
    </div>
  );
}
