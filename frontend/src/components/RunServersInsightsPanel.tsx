// src/components/RunServersInsightsPanel.tsx
//
// Insights panel for a run, backed by the /v1/analysis endpoints.

import React, { useEffect, useState } from "react";
import {
  fetchAnalysisSummary,
  fetchAnalysisRecommendations,
  AnalysisSummary,
  AnalysisRecommendations,
  RecommendationItem,
} from "../api/analysis";

interface Props {
  runId: string;
}

export const RunServersInsightsPanel: React.FC<Props> = ({ runId }) => {
  const [summary, setSummary] = useState<AnalysisSummary | null>(null);
  const [recs, setRecs] = useState<AnalysisRecommendations | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    async function load() {
      try {
        const [s, r] = await Promise.all([
          fetchAnalysisSummary(runId),
          fetchAnalysisRecommendations(runId),
        ]);

        if (!cancelled) {
          setSummary(s);
          setRecs(r);
        }
      } catch (e: any) {
        if (!cancelled) {
          setError(e?.message || "Failed to load analysis data.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, [runId]);

  if (loading) {
    return (
      <div className="rounded-lg border bg-white p-4 text-sm text-gray-500">
        Loading analysis insights…
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-700">
        Analysis insights could not be loaded: {error}
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="rounded-lg border bg-white p-4 text-sm text-gray-500">
        No analysis summary is available for this run yet.
      </div>
    );
  }

  const readiness = summary.readiness;
  const recommendations: RecommendationItem[] = recs?.items ?? [];

  return (
    <div className="space-y-6">
      {/* Top summary tiles */}
      <div className="grid gap-4 md:grid-cols-4">
        <Tile
          label="Total servers in scope"
          value={summary.total_servers}
        />
        <Tile
          label="Modern (non-legacy) servers"
          value={summary.modern_server_count}
        />
        <Tile
          label="Legacy / EOL servers"
          value={summary.legacy_server_count}
        />
        <Tile
          label="Ready for rehost"
          value={readiness?.ready_for_rehost ?? 0}
        />
      </div>

      {/* Environment + OS breakdown */}
      <div className="grid gap-4 md:grid-cols-2">
        <BreakdownCard
          title="By environment"
          rows={summary.environments.map((e) => ({
            label: e.name || "Unknown",
            value: e.count,
          }))}
        />
        <OSCard
          title="By OS family"
          items={summary.os_summary}
        />
      </div>

      {/* Readiness narrative */}
      <div className="rounded-lg border bg-white p-4">
        <h3 className="text-sm font-semibold text-gray-800">
          Readiness overview
        </h3>
        <div className="mt-2 text-xs text-gray-700 space-y-1">
          <div>
            <span className="font-medium">
              {readiness.ready_for_rehost}
            </span>{" "}
            servers appear suitable for a straightforward rehost.
          </div>
          <div>
            <span className="font-medium">
              {readiness.needs_modernization}
            </span>{" "}
            servers may require modernization work (OS uplift or
            refactoring).
          </div>
          <div>
            <span className="font-medium">
              {readiness.needs_investigation}
            </span>{" "}
            servers are currently flagged for further investigation.
          </div>
          {summary.notes.length > 0 && (
            <ul className="mt-2 list-disc pl-5 text-gray-600">
              {summary.notes.map((note, idx) => (
                <li key={idx}>{note}</li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Per-server recommendations */}
      <div className="rounded-lg border bg-white">
        <div className="border-b px-4 py-2 text-sm font-semibold text-gray-800">
          Per-server migration recommendations
        </div>
        <div className="max-h-96 overflow-auto">
          <table className="min-w-full text-left text-xs">
            <thead className="bg-gray-50 text-gray-600">
              <tr>
                <th className="px-3 py-2">Hostname</th>
                <th className="px-3 py-2">Environment</th>
                <th className="px-3 py-2">OS</th>
                <th className="px-3 py-2">Strategy</th>
                <th className="px-3 py-2">Risk</th>
                <th className="px-3 py-2">Wave</th>
                <th className="px-3 py-2">Summary</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {recommendations.map((item) => (
                <tr key={item.server_id}>
                  <td className="px-3 py-2 font-mono">
                    {item.hostname || item.server_id}
                  </td>
                  <td className="px-3 py-2 text-xs">
                    {item.environment || "—"}
                  </td>
                  <td className="px-3 py-2 text-xs">
                    {item.os || "—"}
                  </td>
                  <td className="px-3 py-2 text-[10px]">
                    <span className="inline-flex rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase">
                      {item.strategy}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-[10px]">
                    {item.risk_level}
                  </td>
                  <td className="px-3 py-2 text-[10px]">
                    Wave {item.wave}
                  </td>
                  <td className="px-3 py-2 text-[10px]">
                    {item.summary}
                  </td>
                </tr>
              ))}
              {recommendations.length === 0 && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-3 py-4 text-center text-xs text-gray-500"
                  >
                    No recommendations are available for this run yet.
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

interface TileProps {
  label: string;
  value: number;
}

const Tile: React.FC<TileProps> = ({ label, value }) => {
  return (
    <div className="rounded-lg border bg-white p-4">
      <div className="text-[11px] font-semibold uppercase text-gray-500">
        {label}
      </div>
      <div className="mt-2 text-2xl font-bold text-gray-900">
        {value}
      </div>
    </div>
  );
};

interface BreakdownCardRow {
  label: string;
  value: number;
}

interface BreakdownCardProps {
  title: string;
  rows: BreakdownCardRow[];
}

const BreakdownCard: React.FC<BreakdownCardProps> = ({ title, rows }) => {
  return (
    <div className="rounded-lg border bg-white p-4">
      <div className="text-xs font-semibold uppercase text-gray-500">
        {title}
      </div>
      <div className="mt-2 space-y-1 text-xs">
        {rows.length === 0 && (
          <div className="text-gray-400">No data</div>
        )}
        {rows.map((row) => (
          <div
            key={row.label}
            className="flex items-center justify-between"
          >
            <span className="truncate pr-2">{row.label}</span>
            <span className="font-mono text-gray-700">
              {row.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

interface OSCardProps {
  title: string;
  items: {
    family: string;
    count: number;
    legacy_count: number;
  }[];
}

const OSCard: React.FC<OSCardProps> = ({ title, items }) => {
  return (
    <div className="rounded-lg border bg-white p-4">
      <div className="text-xs font-semibold uppercase text-gray-500">
        {title}
      </div>
      <div className="mt-2 space-y-1 text-xs">
        {items.length === 0 && (
          <div className="text-gray-400">No data</div>
        )}
        {items.map((os) => (
          <div
            key={os.family}
            className="flex items-center justify-between"
          >
            <div className="flex flex-col pr-2">
              <span className="truncate">{os.family}</span>
              <span className="text-[10px] text-gray-500">
                {os.legacy_count} legacy / EOL
              </span>
            </div>
            <span className="font-mono text-gray-700">
              {os.count}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RunServersInsightsPanel;
