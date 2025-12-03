import React, { useEffect, useState } from "react";

type ProvidersResponse = {
  mode: "mock" | "hybrid" | "live";
  providers: string[];
};

export const CloudIntelligenceModeBanner: React.FC = () => {
  const [data, setData] = useState<ProvidersResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch("/v1/phase6/providers");
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        const json = (await res.json()) as ProvidersResponse;
        setData(json);
      } catch (err: any) {
        setError(err?.message || "Unable to load Cloud Intelligence status");
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
  }, []);

  const wrap = (children: React.ReactNode) => (
    <div
      style={{
        margin: "1rem 0",
        padding: "0.75rem 1rem",
        borderRadius: "8px",
        border: "1px solid #e0e0e0",
        background: "#fafafa",
        fontSize: "0.9rem",
      }}
    >
      {children}
    </div>
  );

  if (loading) {
    return wrap(<span>Cloud Intelligence status: loading…</span>);
  }

  if (error) {
    return wrap(
      <span>
        Cloud Intelligence status: <strong>error</strong> ({error})
      </span>
    );
  }

  if (!data) {
    return wrap(<span>Cloud Intelligence status: unavailable</span>);
  }

  const providers = data.providers || [];

  return wrap(
    <div>
      <div style={{ marginBottom: "0.5rem" }}>
        <strong>Cloud Intelligence Engine</strong>{" "}
        <span style={{ fontSize: "0.85rem", opacity: 0.8 }}>
          (Phase 6 global mode: <code>{data.mode}</code>)
        </span>
      </div>
      <div style={{ overflowX: "auto" }}>
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            fontSize: "0.85rem",
          }}
        >
          <thead>
            <tr>
              <th
                style={{
                  textAlign: "left",
                  padding: "0.25rem 0.5rem",
                  borderBottom: "1px solid #ddd",
                }}
              >
                Provider
              </th>
              <th
                style={{
                  textAlign: "left",
                  padding: "0.25rem 0.5rem",
                  borderBottom: "1px solid #ddd",
                }}
              >
                Mode
              </th>
              <th
                style={{
                  textAlign: "left",
                  padding: "0.25rem 0.5rem",
                  borderBottom: "1px solid #ddd",
                }}
              >
                Live Enabled?
              </th>
              <th
                style={{
                  textAlign: "left",
                  padding: "0.25rem 0.5rem",
                  borderBottom: "1px solid #ddd",
                }}
              >
                Notes
              </th>
            </tr>
          </thead>
          <tbody>
            {providers.map((p) => (
              <tr key={p}>
                <td style={{ padding: "0.25rem 0.5rem" }}>
                  {p.toUpperCase()}
                </td>
                <td style={{ padding: "0.25rem 0.5rem" }}>
                  <code>{data.mode}</code>
                </td>
                <td style={{ padding: "0.25rem 0.5rem" }}>
                  {/* For now we treat this as a global mode; when per-provider flags exist
                      we can wire them in here. */}
                  {data.mode === "live" ? "Yes (requires CSP creds)" : "No"}
                </td>
                <td style={{ padding: "0.25rem 0.5rem" }}>
                  {data.mode === "mock"
                    ? "Using internal sample data only."
                    : data.mode === "hybrid"
                    ? "Will try live CSP APIs when configured; falls back to mock."
                    : "Uses live CSP APIs only; ensure credentials and IAM are configured."}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div
        style={{
          marginTop: "0.5rem",
          fontSize: "0.8rem",
          opacity: 0.8,
          lineHeight: 1.4,
        }}
      >
        <div>
          <strong>mock</strong>: uses only internal sample data (no CSP calls).
        </div>
        <div>
          <strong>hybrid</strong>: tries live CSP pricing/instance APIs, falls
          back to mock data on errors.
        </div>
        <div>
          <strong>live</strong>: uses CSP APIs only (no mock fallback).
        </div>
      </div>
    </div>
  );
};
