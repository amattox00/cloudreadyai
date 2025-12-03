import React from "react";
import { Link } from "react-router-dom";

const pageStyle: React.CSSProperties = {
  minHeight: "100vh",
  margin: 0,
  padding: "32px 0",
  display: "flex",
  justifyContent: "center",
  background:
    "linear-gradient(135deg, #22c55e 0%, #0f172a 40%, #020617 100%)",
  fontFamily:
    'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  color: "#e5e7eb",
};

const containerStyle: React.CSSProperties = {
  width: "100%",
  maxWidth: "1100px",
  padding: "0 24px",
};

const topBarStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: "24px",
};

const brandStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
};

const brandNameStyle: React.CSSProperties = {
  fontSize: "22px",
  fontWeight: 600,
};

const brandTaglineStyle: React.CSSProperties = {
  fontSize: "12px",
  color: "#9ca3af",
};

const navStyle: React.CSSProperties = {
  display: "flex",
  gap: "12px",
  fontSize: "13px",
};

const navLinkStyle: React.CSSProperties = {
  padding: "6px 12px",
  borderRadius: "999px",
  textDecoration: "none",
  color: "#e5e7eb",
  border: "1px solid rgba(148,163,184,0.5)",
  backgroundColor: "rgba(15,23,42,0.7)",
};

const navLinkPrimaryStyle: React.CSSProperties = {
  ...navLinkStyle,
  border: "none",
  background:
    "linear-gradient(to right, #0ea5e9, #22c55e)",
  color: "#020617",
  fontWeight: 600,
};

const headingStyle: React.CSSProperties = {
  fontSize: "24px",
  fontWeight: 600,
  marginBottom: "6px",
};

const headingSubStyle: React.CSSProperties = {
  fontSize: "13px",
  color: "#9ca3af",
  marginBottom: "20px",
};

const gridStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "minmax(0, 1.5fr) minmax(0, 1fr)",
  gap: "18px",
  marginBottom: "16px",
};

const cardStyle: React.CSSProperties = {
  background:
    "radial-gradient(circle at top left, rgba(56,189,248,0.18), transparent 55%), rgba(15,23,42,0.95)",
  borderRadius: "24px",
  padding: "20px",
  boxShadow: "0 18px 45px rgba(15,23,42,0.9)",
  border: "1px solid rgba(30,64,175,0.6)",
};

const sectionTitleStyle: React.CSSProperties = {
  fontSize: "15px",
  fontWeight: 600,
  marginBottom: "6px",
};

const sectionSubStyle: React.CSSProperties = {
  fontSize: "12px",
  color: "#9ca3af",
  marginBottom: "12px",
};

const buttonRowStyle: React.CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: "10px",
  marginTop: "10px",
};

const primaryButtonStyle: React.CSSProperties = {
  padding: "8px 16px",
  borderRadius: "999px",
  border: "none",
  background:
    "linear-gradient(to right, #0ea5e9, #22c55e)",
  color: "#020617",
  fontWeight: 600,
  fontSize: "13px",
  cursor: "pointer",
  textDecoration: "none",
};

const secondaryButtonStyle: React.CSSProperties = {
  padding: "8px 16px",
  borderRadius: "999px",
  border: "1px solid rgba(148,163,184,0.6)",
  backgroundColor: "rgba(15,23,42,0.9)",
  color: "#e5e7eb",
  fontSize: "13px",
  cursor: "pointer",
  textDecoration: "none",
};

const badgeStyle: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  borderRadius: "999px",
  padding: "3px 9px",
  fontSize: "10px",
  textTransform: "uppercase",
  letterSpacing: "0.04em",
  backgroundColor: "rgba(15,23,42,0.9)",
  border: "1px solid rgba(52,211,153,0.7)",
  color: "#6ee7b7",
};

const smallTextStyle: React.CSSProperties = {
  fontSize: "11px",
  color: "#9ca3af",
  marginTop: "10px",
  lineHeight: 1.5,
};

const threeColGridStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
  gap: "16px",
};

const Dashboard: React.FC = () => {
  return (
    <div style={pageStyle}>
      <div style={containerStyle}>
        {/* Top bar */}
        <div style={topBarStyle}>
          <div style={brandStyle}>
            <div style={brandNameStyle}>CloudReadyAI</div>
            <div style={brandTaglineStyle}>
              Migration Assessment &amp; Architecture Workspace
            </div>
          </div>
          <nav style={navStyle}>
            <Link to="/dashboard" style={navLinkPrimaryStyle}>
              Dashboard
            </Link>
            <Link to="/diagrams" style={navLinkStyle}>
              Diagrams
            </Link>
          </nav>
        </div>

        {/* Heading */}
        <div>
          <div style={headingStyle}>Assessment Workspace</div>
          <div style={headingSubStyle}>
            Start a new assessment, inspect ingestion results,
            generate architecture diagrams, and (soon) view portfolio
            and TCO insights.
          </div>
        </div>

        {/* Main grid: left = assessment/diagrams, right = status/roadmap */}
        <div style={gridStyle}>
          {/* Left: primary actions */}
          <div style={cardStyle}>
            <div style={sectionTitleStyle}>Start or Continue an Assessment</div>
            <div style={sectionSubStyle}>
              This is the Phase A/B entry point into CloudReadyAI:
              ingestion, analysis, diagrams, and (later) portfolio +
              financial outputs.
            </div>

            <div style={buttonRowStyle}>
              <button
                style={primaryButtonStyle}
                type="button"
                // In the future this will route to a "new assessment" wizard
                onClick={() =>
                  alert(
                    "New Assessment wizard will live here (Phase B3/C). For now, ingest data via API and explore diagrams."
                  )
                }
              >
                New Assessment (coming soon)
              </button>
              <button
                style={secondaryButtonStyle}
                type="button"
                onClick={() =>
                  alert(
                    "Run explorer UI will live here once /v1/runs is wired into the frontend."
                  )
                }
              >
                View Existing Runs (coming soon)
              </button>
            </div>

            <div style={smallTextStyle}>
              Under the hood this ties into:
              <br />
              <span style={{ fontFamily: "monospace" }}>
                /v1/runs, /v1/runs/summary, /v1/runs/problems,
                /v1/runs/analysis
              </span>
              . These APIs are already live; the UI will catch up in
              Phase B3/C.
            </div>
          </div>

          {/* Right: quick status */}
          <div style={cardStyle}>
            <div style={sectionTitleStyle}>Platform Status</div>
            <div style={sectionSubStyle}>
              High-level view of what&apos;s wired in today vs what&apos;s
              planned next in the roadmap.
            </div>

            <ul
              style={{
                paddingLeft: "18px",
                margin: 0,
                fontSize: "12px",
                lineHeight: 1.6,
                color: "#d1d5db",
              }}
            >
              <li>Phase A foundation: backend + diagrams UI ✅</li>
              <li>Phase B ingestion engine: servers, storage, network ✅</li>
              <li>
                Phase C analysis: initial metrics &amp; risk flags (API) ✅
              </li>
              <li>Phase B3 portfolio UI: not yet surfaced in frontend ⏳</li>
              <li>Phase D cost/TCO UI: planned but not visible yet ⏳</li>
            </ul>

            <div style={{ ...smallTextStyle, marginTop: "12px" }}>
              You can already hit the ingestion and analysis endpoints
              directly from scripts or Postman today. The UI will
              progressively expose those capabilities in upcoming phases.
            </div>
          </div>
        </div>

        {/* Lower cards: portfolio / TCO / diagrams */}
        <div style={{ marginTop: "18px" }}>
          <div style={threeColGridStyle}>
            {/* Portfolio Overview */}
            <div style={cardStyle}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <div style={sectionTitleStyle}>Portfolio Overview</div>
                <span style={badgeStyle}>Phase B3</span>
              </div>
              <div style={sectionSubStyle}>
                Apps, servers, storage, networks; summarized per run.
              </div>
              <p style={smallTextStyle}>
                Will surface:
                <br />
                • Application inventory and environments
                <br />
                • Server counts, OS mix, storage totals
                <br />
                • High-level risk indicators and wave planning
              </p>
              <button
                style={secondaryButtonStyle}
                type="button"
                onClick={() =>
                  alert(
                    "Portfolio UI will use /v1/runs/summary and /v1/runs/analysis for each run."
                  )
                }
              >
                View Portfolio (coming soon)
              </button>
            </div>

            {/* Cost & TCO */}
            <div style={cardStyle}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <div style={sectionTitleStyle}>Cost &amp; TCO</div>
                <span style={badgeStyle}>Phase D</span>
              </div>
              <div style={sectionSubStyle}>
                Baseline vs right-sized vs reserved, per scenario.
              </div>
              <p style={smallTextStyle}>
                Will surface:
                <br />
                • Monthly &amp; annual cost by scenario
                <br />
                • Delta between baseline and optimized
                <br />
                • Inputs used (pricing tables, sizing assumptions)
              </p>
              <button
                style={secondaryButtonStyle}
                type="button"
                onClick={() =>
                  alert(
                    "Cost/TCO screen will call the Phase D financial engine and show scenario comparisons."
                  )
                }
              >
                Open Cost View (coming soon)
              </button>
            </div>

            {/* Diagrams / Architecture */}
            <div style={cardStyle}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <div style={sectionTitleStyle}>Architecture Diagrams</div>
                <span style={badgeStyle}>Phase 7B/7E</span>
              </div>
              <div style={sectionSubStyle}>
                Generate draw.io-compatible cloud architectures with
                FedRAMP/DoD overlays.
              </div>
              <p style={smallTextStyle}>
                Uses:
                <br />
                • <span style={{ fontFamily: "monospace" }}>/v1/diagram/generate</span>
                <br />
                • <span style={{ fontFamily: "monospace" }}>/v1/diagram/package</span>
                <br />
                • Zero Trust and compliance overlays (Phase 7E)
              </p>
              <Link to="/diagrams" style={primaryButtonStyle}>
                Open Diagram Generator
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
