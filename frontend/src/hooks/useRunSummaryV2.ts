import { useEffect, useState } from "react";
import type { RunSummaryV2 } from "../types/runSummaryV2";

interface UseRunSummaryV2Result {
  data?: RunSummaryV2;
  loading: boolean;
  error?: string | null;
}

export function useRunSummaryV2(runId?: string): UseRunSummaryV2Result {
  const [data, setData] = useState<RunSummaryV2 | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // If no runId yet, don’t fetch, just reset state
    if (!runId) {
      setData(undefined);
      setLoading(false);
      setError(null);
      return;
    }

    let cancelled = false;

    async function fetchSummary() {
      setLoading(true);
      setError(null);

      try {
        const resp = await fetch(`/v1/runs/${runId}/summary/v2`);
        if (!resp.ok) {
          throw new Error(`HTTP ${resp.status}`);
        }

        const json = (await resp.json()) as RunSummaryV2;
        if (!cancelled) {
          setData(json);
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err?.message ?? "Failed to load run summary");
          setData(undefined);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchSummary();

    return () => {
      cancelled = true;
    };
  }, [runId]);

  return { data, loading, error };
}
