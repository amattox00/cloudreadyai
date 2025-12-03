#!/usr/bin/env bash
set -euo pipefail

echo "==[ Phase 6 – Add Cloud Intelligence Mode Status UI ]=="

FRONTEND_DIR="$HOME/cloudreadyai/frontend"
cd "$FRONTEND_DIR"

# 0) Determine diagrams page file (we'll attach the banner here)
if [[ -f "src/pages/DiagramsPage.tsx" ]]; then
  DIAGRAM_PAGE="src/pages/DiagramsPage.tsx"
else
  echo "ERROR: Could not find src/pages/DiagramsPage.tsx"
  exit 1
fi

echo "Using diagrams page: $DIAGRAM_PAGE"

# 1) Create the CloudIntelligenceModeBanner component
mkdir -p src/components

cat > src/components/CloudIntelligenceModeBanner.tsx << 'TSXEOF'
import React, { useEffect, useState } from "react";

type ProviderMode = {
  provider: string;
  mode: "mock" | "hybrid" | "live";
  live_enabled?: boolean;
  notes?: string;
};

type ProvidersResponse = {
  global_mode: "mock" | "hybrid" | "live";
  providers: ProviderMode[];
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
        const json = await res.json();
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

  return wrap(
    <div>
      <div style={{ marginBottom: "0.5rem" }}>
        <strong>Cloud Intelligence Engine</strong>{" "}
        <span style={{ fontSize: "0.85rem", opacity: 0.8 }}>
          (Phase 6 mode: <code>{data.global_mode}</code>)
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
            {data.providers.map((p) => (
              <tr key={p.provider}>
                <td style={{ padding: "0.25rem 0.5rem" }}>
                  {p.provider.toUpperCase()}
                </td>
                <td style={{ padding: "0.25rem 0.5rem" }}>
                  <code>{p.mode}</code>
                </td>
                <td style={{ padding: "0.25rem 0.5rem" }}>
                  {p.live_enabled ? "Yes" : "No"}
                </td>
                <td style={{ padding: "0.25rem 0.5rem" }}>
                  {p.notes || "\u2014"}
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
TSXEOF

echo "Created src/components/CloudIntelligenceModeBanner.tsx"

# 2) Ensure DiagramsPage imports the component and useEffect

# 2a) Make sure useEffect is imported along with useState
if grep -q 'import React, { ' "$DIAGRAM_PAGE"; then
  perl -0pi -e 's/import React, { ([^}]*) } from "react";/import React, { $1, useEffect } from "react";/' "$DIAGRAM_PAGE"
elif grep -q 'import React from "react";' "$DIAGRAM_PAGE"; then
  perl -0pi -e 's/import React from "react";/import React, { useEffect, useState } from "react";/' "$DIAGRAM_PAGE"
fi

# 2b) Add the component import if not already present
if ! grep -q "CloudIntelligenceModeBanner" "$DIAGRAM_PAGE"; then
  perl -0pi -e 's|(import .*\n)(?=type CloudProvider|type DiagramType|type OverlayProfile)|$1import { CloudIntelligenceModeBanner } from "../components/CloudIntelligenceModeBanner";\n\n|;' "$DIAGRAM_PAGE" || true

  # Fallback: if the above pattern fails, append import after first import block
  if ! grep -q "CloudIntelligenceModeBanner" "$DIAGRAM_PAGE"; then
    perl -0pi -e 's|(\nimport .*?from "react";\n)|$1import { CloudIntelligenceModeBanner } from "../components/CloudIntelligenceModeBanner";\n|;' "$DIAGRAM_PAGE"
  fi
fi

# 2c) Inject the banner JSX near the top of the returned layout
if ! grep -q "CloudIntelligenceModeBanner" "$DIAGRAM_PAGE"; then
  # Try to insert right after the first 'return ('
  perl -0pi -e 's/return \(\n/return (\n    <CloudIntelligenceModeBanner \/>\n\n/' "$DIAGRAM_PAGE" || true
fi

echo "Phase 6 mode status banner wiring complete (frontend)."
