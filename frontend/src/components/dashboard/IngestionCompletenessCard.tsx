import React from "react";
import type { RunSummaryV2 } from "../../types/runSummaryV2";

type SliceKey =
  | "servers"
  | "storage"
  | "network"
  | "databases"
  | "applications"
  | "business"
  | "dependencies"
  | "os"
  | "licensing"
  | "utilization";

type SliceStatus = "present" | "partial" | "missing";

interface SliceInfo {
  key: SliceKey;
  label: string;
  countLabel: string;
  status: SliceStatus;
  weight: number;
}

const SLICE_WEIGHTS: Record<SliceKey, number> = {
  servers: 2,
  storage: 1.5,
  network: 1,
  databases: 2,
  applications: 2,
  business: 1,
  dependencies: 1,
  os: 1,
  licensing: 0.5,
  utilization: 1,
};

function computeSlices(summary: RunSummaryV2 | null | undefined): SliceInfo[] {
  if (!summary) {
    return [];
  }

  const serverCount = summary.servers?.totals?.server_count ?? 0;
  const storageCount = summary.storage?.totals?.volume_count ?? 0;
  const networkCount = summary.network?.device_count ?? 0;
  const dbCount = summary.databases?.totals?.db_count ?? 0;
  const appCount = summary.applications?.totals?.app_count ?? 0;
  const businessCriticality =
    summary.business?.by_criticality?.length ?? 0;
  const businessSla = summary.business?.by_sla_tier?.length ?? 0;
  const depCount = summary.dependencies?.dependency_count ?? 0;
  const osEntries = summary.os?.by_name?.length ?? 0;
  const licensingProducts =
    summary.licensing?.by_product?.length ?? 0;
  const utilServers = summary.utilization?.servers_with_metrics ?? 0;

  const slices: SliceInfo[] = [];

  // Helpers to push rows
  const push = (
    key: SliceKey,
    label: string,
    countLabel: string,
    status: SliceStatus
  ) => {
    slices.push({
      key,
      label,
      countLabel,
      status,
      weight: SLICE_WEIGHTS[key],
    });
  };

  // Servers
  push(
    "servers",
    "Servers",
    serverCount === 1 ? "1 server" : `${serverCount} servers`,
    serverCount > 0 ? "present" : "missing"
  );

  // Storage
  push(
    "storage",
    "Storage",
    storageCount === 1 ? "1 volume" : `${storageCount} volumes`,
    storageCount > 0 ? "present" : "missing"
  );

  // Network
  push(
    "network",
    "Network",
    networkCount === 1 ? "1 record" : `${networkCount} records`,
    networkCount > 0 ? "present" : "missing"
  );

  // Databases
  push(
    "databases",
    "Databases",
    dbCount === 1 ? "1 DB" : `${dbCount} DBs`,
    dbCount > 0 ? "present" : "missing"
  );

  // Applications
  push(
    "applications",
    "Applications",
    appCount === 1 ? "1 app" : `${appCount} apps`,
    appCount > 0 ? "present" : "missing"
  );

  // Business metadata
  const businessPresent = businessCriticality + businessSla > 0;
  push(
    "business",
    "Business metadata",
    businessPresent
      ? `${businessCriticality || 0} criticality tiers`
      : "No business metadata",
    businessPresent ? "present" : "missing"
  );

  // App dependencies – treat as partial if we have apps but no deps
  let depsStatus: SliceStatus = "missing";
  if (depCount > 0) {
    depsStatus = "present";
  } else if (appCount > 0 && depCount === 0) {
    depsStatus = "partial";
  }
  push(
    "dependencies",
    "App dependencies",
    depCount === 1 ? "1 link" : `${depCount} links`,
    depsStatus
  );

  // OS metadata
  push(
    "os",
    "OS metadata",
    osEntries === 1 ? "1 OS entry" : `${osEntries} OS entries`,
    osEntries > 0 ? "present" : "missing"
  );

  // Licensing
  push(
    "licensing",
    "Licensing",
    licensingProducts === 1
      ? "1 product"
      : `${licensingProducts} products`,
    licensingProducts > 0 ? "present" : "missing"
  );

  // Utilization – partial if some servers have metrics, but not all
  let utilStatus: SliceStatus = "missing";
  if (utilServers === 0) {
    utilStatus = "missing";
  } else if (serverCount > 0 && utilServers < serverCount) {
    utilStatus = "partial";
  } else {
    utilStatus = "present";
  }
  push(
    "utilization",
    "Utilization metrics",
    utilServers === 1
      ? "1 server with metrics"
      : `${utilServers} servers with metrics`,
    utilStatus
  );

  return slices;
}

function statusCoverage(status: SliceStatus): number {
  if (status === "present") return 1.0;
  if (status === "partial") return 0.5;
  return 0.0;
}

function statusBadge(status: SliceStatus) {
  const base =
    "inline-flex items-center justify-center rounded-full px-1.5 py-0.5 text-[11px] font-semibold";

  if (status === "present") {
    return (
      <span
        className={`${base} bg-emerald-50 text-emerald-700 border border-emerald-200`}
        aria-label="Ingestion present"
      >
        ✓
      </span>
    );
  }

  if (status === "partial") {
    return (
      <span
        className={`${base} bg-amber-50 text-amber-700 border border-amber-200`}
        aria-label="Partially ingested"
      >
        ✓
      </span>
    );
  }

  return (
    <span
      className={`${base} bg-slate-50 text-slate-400 border border-slate-200`}
      aria-label="Missing"
    >
      –
    </span>
  );
}

export interface IngestionCompletenessCardProps {
  activeRunId: string | null;
  summary: RunSummaryV2 | null | undefined;
  isLoading: boolean;
}

export function IngestionCompletenessCard({
  activeRunId,
  summary,
  isLoading,
}: IngestionCompletenessCardProps) {
  const slices = computeSlices(summary);
  const totalSlices = slices.length || 10; // we still target 10
  const nonMissingCount = slices.filter(
    (s) => s.status !== "missing"
  ).length;

  const totalWeight = slices.reduce(
    (acc, s) => acc + s.weight,
    0
  );
  const weightedCoverage = slices.reduce((acc, s) => {
    return acc + s.weight * statusCoverage(s.status);
  }, 0);

  const score =
    totalWeight > 0
      ? Math.round((weightedCoverage / totalWeight) * 100)
      : 0;

  let scoreLabel = "Insufficient";
  if (score >= 90) scoreLabel = "Comprehensive";
  else if (score >= 70) scoreLabel = "Good";
  else if (score >= 40) scoreLabel = "Partial";

  const showPlaceholder = !activeRunId;

  return (
    <div className="space-y-4">
      {/* Overall score box */}
      <div className="rounded-xl border border-slate-200 bg-slate-50/60 px-4 py-3 flex items-center justify-between gap-4">
        <div className="space-y-1">
          <p className="text-xs font-semibold tracking-wide text-slate-600 uppercase">
            Overall Ingestion Completeness
          </p>
          {showPlaceholder && (
            <p className="text-xs text-slate-500">
              Enter a Run ID in the <span className="font-semibold">Run Summary</span>{" "}
              card to check how complete this assessment&apos;s ingestion is.
            </p>
          )}
          {!showPlaceholder && isLoading && (
            <p className="text-xs text-slate-500">
              Loading completeness for{" "}
              <span className="font-mono">{activeRunId}</span>…
            </p>
          )}
          {!showPlaceholder && !isLoading && summary && (
            <p className="text-xs text-slate-600">
              {nonMissingCount}/{totalSlices} ingestion slices populated for run{" "}
              <span className="font-mono">{activeRunId}</span>.
            </p>
          )}
          {!showPlaceholder && !isLoading && !summary && (
            <p className="text-xs text-red-600">
              No ingestion data found for this run.
            </p>
          )}
        </div>
        <div className="text-right">
          <p className="text-[11px] font-medium text-slate-500 uppercase tracking-wide">
            Assessment score
          </p>
          <p className="text-2xl font-bold text-slate-900 leading-none">
            {score}%
          </p>
          <p className="text-[11px] text-slate-500">{scoreLabel}</p>
        </div>
      </div>

      {/* Slices grid */}
      <div className="rounded-xl border border-slate-200 bg-white px-4 py-3">
        <p className="text-xs font-semibold tracking-wide text-slate-600 uppercase mb-3">
          Ingestion Slices ({totalSlices})
        </p>

        {showPlaceholder && (
          <p className="text-xs text-slate-500">
            Enter a Run ID in the <span className="font-semibold">Run Summary</span>{" "}
            card to check ingestion slices.
          </p>
        )}

        {!showPlaceholder && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2">
            {slices.map((slice) => (
              <div
                key={slice.key}
                className="flex items-center justify-between gap-2 text-xs"
              >
                <div className="flex flex-col">
                  <span className="text-sm font-medium text-slate-800">
                    {slice.label}
                  </span>
                  <span className="text-[11px] text-slate-500">
                    {slice.countLabel}
                  </span>
                </div>
                {statusBadge(slice.status)}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
