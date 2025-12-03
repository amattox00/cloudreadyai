import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

type RunCreateResponse = {
  id?: string;              // backend returns `id`
  name?: string;
  status?: string;
  created_at?: string;
  customer?: string | null;
  source?: string;
};

export default function DashboardPage() {
  const navigate = useNavigate();

  const [newRunBusy, setNewRunBusy] = useState(false);
  const [newRunError, setNewRunError] = useState<string | null>(null);

  const handleStartNewAssessment = async () => {
    try {
      setNewRunBusy(true);
      setNewRunError(null);

      // Create a new run via the registry API
      const res = await fetch("/v1/run_registry", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          source: "dashboard", // required by backend
          name: `Assessment ${new Date().toISOString()}`,
          description: "Created from Dashboard Start New Assessment button",
        }),
      });

      if (!res.ok) {
        throw new Error(`Failed to create run (HTTP ${res.status})`);
      }

      const data = (await res.json()) as RunCreateResponse;
      const newRunId = (data.id || "").trim(); // use `id` from backend

      if (!newRunId) {
        throw new Error("Backend did not return an id for new run");
      }

      // ✅ Go to Runs & Ingestion, passing the run id along
      navigate("/runs", {
        state: {
          newRunId,
        },
      });
    } catch (err: any) {
      setNewRunError(
        err?.message || "Failed to create run. Please try again.",
      );
    } finally {
      setNewRunBusy(false);
    }
  };

  return (
    <div className="px-8 py-8 bg-slate-50 text-slate-900 min-h-screen">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Page title */}
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">
              CloudReadyAI Dashboard
            </h1>
            <p className="mt-1 text-sm text-slate-600 max-w-2xl">
              One place to monitor ingestion, analysis, cost modeling, and overall
              assessment progress for your modernization projects.
            </p>
          </div>

          <Link
            to="/runs"
            className="inline-flex items-center rounded-full border border-sky-500 px-4 py-2 text-xs font-medium text-sky-700 bg-sky-50 hover:bg-sky-100 transition"
          >
            Open Runs workspace
            <span className="ml-1 text-[11px]">↗</span>
          </Link>
        </header>

        {/* Top row: entry actions + platform status */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          <section className="lg:col-span-3 space-y-4">
            <div className="rounded-2xl bg-white border border-slate-200 shadow-sm p-4">
              <h2 className="text-sm font-semibold text-slate-800">
                Get started
              </h2>
              <p className="mt-1 text-xs text-slate-600">
                Choose how you want to move forward with your next assessment.
              </p>

              {/* Error banner for run creation */}
              {newRunError && (
                <div className="mt-3 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-700">
                  {newRunError}
                </div>
              )}

              <div className="mt-4 grid gap-4 md:grid-cols-3">
                {/* Start new assessment */}
                <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4 flex flex-col justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-900">
                      Start New Assessment
                    </h3>
                    <p className="mt-1 text-xs text-slate-600 leading-relaxed">
                      Create a fresh assessment for a new customer. A new run
                      will be registered and you&apos;ll be taken to the Runs
                      &amp; Ingestion workspace with that run selected.
                    </p>
                  </div>
                  <div className="mt-3">
                    <button
                      type="button"
                      onClick={handleStartNewAssessment}
                      disabled={newRunBusy}
                      className="inline-flex items-center rounded-full bg-sky-600 text-white text-xs font-medium px-3 py-1.5 hover:bg-sky-700 transition disabled:opacity-60 disabled:cursor-not-allowed"
                    >
                      {newRunBusy ? "Creating..." : "Start assessment"}
                      <span className="ml-1 text-[11px]">↗</span>
                    </button>
                  </div>
                </div>

                {/* View existing runs */}
                <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4 flex flex-col justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-900">
                      View Existing Runs
                    </h3>
                    <p className="mt-1 text-xs text-slate-600 leading-relaxed">
                      Open the run registry to resume or manage an existing
                      assessment snapshot.
                    </p>
                  </div>
                  <div className="mt-3">
                    <Link
                      to="/runs"
                      className="inline-flex items-center rounded-full bg-slate-900 text-white text-xs font-medium px-3 py-1.5 hover:bg-slate-800 transition"
                    >
                      Open
                      <span className="ml-1 text-[11px]">↗</span>
                    </Link>
                  </div>
                </div>

                {/* Go to ingestion workspace */}
                <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4 flex flex-col justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-900">
                      Go to Ingestion Workspace
                    </h3>
                    <p className="mt-1 text-xs text-slate-600 leading-relaxed">
                      Upload servers, storage, network, databases, and
                      application CSVs into the active assessment run.
                    </p>
                  </div>
                  <div className="mt-3">
                    <Link
                      to="/runs"
                      className="inline-flex items-center rounded-full bg-emerald-600 text-white text-xs font-medium px-3 py-1.5 hover:bg-emerald-700 transition"
                    >
                      Open
                      <span className="ml-1 text-[11px]">↗</span>
                    </Link>
                  </div>
                </div>
              </div>
            </div>

            {/* Hero tiles row: ingestion / analysis / cost */}
            <div className="grid gap-4 md:grid-cols-3">
              {/* Ingestion coverage */}
              <div className="rounded-2xl bg-white border border-slate-200 shadow-sm p-4 flex flex-col">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-slate-800">
                    Ingestion coverage
                  </h2>
                  <span className="inline-flex items-center rounded-full border border-sky-200 bg-sky-50 px-2.5 py-0.5 text-[11px] font-medium text-sky-700">
                    Phase B / B3 / B4
                  </span>
                </div>
                <p className="mt-1 text-xs text-slate-600">
                  % of core data slices captured for this assessment.
                </p>

                <div className="mt-4 flex items-end justify-between">
                  <div>
                    <div className="text-3xl font-semibold text-slate-900">
                      0%
                    </div>
                    <p className="mt-1 text-xs text-slate-500">
                      Servers • Storage • Network • Databases • Apps
                    </p>
                  </div>
                </div>

                <p className="mt-3 text-xs text-slate-500">
                  Coverage metrics will appear here once the summary API is fully
                  wired and ingestion data is available for the active run.
                </p>

                <div className="mt-4">
                  <Link
                    to="/runs"
                    className="inline-flex items-center rounded-full border border-slate-300 bg-slate-50 text-xs font-medium text-slate-800 px-3 py-1.5 hover:bg-slate-100 transition"
                  >
                    Go to Runs &amp; ingestion
                  </Link>
                </div>
              </div>

              {/* Analysis & readiness */}
              <div className="rounded-2xl bg-white border border-slate-200 shadow-sm p-4 flex flex-col">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-slate-800">
                    Analysis &amp; readiness
                  </h2>
                  <span className="inline-flex items-center rounded-full border border-amber-200 bg-amber-50 px-2.5 py-0.5 text-[11px] font-medium text-amber-700">
                    Phase C
                  </span>
                </div>
                <p className="mt-1 text-xs text-slate-600">
                  Workload patterns, migration paths, and readiness scoring for
                  the active assessment.
                </p>

                <div className="mt-3 rounded-xl border border-dashed border-slate-200 bg-slate-50/80 p-3">
                  <p className="text-[11px] font-medium text-slate-700">
                    Coming online with Phase C APIs
                  </p>
                  <p className="mt-1 text-xs text-slate-600">
                    This card will surface readiness scores, refactor vs rehost
                    guidance, and critical risks per workload as analysis views
                    are wired.
                  </p>
                </div>

                <div className="mt-4">
                  <button
                    type="button"
                    className="inline-flex items-center rounded-full border border-slate-200 bg-slate-100 text-xs font-medium text-slate-500 px-3 py-1.5 cursor-not-allowed"
                  >
                    Open Analysis (coming soon)
                  </button>
                </div>
              </div>

              {/* Cost & TCO */}
              <div className="rounded-2xl bg-white border border-slate-200 shadow-sm p-4 flex flex-col">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-slate-800">
                    Cost &amp; TCO snapshot
                  </h2>
                  <span className="inline-flex items-center rounded-full border border-violet-200 bg-violet-50 px-2.5 py-0.5 text-[11px] font-medium text-violet-700">
                    Phase D+
                  </span>
                </div>
                <p className="mt-1 text-xs text-slate-600">
                  Compare on-prem vs cloud scenarios with provider pricing.
                </p>

                <div className="mt-3 rounded-xl border border-dashed border-slate-200 bg-slate-50/80 p-3">
                  <p className="text-[11px] font-medium text-slate-700">
                    UI planned but not fully exposed yet
                  </p>
                  <p className="mt-1 text-xs text-slate-600">
                    When enabled, this card will display cloud cost ranges by
                    provider, savings vs on-prem, and reservation strategy
                    recommendations per workload group.
                  </p>
                </div>

                <div className="mt-4">
                  <button
                    type="button"
                    className="inline-flex items-center rounded-full border border-slate-200 bg-slate-100 text-xs font-medium text-slate-500 px-3 py-1.5 cursor-not-allowed"
                  >
                    Open Cost &amp; TCO (coming soon)
                  </button>
                </div>
              </div>
            </div>
          </section>

          {/* Platform status + roadmap */}
          <aside className="space-y-4">
            <div className="rounded-2xl bg-white border border-slate-200 shadow-sm p-4">
              <h2 className="text-sm font-semibold text-slate-800">
                Platform status
              </h2>
              <p className="mt-1 text-xs text-slate-600">
                Quick view of key CloudReadyAI services.
              </p>

              <dl className="mt-3 space-y-2">
                {[
                  { label: "Backend API", status: "Healthy" },
                  { label: "PostgreSQL (devops-db)", status: "Healthy" },
                  { label: "Redis (devops-redis)", status: "Healthy" },
                ].map((item) => (
                  <div
                    key={item.label}
                    className="flex items-center justify-between"
                  >
                    <dt className="text-xs text-slate-600">{item.label}</dt>
                    <dd>
                      <span className="inline-flex items-center rounded-full bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 text-[11px] font-medium text-emerald-700">
                        ● {item.status}
                      </span>
                    </dd>
                  </div>
                ))}
              </dl>
            </div>

            <div className="rounded-2xl bg-white border border-slate-200 shadow-sm p-4">
              <h2 className="text-sm font-semibold text-slate-800">
                Roadmap preview
              </h2>
              <p className="mt-1 text-xs text-slate-600">
                Features CloudReadyAI will unlock as more phases are completed.
              </p>

              <ul className="mt-3 space-y-2 text-xs text-slate-600">
                <li className="flex items-start">
                  <span className="mt-1 mr-2 h-1.5 w-1.5 rounded-full bg-emerald-500" />
                  <span>
                    AI-generated migration playbooks per application group.
                  </span>
                </li>
                <li className="flex items-start">
                  <span className="mt-1 mr-2 h-1.5 w-1.5 rounded-full bg-emerald-500" />
                  <span>
                    Automated landing-zone diagram export for AWS, Azure, and GCP.
                  </span>
                </li>
                <li className="flex items-start">
                  <span className="mt-1 mr-2 h-1.5 w-1.5 rounded-full bg-emerald-500" />
                  <span>
                    Risk scoring and RAG (Red/Amber/Green) indicators for each
                    workload.
                  </span>
                </li>
                <li className="flex items-start">
                  <span className="mt-1 mr-2 h-1.5 w-1.5 rounded-full bg-emerald-500" />
                  <span>
                    Side-by-side comparison of multiple migration scenarios.
                  </span>
                </li>
              </ul>
            </div>
          </aside>
        </div>

        {/* Workflow row */}
        <section className="rounded-2xl bg-white border border-slate-200 shadow-sm p-4">
          <h2 className="text-sm font-semibold text-slate-800">
            End-to-end migration workflow
          </h2>
          <p className="mt-1 text-xs text-slate-600">
            This reflects the CloudReadyAI roadmap from ingestion through
            reporting and planning.
          </p>

          <div className="mt-4 grid gap-4 lg:grid-cols-5 md:grid-cols-3 sm:grid-cols-2">
            {/* Step 1 */}
            <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4 flex flex-col">
              <p className="text-[11px] font-semibold text-slate-700">Step 1</p>
              <h3 className="mt-1 text-sm font-semibold text-slate-900">
                Ingest Environment Data
              </h3>
              <p className="mt-1 text-xs text-slate-600">
                Upload CSVs or connect to collectors for servers, storage,
                network, and apps.
              </p>
              <p className="mt-3 text-[11px] text-slate-500">
                Status: Phase B engine live for CSV ingestion.
              </p>
            </div>

            {/* Step 2 */}
            <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4 flex flex-col">
              <p className="text-[11px] font-semibold text-slate-700">Step 2</p>
              <h3 className="mt-1 text-sm font-semibold text-slate-900">
                Review Assessment Summary
              </h3>
              <p className="mt-1 text-xs text-slate-600">
                Confirm that all required slices are present for a strong
                migration assessment.
              </p>
              <p className="mt-3 text-[11px] text-slate-500">
                Status: Summary API wiring in progress.
              </p>
            </div>

            {/* Step 3 */}
            <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4 flex flex-col">
              <p className="text-[11px] font-semibold text-slate-700">Step 3</p>
              <h3 className="mt-1 text-sm font-semibold text-slate-900">
                Run Analysis
              </h3>
              <p className="mt-1 text-xs text-slate-600">
                Generate migration insights, patterns, and refactor/rehost
                recommendations.
              </p>
              <p className="mt-3 text-[11px] text-slate-500">
                Status: Analysis views planned for Phase C.
              </p>
            </div>

            {/* Step 4 */}
            <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4 flex flex-col">
              <p className="text-[11px] font-semibold text-slate-700">Step 4</p>
              <h3 className="mt-1 text-sm font-semibold text-slate-900">
                Review Cost &amp; TCO
              </h3>
              <p className="mt-1 text-xs text-slate-600">
                Compare on-prem vs cloud cost scenarios using provider-native
                pricing.
              </p>
              <p className="mt-3 text-[11px] text-slate-500">
                Status: Phase D cost engine on the roadmap.
              </p>
            </div>

            {/* Step 5 */}
            <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4 flex flex-col">
              <p className="text-[11px] font-semibold text-slate-700">Step 5</p>
              <h3 className="mt-1 text-sm font-semibold text-slate-900">
                Export Reports
              </h3>
              <p className="mt-1 text-xs text-slate-600">
                Generate executive summaries, detailed workbooks, and diagram
                bundles for client delivery.
              </p>
              <p className="mt-3 text-[11px] text-slate-500">
                Status: Reporting &amp; packaging planned for later phases.
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}


