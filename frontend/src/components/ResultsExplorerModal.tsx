import React, { useEffect, useMemo, useState } from "react";

type SliceKey = "servers" | "storage" | "databases" | "applications" | "dependencies";

type Props = {
  open: boolean;
  onClose: () => void;
  runId: string;
  slice: SliceKey;
  title: string;
};

export default function ResultsExplorerModal({ open, onClose, runId, slice, title }: Props) {
  const [limit, setLimit] = useState<number>(25);
  const [offset, setOffset] = useState<number>(0);
  const [total, setTotal] = useState<number>(0);
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [err, setErr] = useState<string | null>(null);

  const page = useMemo(() => Math.floor(offset / limit) + 1, [offset, limit]);
  const totalPages = useMemo(() => (total > 0 ? Math.ceil(total / limit) : 1), [total, limit]);

  useEffect(() => {
    if (!open) return;
    // Reset paging when slice changes / modal opens
    setOffset(0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, slice, runId]);

  useEffect(() => {
    if (!open) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        setErr(null);

        const url = `/v1/ingest/results/${encodeURIComponent(slice)}?run_id=${encodeURIComponent(
          runId
        )}&limit=${encodeURIComponent(limit)}&offset=${encodeURIComponent(offset)}`;

        const res = await fetch(url);
        const txt = await res.text();
        let data: any = {};
        try {
          data = txt ? JSON.parse(txt) : {};
        } catch {
          data = { raw: txt };
        }

        if (!res.ok) {
          const msg = data?.detail || data?.message || txt || `HTTP ${res.status}`;
          throw new Error(msg);
        }

        setTotal(typeof data?.total === "number" ? data.total : 0);
        setItems(Array.isArray(data?.items) ? data.items : []);
      } catch (e: any) {
        setErr(e?.message || "Failed to load records.");
        setItems([]);
        setTotal(0);
      } finally {
        setLoading(false);
      }
    };

    void fetchData();
  }, [open, runId, slice, limit, offset]);

  const columns = useMemo(() => {
    const first = items?.[0];
    if (!first || typeof first !== "object") return [];
    // Prefer stable order: id/run_id first if present, then rest
    const keys = Object.keys(first);
    const preferred = ["id", "run_id"];
    const ordered: string[] = [];
    preferred.forEach((k) => {
      if (keys.includes(k)) ordered.push(k);
    });
    keys.forEach((k) => {
      if (!ordered.includes(k)) ordered.push(k);
    });
    return ordered.slice(0, 14); // keep table readable; details view is still possible later
  }, [items]);

  const closeOnBackdrop = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) onClose();
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50">
      {/* backdrop */}
      <div className="absolute inset-0 bg-black/40" onClick={closeOnBackdrop} />

      {/* modal */}
      <div className="absolute inset-0 flex items-center justify-center p-4">
        <div className="w-full max-w-6xl bg-white rounded-lg shadow-xl border border-gray-200 overflow-hidden">
          {/* header */}
          <div className="flex items-start justify-between px-5 py-4 border-b border-gray-200">
            <div>
              <h2 className="text-sm font-semibold text-gray-900">{title}</h2>
              <p className="text-xs text-gray-600 mt-1">
                Slice: <span className="font-mono">{slice}</span> • Run:{" "}
                <span className="font-mono">{runId}</span>
              </p>
            </div>

            <button
              className="text-xs px-3 py-1.5 rounded-md bg-white border border-gray-200 hover:bg-gray-50 text-gray-700"
              onClick={onClose}
            >
              Close
            </button>
          </div>

          {/* controls */}
          <div className="px-5 py-3 border-b border-gray-200 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="text-xs text-gray-700">
              {loading ? (
                <span>Loading…</span>
              ) : (
                <>
                  Showing <span className="font-semibold">{items.length}</span> of{" "}
                  <span className="font-semibold">{total}</span>
                </>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <label className="text-xs text-gray-600">Rows/page</label>
              <select
                className="text-xs border border-gray-200 rounded-md px-2 py-1"
                value={limit}
                onChange={(e) => {
                  const next = Number(e.target.value || 25);
                  setLimit(next);
                  setOffset(0);
                }}
              >
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>

              <div className="w-px h-5 bg-gray-200 mx-1" />

              <button
                className="text-xs px-3 py-1.5 rounded-md bg-white border border-gray-200 hover:bg-gray-50 disabled:opacity-50"
                onClick={() => setOffset(Math.max(0, offset - limit))}
                disabled={offset <= 0 || loading}
              >
                Prev
              </button>

              <div className="text-xs text-gray-600 px-2">
                Page <span className="font-semibold text-gray-900">{page}</span> /{" "}
                <span className="font-semibold text-gray-900">{totalPages}</span>
              </div>

              <button
                className="text-xs px-3 py-1.5 rounded-md bg-white border border-gray-200 hover:bg-gray-50 disabled:opacity-50"
                onClick={() => setOffset(offset + limit)}
                disabled={loading || offset + limit >= total}
              >
                Next
              </button>
            </div>
          </div>

          {/* body */}
          <div className="p-5">
            {err ? (
              <div className="border border-red-200 bg-red-50 text-red-800 text-xs rounded-md px-3 py-2">
                {err}
              </div>
            ) : null}

            <div className="mt-3 border border-gray-200 rounded-md overflow-auto max-h-[70vh]">
              <table className="min-w-full text-xs">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    {columns.length === 0 ? (
                      <th className="text-left px-3 py-2 font-semibold text-gray-700">Records</th>
                    ) : (
                      columns.map((c) => (
                        <th key={c} className="text-left px-3 py-2 font-semibold text-gray-700 whitespace-nowrap">
                          {c}
                        </th>
                      ))
                    )}
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr>
                      <td className="px-3 py-3 text-gray-500" colSpan={Math.max(1, columns.length)}>
                        Loading…
                      </td>
                    </tr>
                  ) : items.length === 0 ? (
                    <tr>
                      <td className="px-3 py-3 text-gray-500" colSpan={Math.max(1, columns.length)}>
                        No records found for this slice/run.
                      </td>
                    </tr>
                  ) : columns.length === 0 ? (
                    items.map((it, idx) => (
                      <tr key={idx} className="border-t border-gray-100">
                        <td className="px-3 py-2 text-gray-800">
                          <pre className="text-[11px] whitespace-pre-wrap">
                            {(() => {
                              try {
                                return JSON.stringify(it, null, 2);
                              } catch {
                                return String(it);
                              }
                            })()}
                          </pre>
                        </td>
                      </tr>
                    ))
                  ) : (
                    items.map((it, idx) => (
                      <tr key={idx} className="border-t border-gray-100 hover:bg-gray-50">
                        {columns.map((c) => (
                          <td key={c} className="px-3 py-2 text-gray-800 whitespace-nowrap">
                            {renderCell(it?.[c])}
                          </td>
                        ))}
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            <div className="mt-3 text-[11px] text-gray-500">
              Tip: This is read-only and paginated. We can add search/filter + column presets per slice next.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function renderCell(val: any) {
  if (val === null || val === undefined) return "—";
  if (typeof val === "boolean") return val ? "true" : "false";
  if (typeof val === "number") return String(val);
  if (typeof val === "string") return val.length > 60 ? val.slice(0, 57) + "…" : val;
  try {
    const s = JSON.stringify(val);
    return s.length > 60 ? s.slice(0, 57) + "…" : s;
  } catch {
    return String(val);
  }
}
