import React, { FormEvent, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

/**
 * Phase C1 Analysis prototype
 *
 * - Lets the user enter a Run ID manually (no backend dependency yet)
 * - Persists the selected runId in the URL as ?runId=...
 * - Renders sample / placeholder analysis content for the active run
 * - Safe: does not call /v1/run_registry or /v1/runs/{id}/summary yet
 */

const AnalysisPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialRunId = (searchParams.get("runId") || "").trim();

  const [runIdInput, setRunIdInput] = useState<string>(initialRunId);
  const [activeRunId, setActiveRunId] = useState<string>(initialRunId);
  const [hasSubmitted, setHasSubmitted] = useState<boolean>(
    initialRunId.length > 0,
  );

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = runIdInput.trim();

    setHasSubmitted(true);
    setActiveRunId(trimmed);

    if (trimmed) {
      setSearchParams({ runId: trimmed });
    } else {
      setSearchParams({});
    }
  };

  const noRunSelected = !activeRunId;

  return (
    <div className="px-8 py-8 min-h-screen bg-slate-50 text-slate-900">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <header className="flex items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">
              Analysis
            </h1>
            <p className="mt-1 text-sm text-slate-600 max-w-2xl">
              Phase C analysis prototype. Select a CloudReadyAI assessment
              run and review readiness, landing patterns, and risk signals.
              This view is currently backed by representative sample data.
            </p>
          </div>

          <Link
            to="/runs"
            className="inline-flex items-center rounded-full border border-slate-300 bg-white px-4 py-2 text-xs font-medium text-slate-800 shadow-sm hover:bg-slate-100 transition"
          >
            Open Runs &amp; Ingestion
            <span className="ml-1 text-[11px]">↗</span>
          </Link>
        </header>

        {/* Run selection bar */}
        <section className="rounded-2xl bg-white border border-slate-200 shadow-sm p-4 flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div className="flex-1 space-y-2">
            <p className="text-xs font-semibold text-slate-800 uppercase tracking-wide">
              Select assessment run
            </p>
            <p className="text-xs text-slate-600">
              Paste any valid CloudReadyAI <span className="font-mono">run_id</span>{" "}
              from the Runs &amp; Ingestion workspace. In a future Phase C
              drop, this will be wired directly to the run registry and
              summary APIs.
            </p>

            <form
              onSubmit={handleSubmit}
              className="mt-2 flex flex-col sm:flex-row sm:items-center gap-2"
            >
              <div className="flex-1">
                <input
                  type="text"
                  value={runIdInput}
                  onChange={(e) => setRunIdInput(e.target.value)}
                  placeholder="e.g. RUN-20251128-020746-ea4f3ceb"
                  className="block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-orange-500 focus:ring-orange-500 font-mono"
                />
                <p className="mt-1 text-[0.7rem] text-slate-500">
                  Current URL parameter:{" "}
                  <code className="font-mono">
                    {searchParams.get("runId") || "none"}
                  </code>
                </p>
              </div>

              <button
                type="submit"
                className="inline-flex items-center justify-center rounded-md bg-emerald-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-emerald-700"
              >
                Analyze run
              </button>
            </form>
          </div>

          <div className="min-w-[220px] rounded-xl border border-dashed border-slate-200 bg-slate-50 px-3 py-3 text-xs">
            <p className="text-[11px] font-semibold text-slate-700">
              Phase C1 status
            </p>
            <p className="mt-1 text-[0.7rem] text-slate-600">
              • UI and UX shell in place{" "}
              <span className="text-emerald-600 font-semibold">✔</span>
            </p>
            <p className="mt-0.5 text-[0.7rem] text-slate-600">
              • Using sample analysis data for now{" "}
              <span className="text-amber-600 font-semibold">●</span>
            </p>
            <p className="mt-0.5 text-[0.7rem] text-slate-600">
              • Next: wire to{" "}
              <code className="font-mono text-[0.65rem]">
                /v1/runs/&lt;run_id&gt;/summary
              </code>{" "}
              once backend analysis model is ready.
            </p>
          </div>
        </section>

        {/* If no run has been selected yet */}
        {noRunSelected && (
          <section className="rounded-2xl bg-white border border-slate-200 shadow-sm p-6">
            <p className="text-sm text-slate-700">
              No <code className="font-mono text-[0.75rem]">runId</code> is
              currently active.
            </p>
            <p className="mt-2 text-sm text-slate-600">
              Enter a Run ID above, or open the{" "}
              <Link
                to="/runs"
                className="text-orange-600 hover:text-orange-700 underline underline-offset-2"
              >
                Runs &amp; Ingestion
              </Link>{" "}
              workspace to create or select an assessment. Once a Run ID is
              selected, this page will render a representative analysis
              view for Phase C.
            </p>
          </section>
        )}

        {/* When a run is selected, show the sample analysis layout */}
        {!noRunSelected && (
          <section className="space-y-5">
            {/* Overview stripe */}
            <div className="rounded-2xl bg-white border border-slate-200 shadow-sm p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <p className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
                  Active assessment
                </p>
                <p className="mt-1 text-sm text-slate-900">
                  Run ID:{" "}
                  <span className="font-mono text-[0.8rem] bg-slate-100 px-1.5 py-0.5 rounded">
                    {activeRunId}
                  </span>
                </p>
                <p className="mt-1 text-xs text-slate-600 max-w-xl">
                  This analysis is rendered using curated sample data that
                  mirrors a typical medium-size enterprise migration
                  portfolio (Phase C1). Wiring to live summaries will be a
                  Phase C2 task.
                </p>
              </div>
              <div className="text-right space-y-1">
                <p className="text-[0.7rem] uppercase tracking-wide text-slate-500">
                  Analysis grade (sample)
                </p>
                <p className="text-xl font-semibold text-emerald-700">
                  B+ • Migration ready
                </p>
                <p className="text-[0.7rem] text-slate-500">
                  Majority of workloads can move in 3–4 structured waves.
                </p>
              </div>
            </div>

            {/* Main three-column layout */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
              {/* Column 1: Portfolio & patterns */}
              <div className="space-y-4">
                <div className="rounded-2xl bg-white border border-slate-200 shadow-sm p-4">
                  <h2 className="text-sm font-semibold text-slate-800">
                    Workload portfolio snapshot (sample)
                  </h2>
                  <p className="mt-1 text-xs text-slate-600">
                    Representative mix of server, database, and application
                    tiers for this assessment.
                  </p>

                  <dl className="mt-3 space-y-2 text-xs text-slate-700">
                    <div className="flex items-center justify-between">
                      <dt>Discovered workloads</dt>
                      <dd className="font-semibold">124</dd>
                    </div>
                    <div className="flex items-center justify-between">
                      <dt>Business-critical applications</dt>
                      <dd className="font-semibold">18</dd>
                    </div>
                    <div className="flex items-center justify-between">
                      <dt>Databases in scope</dt>
                      <dd className="font-semibold">32</dd>
                    </div>
                    <div className="flex items-center justify-between">
                      <dt>Legacy / end-of-support OS</dt>
                      <dd className="font-semibold text-amber-700">14</dd>
                    </div>
                    <div className="flex items-center justify-between">
                      <dt>Heavily coupled systems</dt>
                      <dd className="font-semibold text-rose-700">7</dd>
                    </div>
                  </dl>
                </div>

                <div className="rounded-2xl bg-white border border-slate-200 shadow-sm p-4">
                  <h2 className="text-sm font-semibold text-slate-800">
                    Pattern recommendations (sample)
                  </h2>
                  <p className="mt-1 text-xs text-slate-600">
                    Rough distribution of recommended landing patterns for
                    this run&apos;s portfolio.
                  </p>

                  <ul className="mt-3 space-y-2 text-xs text-slate-700">
                    <li className="flex items-center justify-between">
                      <span>Rehost (lift &amp; shift)</span>
                      <span className="font-semibold">38%</span>
                    </li>
                    <li className="flex items-center justify-between">
                      <span>Replatform (minor optimization)</span>
                      <span className="font-semibold">27%</span>
                    </li>
                    <li className="flex items-center justify-between">
                      <span>Refactor / modernize</span>
                      <span className="font-semibold text-emerald-700">
                        21%
                      </span>
                    </li>
                    <li className="flex items-center justify-between">
                      <span>Retire / archive</span>
                      <span className="font-semibold text-slate-700">
                        14%
                      </span>
                    </li>
                  </ul>
                </div>
              </div>

              {/* Column 2: Migration waves */}
              <div className="space-y-4">
                <div className="rounded-2xl bg-white border border-slate-200 shadow-sm p-4">
                  <h2 className="text-sm font-semibold text-slate-800">
                    Migration wave plan (sample)
                  </h2>
                  <p className="mt-1 text-xs text-slate-600">
                    Example of how CloudReadyAI would group workloads into
                    structured migration waves.
                  </p>

                  <div className="mt-3 space-y-3 text-xs">
                    <div className="rounded-xl bg-emerald-50 border border-emerald-100 px-3 py-2">
                      <p className="font-semibold text-emerald-800">
                        Wave 1 — Foundational / low-risk (25 workloads)
                      </p>
                      <p className="mt-1 text-slate-700">
                        Non-critical internal apps, Dev / Test environments,
                        and low-dependency file servers. Ideal for proving
                        out landing zone and automation.
                      </p>
                    </div>

                    <div className="rounded-xl bg-sky-50 border border-sky-100 px-3 py-2">
                      <p className="font-semibold text-sky-800">
                        Wave 2 — Business core (40 workloads)
                      </p>
                      <p className="mt-1 text-slate-700">
                        Line-of-business apps with moderate dependencies and
                        shared databases. Requires coordinated cutovers and
                        performance validation.
                      </p>
                    </div>

                    <div className="rounded-xl bg-amber-50 border border-amber-100 px-3 py-2">
                      <p className="font-semibold text-amber-800">
                        Wave 3 — High-risk / refactor (16 workloads)
                      </p>
                      <p className="mt-1 text-slate-700">
                        Legacy OS, tightly coupled integrations, or
                        significant refactoring required. Often sequenced
                        after initial cloud operating model is stable.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="rounded-2xl bg-white border border-slate-200 shadow-sm p-4">
                  <h2 className="text-sm font-semibold text-slate-800">
                    Technical risk signals (sample)
                  </h2>
                  <p className="mt-1 text-xs text-slate-600">
                    High-level areas to watch as you refine the migration
                    plan for this run.
                  </p>

                  <ul className="mt-3 space-y-2 text-xs">
                    <li className="flex items-start">
                      <span className="mt-1 mr-2 h-1.5 w-1.5 rounded-full bg-rose-500" />
                      <span>
                        <span className="font-semibold">
                          7 workloads with hard-coded IP dependencies
                        </span>{" "}
                        — may require network refactoring or private
                        connectivity patterns.
                      </span>
                    </li>
                    <li className="flex items-start">
                      <span className="mt-1 mr-2 h-1.5 w-1.5 rounded-full bg-amber-500" />
                      <span>
                        <span className="font-semibold">
                          5 databases close to capacity
                        </span>{" "}
                        — consider right-sizing or refactoring before
                        migration to avoid performance degradation.
                      </span>
                    </li>
                    <li className="flex items-start">
                      <span className="mt-1 mr-2 h-1.5 w-1.5 rounded-full bg-sky-500" />
                      <span>
                        <span className="font-semibold">
                          Mixed authentication models
                        </span>{" "}
                        — on-prem AD, local accounts, and application-level
                        auth. Align with target identity strategy early.
                      </span>
                    </li>
                  </ul>
                </div>
              </div>

              {/* Column 3: Business / readiness */}
              <div className="space-y-4">
                <div className="rounded-2xl bg-white border border-slate-200 shadow-sm p-4">
                  <h2 className="text-sm font-semibold text-slate-800">
                    Business readiness (sample)
                  </h2>
                  <p className="mt-1 text-xs text-slate-600">
                    Non-technical considerations for this assessment
                    snapshot.
                  </p>

                  <dl className="mt-3 space-y-2 text-xs text-slate-700">
                    <div className="flex items-center justify-between">
                      <dt>Stakeholder alignment</dt>
                      <dd className="font-semibold text-emerald-700">
                        Strong
                      </dd>
                    </div>
                    <div className="flex items-center justify-between">
                      <dt>Change management maturity</dt>
                      <dd className="font-semibold text-amber-700">
                        Moderate
                      </dd>
                    </div>
                    <div className="flex items-center justify-between">
                      <dt>Migration funding horizon</dt>
                      <dd className="font-semibold">18–24 months</dd>
                    </div>
                    <div className="flex items-center justify-between">
                      <dt>Operational runbook coverage</dt>
                      <dd className="font-semibold text-amber-700">
                        ~60%
                      </dd>
                    </div>
                  </dl>
                </div>

                <div className="rounded-2xl bg-white border border-slate-200 shadow-sm p-4">
                  <h2 className="text-sm font-semibold text-slate-800">
                    Next steps for this run
                  </h2>
                  <p className="mt-1 text-xs text-slate-600">
                    How CloudReadyAI would guide the next 2–3 working
                    sessions once analysis is live.
                  </p>

                  <ol className="mt-3 space-y-2 text-xs text-slate-700 list-decimal list-inside">
                    <li>
                      Confirm target scope and prioritize top 10
                      business-critical applications.
                    </li>
                    <li>
                      Finalize migration pattern per workload group (rehost,
                      replatform, refactor, retire).
                    </li>
                    <li>
                      Align migration waves with maintenance windows and
                      business events.
                    </li>
                    <li>
                      Feed agreed patterns into Cost &amp; TCO to compare
                      on-prem vs cloud scenarios.
                    </li>
                  </ol>
                </div>
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  );
};

export default AnalysisPage;
