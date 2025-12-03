#!/usr/bin/env bash
set -euo pipefail

echo "==[ Phase 7E – Rewrite DiagramsPage.tsx with login + generator UI ]=="

cd ~/cloudreadyai/frontend

cat > src/pages/DiagramsPage.tsx << 'TSX'
import React, { useState } from "react";
import CloudIntelligenceModeBanner from "../components/CloudIntelligenceModeBanner";

type CloudProvider = "aws" | "azure" | "gcp";
type DiagramType = "landing_zone" | "network" | "application";
type OverlayProfile = "none" | "fedramp_high" | "dod" | "zero_trust";

export default function DiagramsPage() {
  // --- Dev auth state ---
  const [email, setEmail] = useState("dev@cloudreadyai.com");
  const [password, setPassword] = useState("test");
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [meJson, setMeJson] = useState<string | null>(null);
  const [authError, setAuthError] = useState<string | null>(null);
  const [loggingIn, setLoggingIn] = useState(false);

  // --- Diagram generator state ---
  const [cloud, setCloud] = useState<CloudProvider>("aws");
  const [diagramType, setDiagramType] = useState<DiagramType>("landing_zone");
  const [overlayProfile, setOverlayProfile] = useState<OverlayProfile>("none");
  const [orgName, setOrgName] = useState("");
  const [environment, setEnvironment] = useState("");
  const [workloadName, setWorkloadName] = useState("");
  const [workloadId, setWorkloadId] = useState("");
  const [generateError, setGenerateError] = useState<string | null>(null);
  const [diagramXml, setDiagramXml] = useState<string | null>(null);
  const [packageStatus, setPackageStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const isLoggedIn = !!accessToken;

  // ---------------- Dev auth handlers ----------------

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoggingIn(true);
    setAuthError(null);
    setMeJson(null);

    try {
      const resp = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!resp.ok) {
        const text = await resp.text();
        setAuthError(`Login failed (${resp.status}): ${text}`);
        return;
      }

      const data = await resp.json();
      setAccessToken(data.access_token ?? null);
      setAuthError(null);
    } catch (err: any) {
      setAuthError(`Login error: ${String(err)}`);
    } finally {
      setLoggingIn(false);
    }
  }

  async function handleWhoAmI() {
    if (!accessToken) {
      setMeJson("No access token yet");
      return;
    }

    try {
      const resp = await fetch("/auth/me", {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      const text = await resp.text();
      setMeJson(text);
    } catch (err: any) {
      setMeJson(`Error calling /auth/me: ${String(err)}`);
    }
  }

  // --------------- Diagram Generator 2.0 handlers ----------------

  async function handleGenerateDiagramV2() {
    setBusy(true);
    setGenerateError(null);
    setDiagramXml(null);

    try {
      const payload: any = {
        cloud,
        diagram_type: diagramType,
        overlay_profile: overlayProfile,
      };

      if (workloadId.trim()) {
        payload.workload_id = workloadId.trim();
      }

      if (orgName.trim()) payload.org_name = orgName.trim();
      if (environment.trim()) payload.environment = environment.trim();
      if (workloadName.trim()) payload.workload_name = workloadName.trim();

      const resp = await fetch("/v1/diagram/generate_v2", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!resp.ok) {
        const text = await resp.text();
        setGenerateError(
          `Diagram generation failed (${resp.status}): ${text}`
        );
        return;
      }

      const data = await resp.json();
      if (!data.xml) {
        setGenerateError("Response did not contain XML.");
        return;
      }

      setDiagramXml(data.xml);
    } catch (err: any) {
      setGenerateError(`Error calling /v1/diagram/generate_v2: ${String(err)}`);
    } finally {
      setBusy(false);
    }
  }

  async function handleDownloadPackageV2() {
    setBusy(true);
    setPackageStatus("Requesting deliverables package...");
    setGenerateError(null);

    try {
      const payload: any = {};

      if (workloadId.trim()) {
        payload.workload_id = workloadId.trim();
      }

      const resp = await fetch("/v1/deliverables/package_v2", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!resp.ok) {
        const text = await resp.text();
        setPackageStatus(
          `Deliverables packaging failed (${resp.status}): ${text}`
        );
        return;
      }

      const data = await resp.json();
      if (!data.zip_filename || !data.zip_base64) {
        setPackageStatus("Response did not include zip data.");
        return;
      }

      const byteCharacters = atob(data.zip_base64);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: "application/zip" });

      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = data.zip_filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);

      setPackageStatus(`Download started: ${data.zip_filename}`);
    } catch (err: any) {
      setPackageStatus(
        `Error calling /v1/deliverables/package_v2: ${String(err)}`
      );
    } finally {
      setBusy(false);
    }
  }

  // ----------------------- RENDER -----------------------

  return (
    <div style={{ maxWidth: "1100px", margin: "2rem auto", padding: "0 1rem" }}>
      <h1 style={{ fontSize: "2.5rem", marginBottom: "1.5rem" }}>
        CloudReadyAI
      </h1>

      {/* Login panel always visible, but once logged in we show a small banner instead of error */}
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: "8px",
          padding: "1.5rem",
          marginBottom: "1.5rem",
        }}
      >
        <h2 style={{ fontSize: "1.4rem", marginBottom: "1rem" }}>Login</h2>

        <form
          onSubmit={handleLogin}
          style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}
        >
          <label style={{ display: "flex", flexDirection: "column" }}>
            <span>Email</span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{ padding: "0.4rem", fontSize: "0.95rem" }}
            />
          </label>

          <label style={{ display: "flex", flexDirection: "column" }}>
            <span>Password</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ padding: "0.4rem", fontSize: "0.95rem" }}
            />
          </label>

          <button
            type="submit"
            disabled={loggingIn}
            style={{
              padding: "0.5rem 1.2rem",
              fontSize: "0.95rem",
              cursor: "pointer",
              alignSelf: "flex-start",
            }}
          >
            {loggingIn ? "Logging in..." : "Login"}
          </button>
        </form>

        {accessToken && (
          <div style={{ marginTop: "0.75rem", fontSize: "0.9rem" }}>
            <strong>Access Token:</strong> {accessToken}
          </div>
        )}
        {authError && (
          <div style={{ marginTop: "0.75rem", color: "red" }}>Error: {authError}</div>
        )}

        <div
          style={{
            marginTop: "1.25rem",
            paddingTop: "1rem",
            borderTop: "1px solid #eee",
          }}
        >
          <h3 style={{ marginBottom: "0.5rem" }}>Who am I?</h3>
          <button
            type="button"
            onClick={handleWhoAmI}
            disabled={!accessToken}
            style={{
              padding: "0.4rem 0.9rem",
              fontSize: "0.9rem",
              cursor: accessToken ? "pointer" : "not-allowed",
            }}
          >
            Call /auth/me
          </button>

          {meJson && (
            <pre
              style={{
                marginTop: "0.75rem",
                padding: "0.75rem",
                background: "#f7f7f7",
                borderRadius: "4px",
                fontSize: "0.85rem",
              }}
            >
              {meJson}
            </pre>
          )}
        </div>
      </div>

      {/* After login, show Cloud Intelligence mode banner + diagram generator */}
      {isLoggedIn && (
        <>
          <CloudIntelligenceModeBanner />

          <div
            style={{
              border: "1px solid #ddd",
              borderRadius: "8px",
              padding: "1.5rem",
              marginTop: "1.5rem",
              marginBottom: "1.5rem",
            }}
          >
            <h2 style={{ fontSize: "1.4rem", marginBottom: "1rem" }}>
              Diagram Generator 2.0
            </h2>

            <div
              style={{
                display: "grid",
                gap: "0.75rem",
                gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                marginBottom: "1rem",
              }}
            >
              <label style={{ display: "flex", flexDirection: "column" }}>
                <span>Cloud Provider</span>
                <select
                  value={cloud}
                  onChange={(e) => setCloud(e.target.value as CloudProvider)}
                  style={{ padding: "0.4rem" }}
                >
                  <option value="aws">AWS</option>
                  <option value="azure">Azure</option>
                  <option value="gcp">GCP</option>
                </select>
              </label>

              <label style={{ display: "flex", flexDirection: "column" }}>
                <span>Diagram Type</span>
                <select
                  value={diagramType}
                  onChange={(e) =>
                    setDiagramType(e.target.value as DiagramType)
                  }
                  style={{ padding: "0.4rem" }}
                >
                  <option value="landing_zone">Landing Zone</option>
                  <option value="network">Network Topology</option>
                  <option value="application">Application Flow</option>
                </select>
              </label>

              <label style={{ display: "flex", flexDirection: "column" }}>
                <span>Overlay Profile</span>
                <select
                  value={overlayProfile}
                  onChange={(e) =>
                    setOverlayProfile(e.target.value as OverlayProfile)
                  }
                  style={{ padding: "0.4rem" }}
                >
                  <option value="none">None</option>
                  <option value="fedramp_high">FedRAMP High</option>
                  <option value="dod">DoD / IL overlays</option>
                  <option value="zero_trust">Zero Trust</option>
                </select>
              </label>

              <label style={{ display: "flex", flexDirection: "column" }}>
                <span>Organization Name</span>
                <input
                  type="text"
                  value={orgName}
                  onChange={(e) => setOrgName(e.target.value)}
                  placeholder="e.g. 5NINE Data Solutions"
                  style={{ padding: "0.4rem" }}
                />
              </label>

              <label style={{ display: "flex", flexDirection: "column" }}>
                <span>Environment</span>
                <input
                  type="text"
                  value={environment}
                  onChange={(e) => setEnvironment(e.target.value)}
                  placeholder="e.g. Prod"
                  style={{ padding: "0.4rem" }}
                />
              </label>

              <label style={{ display: "flex", flexDirection: "column" }}>
                <span>Workload Name</span>
                <input
                  type="text"
                  value={workloadName}
                  onChange={(e) => setWorkloadName(e.target.value)}
                  placeholder="e.g. CloudReadyAI"
                  style={{ padding: "0.4rem" }}
                />
              </label>

              <label style={{ display: "flex", flexDirection: "column" }}>
                <span>Workload ID (optional)</span>
                <input
                  type="text"
                  value={workloadId}
                  onChange={(e) => setWorkloadId(e.target.value)}
                  placeholder="e.g. wl-sample-3tier-001"
                  style={{ padding: "0.4rem" }}
                />
              </label>
            </div>

            <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
              <button
                type="button"
                onClick={handleGenerateDiagramV2}
                disabled={busy}
                style={{
                  padding: "0.5rem 1.2rem",
                  fontSize: "0.95rem",
                  cursor: busy ? "wait" : "pointer",
                }}
              >
                {busy ? "Working..." : "Generate Diagram (v2)"}
              </button>

              <button
                type="button"
                onClick={handleDownloadPackageV2}
                disabled={busy}
                style={{
                  padding: "0.5rem 1.2rem",
                  fontSize: "0.95rem",
                  cursor: busy ? "wait" : "pointer",
                }}
              >
                Download Deliverables Package (v2)
              </button>
            </div>

            {generateError && (
              <div style={{ marginTop: "0.75rem", color: "red" }}>
                Error: {generateError}
              </div>
            )}
            {packageStatus && (
              <div style={{ marginTop: "0.75rem" }}>{packageStatus}</div>
            )}

            {diagramXml && (
              <div style={{ marginTop: "1.25rem" }}>
                <h3 style={{ marginBottom: "0.5rem" }}>
                  Raw draw.io XML (preview)
                </h3>
                <textarea
                  readOnly
                  value={diagramXml}
                  style={{
                    width: "100%",
                    minHeight: "220px",
                    fontFamily: "monospace",
                    fontSize: "0.8rem",
                    padding: "0.75rem",
                  }}
                />
                <p style={{ marginTop: "0.5rem", fontSize: "0.85rem" }}>
                  Tip: copy this XML into{" "}
                  <a
                    href="https://app.diagrams.net/"
                    target="_blank"
                    rel="noreferrer"
                  >
                    draw.io
                  </a>{" "}
                  using <em>File → Import From → XML</em>.
                </p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
TSX

echo "DiagramsPage.tsx rewritten."

