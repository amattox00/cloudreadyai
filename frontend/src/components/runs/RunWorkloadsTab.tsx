import React, { useEffect, useState } from "react";
import type { Workload } from "../../api/analysis";
import { fetchWorkloads, rebuildWorkloads } from "../../api/analysis";

type Props = {
  runId: string;
};

export const RunWorkloadsTab: React.FC<Props> = ({ runId }) => {
  const [workloads, setWorkloads] = useState<Workload[]>([]);
  const [loading, setLoading] = useState(false);
  const [rebuilding, setRebuilding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchWorkloads(runId);
      setWorkloads(data.workloads ?? []);
    } catch (err: any) {
      setError(err.message ?? "Failed to load workloads");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [runId]);

  const handleRebuild = async () => {
    try {
      setRebuilding(true);
      setError(null);
      const data = await rebuildWorkloads(runId);
      setWorkloads(data.workloads ?? []);
    } catch (err: any) {
      setError(err.message ?? "Failed to rebuild workloads");
    } finally {
      setRebuilding(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-2">
        <div>
          <h3 className="text-lg font-semibold">Workloads</h3>
          <p className="text-sm text-gray-500">
            Grouped application workloads inferred from servers and databases in
            this run.
          </p>
        </div>
        <button
          onClick={handleRebuild}
          disabled={rebuilding}
          className="px-3 py-1.5 rounded-md border text-sm disabled:opacity-50"
        >
          {rebuilding ? "Rebuilding…" : "Rebuild Workloads"}
        </button>
      </div>

      {loading && <div className="text-sm text-gray-500">Loading workloads…</div>}
      {error && <div className="text-sm text-red-600">{error}</div>}

      {!loading && !error && workloads.length === 0 && (
        <div className="text-sm text-gray-500">
          No workloads found yet. Try clicking &quot;Rebuild Workloads&quot;
          above.
        </div>
      )}

      {!loading && workloads.length > 0 && (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm border border-gray-200 rounded-md overflow-hidden">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 py-2 text-left font-medium">Name</th>
                <th className="px-3 py-2 text-left font-medium">Type</th>
                <th className="px-3 py-2 text-left font-medium">Env</th>
                <th className="px-3 py-2 text-left font-medium">Servers</th>
                <th className="px-3 py-2 text-left font-medium">Databases</th>
              </tr>
            </thead>
            <tbody>
              {workloads.map((w) => {
                const serverCount = w.components.filter(
                  (c) => c.component_type === "server"
                ).length;
                const dbCount = w.components.filter(
                  (c) => c.component_type === "database"
                ).length;

                return (
                  <tr key={w.id} className="border-t border-gray-200">
                    <td className="px-3 py-2">{w.name}</td>
                    <td className="px-3 py-2">{w.type}</td>
                    <td className="px-3 py-2">{w.environment ?? "-"}</td>
                    <td className="px-3 py-2">{serverCount}</td>
                    <td className="px-3 py-2">{dbCount}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
