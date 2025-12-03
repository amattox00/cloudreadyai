import React, { useState } from "react";
import { DiagramPreview } from "../../components/diagram/DiagramPreview";
import {
  enrichDiagram,
  DiagramMetadata,
  DiagramEnrichResponse,
} from "../../lib/api/diagram";

const defaultXml = `<mxfile><diagram id="cloud-diagram" name="Cloud Diagram"><mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel></diagram></mxfile>`;

const defaultMetadata: DiagramMetadata = {
  cloud: "aws",
  use_case: "landing_zone",
  compliance: "dod",
  environment: "Prod",
  org_name: "5NINE Data Solutions",
  workload_name: "CloudReadyAI",
};

const Phase7EEnrichPanel: React.FC = () => {
  const [xml, setXml] = useState<string>(defaultXml);
  const [response, setResponse] = useState<DiagramEnrichResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleEnrich = async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await enrichDiagram({
        xml,
        metadata: defaultMetadata,
        enable_auto_layout: true,
        enable_zero_trust: true,
        include_recommendations: true,
      });
      setResponse(resp);
      setXml(resp.xml);
    } catch (err: any) {
      setError(err.message || "Failed to enrich diagram");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 style={{ fontSize: "1.4rem", marginBottom: "0.5rem" }}>
        Phase 7E – AI-driven Diagram Enrichment
      </h2>
      <p style={{ marginBottom: "1rem", fontSize: "0.9rem" }}>
        Paste diagram XML (e.g., generated from Phase 7B), then enrich it with
        CSP auto-layout, Zero Trust overlays, and architecture recommendations.
      </p>

      <div style={{ display: "flex", flexDirection: "row", gap: "1rem", alignItems: "flex-start" }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <label style={{ display: "block", fontWeight: 600, marginBottom: "0.25rem" }}>
            Input / Enriched XML
          </label>
          <textarea
            style={{
              width: "100%",
              height: "18rem",
              border: "1px solid #ccc",
              borderRadius: "4px",
              padding: "0.5rem",
              fontFamily: "monospace",
              fontSize: "0.75rem",
            }}
            value={xml}
            onChange={(e) => setXml(e.target.value)}
          />
          <button
            onClick={handleEnrich}
            disabled={loading}
            style={{
              marginTop: "0.5rem",
              padding: "0.5rem 1rem",
              borderRadius: "4px",
              border: "1px solid #ccc",
              background: "#f5f5f5",
              cursor: loading ? "wait" : "pointer",
            }}
          >
            {loading ? "Enriching..." : "Run Phase 7E Enrichment"}
          </button>
          {error && (
            <p style={{ color: "red", fontSize: "0.8rem", marginTop: "0.25rem" }}>
              {error}
            </p>
          )}
        </div>

        <div style={{ flex: 1, minWidth: 0 }}>
          <DiagramPreview xml={xml} />
        </div>
      </div>

      {response?.recommendations?.length ? (
        <div style={{ marginTop: "1rem" }}>
          <h3 style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>
            Recommendations
          </h3>
          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {response.recommendations.map((r, idx) => (
              <li
                key={idx}
                style={{
                  border: "1px solid #ddd",
                  borderRadius: "4px",
                  padding: "0.5rem",
                  marginBottom: "0.5rem",
                  fontSize: "0.85rem",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    marginBottom: "0.25rem",
                  }}
                >
                  <span style={{ fontWeight: 600 }}>{r.title}</span>
                  <span
                    style={{
                      fontSize: "0.7rem",
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                    }}
                  >
                    {r.severity}
                  </span>
                </div>
                <p style={{ margin: 0 }}>{r.description}</p>
                {r.tags?.length ? (
                  <div
                    style={{
                      marginTop: "0.25rem",
                      display: "flex",
                      flexWrap: "wrap",
                      gap: "0.25rem",
                    }}
                  >
                    {r.tags.map((tag) => (
                      <span
                        key={tag}
                        style={{
                          fontSize: "0.7rem",
                          padding: "0.1rem 0.4rem",
                          borderRadius: "999px",
                          border: "1px solid #ccc",
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                ) : null}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
};

export default Phase7EEnrichPanel;
