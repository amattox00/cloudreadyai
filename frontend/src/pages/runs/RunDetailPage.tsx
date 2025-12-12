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
  databases_ingested?: number; // Databases slice wiring
  applications_ingested?: number; // Applications slice wiring
  dependencies_ingested?: number; // ✅ Dependencies slice wiring
}

type SliceKey = "servers" | "storage" | "databases" | "applications" | "dependencies";

interface UploadState {
  file?: File;
  uploading: boolean;
  error?: string | null;
  okMessage?: string | null;
}

const initialUploadState: UploadState = {
  file: undefined,
  uploading: false,
  error: null,
  okMessage: null,
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
      if (!res.ok) {
        throw new Error(`Failed to load assessment (${res.status})`);
      }
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
        event.target.files && event.target.files[0]
          ? event.target.files[0]
          : undefined;

      setUploads((prev) => ({
        ...prev,
        [slice]: {
          ...prev[slice],
          file,
          error: null,
          okMessage: null,
        },
      }));
    };

  const handleUpload = (slice: SliceKey) => async () => {
    if (!runId || !run) return;

    const current = uploads[slice];
    if (!current.file) {
      setUploads((prev) => ({
        ...prev,
        [slice]: {
          ...prev[slice],
          error: "Please choose a CSV file first.",
        },
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

      const res = await fetch(
        `/v1/ingest/${slice}?run_id=${encodeURIComponent(run.id)}`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Upload failed (${res.status}): ${text}`);
      }

      const payload = await res.json().catch(() => ({}));

      setUploads((prev) => ({
        ...prev,
        [slice]: {
          ...prev[slice],
          uploading: false,
          file: undefined,
          okMessage: payload?.details?.message || "Upload completed successfully.",
        },
      }));

      // Refresh run so counters & tiles update for these slices
      if (
        slice === "servers" ||
        slice === "storage" ||
        slice === "databases" ||
        slice === "applications" ||
        slice === "dependencies"
      ) {
        void fetchRun();
      }
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
          <button
            onClick={goBack}
            className="text-xs text-blue-600 hover:underline mb-1"
          >
            ← Back to Assessments
          </button>
          <h1 className="text-xl font-semibold text-gray-900">
            {run?.name || "New assessment"}
          </h1>
          <p className="text-sm text-gray-600">
            Assessment ID:{" "}
            <span className="font-mono">{run?.id || runId || "—"}</span>
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
          <p className="text-xs text-gray-500">
            Created {formatDate(run?.created_at)}
          </p>
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
          <SummaryCard
            title="Assessment activity"
            value={`Created ${formatDate(run?.created_at)}`}
          />
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

          {/* Tab content */}
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
      {/* Left: Summary */}
      <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4 space-y-3">
        <h2 className="text-sm font-medium text-gray-900">Assessment summary</h2>
        <p className="text-xs text-gray-600">
          High-level details including source, status, and creation time.
        </p>

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
            <dd className="text-gray-900">
              {run ? new Date(run.created_at).toLocaleString() : "—"}
            </dd>
          </div>
        </dl>
      </div>

      {/* Right: Placeholder for future portfolio / client info */}
      <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4 space-y-3">
        <h2 className="text-sm font-medium text-gray-900">Portfolio context</h2>
        <p className="text-xs text-gray-600">
          This section will eventually show how this assessment maps into your broader
          client portfolio, workloads, and migration plans.
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
}: {
  serversIngested: number;
  storageIngested: number;
  databasesIngested: number;
  applicationsIngested: number;
  dependenciesIngested: number;
  uploads: Record<SliceKey, UploadState>;
  onFileChange: (slice: SliceKey) => (event: ChangeEvent<HTMLInputElement>) => void;
  onUpload: (slice: SliceKey) => () => void;
}) {
  return (
    <div className="space-y-6">
      {/* Top summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-5 gap-4">
        <SummaryCard title="Servers ingested" value={serversIngested.toString()} />
        <SummaryCard title="Storage volumes" value={storageIngested.toString()} />
        <SummaryCard title="Databases" value={databasesIngested.toString()} />
        <SummaryCard title="Applications" value={applicationsIngested.toString()} />
        <SummaryCard title="Dependencies" value={dependenciesIngested.toString()} />
      </div>

      {/* Ingestion overview & upload controls */}
      <div className="border border-gray-200 bg-white rounded-md shadow-sm p-4 space-y-4">
        <h3 className="text-sm font-medium text-gray-900">Ingestion overview</h3>
        <p className="text-xs text-gray-600">
          Upload CSV data for each slice in this assessment. Servers are wired end-to-end today.
          Storage volumes, databases, applications, and dependencies use the same ingestion pattern
          and can be enhanced further as their v2 engines come online.
        </p>

        <div className="space-y-3">
          <SliceUploadRow
            label="Servers CSV"
            description="Core compute inventory. Each row represents a server or VM."
            slice="servers"
            state={uploads.servers}
            onFileChange={onFileChange("servers")}
            onUpload={onUpload("servers")}
          />
          <SliceUploadRow
            label="Storage volumes CSV"
            description="Block / file storage objects, LUNs, and volumes."
            slice="storage"
            state={uploads.storage}
            onFileChange={onFileChange("storage")}
            onUpload={onUpload("storage")}
          />
          <SliceUploadRow
            label="Databases CSV"
            description="Database servers and logical databases / schemas."
            slice="databases"
            state={uploads.databases}
            onFileChange={onFileChange("databases")}
            onUpload={onUpload("databases")}
          />
          <SliceUploadRow
            label="Applications CSV"
            description="Logical application inventory, ownership, and dependency context."
            slice="applications"
            state={uploads.applications}
            onFileChange={onFileChange("applications")}
            onUpload={onUpload("applications")}
          />
          <SliceUploadRow
            label="Dependencies CSV"
            description="Application-to-application dependency edges (app_id → depends_on_app_id)."
            slice="dependencies"
            state={uploads.dependencies}
            onFileChange={onFileChange("dependencies")}
            onUpload={onUpload("dependencies")}
          />
        </div>
      </div>

      {/* Charts placeholders (still mock / future wiring) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard
          title="Ingestion status by resource type"
          description="As more slices are ingested, this chart will show coverage across servers, storage, databases, applications, and dependencies."
        />
        <ChartCard
          title="Utilization and trends"
          description="Future view for CPU, memory, and storage utilization over time."
        />
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

function SliceUploadRow({
  label,
  description,
  slice,
  state,
  onFileChange,
  onUpload,
}: {
  label: string;
  description: string;
  slice: SliceKey;
  state: UploadState;
  onFileChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onUpload: () => void;
}) {
  return (
    <div className="border border-gray-100 rounded-md px-3 py-3">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-gray-900">{label}</p>
          <p className="text-xs text-gray-600">{description}</p>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center gap-2">
          <input
            type="file"
            accept=".csv"
            onChange={onFileChange}
            className="block text-xs text-gray-700"
          />
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
      {title} workspace wiring is planned for the MVP. The ingestion and run registry flows you just
      validated will feed this section.
    </div>
  );
}
