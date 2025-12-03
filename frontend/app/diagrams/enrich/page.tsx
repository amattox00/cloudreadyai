"use client";

import React, { useState } from "react";
import { DiagramPreview } from "@/components/diagram/DiagramPreview";
import { enrichDiagram, DiagramMetadata, DiagramEnrichResponse } from "@/lib/api/diagram";

const defaultXml = `<mxfile><diagram id="cloud-diagram" name="Cloud Diagram"><mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel></diagram></mxfile>`;

const defaultMetadata: DiagramMetadata = {
  cloud: "aws",
  use_case: "landing_zone",
  compliance: "dod",
  environment: "Prod",
  org_name: "5NINE Data Solutions",
  workload_name: "CloudReadyAI",
};

export default function DiagramEnrichPage() {
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
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Phase 7E – AI-driven Diagram Enrichment</h1>

      <div className="flex flex-col gap-4 md:flex-row">
        <div className="md:w-1/2 space-y-2">
          <label className="font-medium">Input / Enriched XML</label>
          <textarea
            className="w-full h-72 border rounded p-2 text-xs font-mono"
            value={xml}
            onChange={(e) => setXml(e.target.value)}
          />
          <button
            onClick={handleEnrich}
            disabled={loading}
            className="px-4 py-2 rounded border text-sm disabled:opacity-60"
          >
            {loading ? "Enriching..." : "Run Phase 7E Enrichment"}
          </button>
          {error && <p className="text-red-600 text-sm mt-1">{error}</p>}
        </div>

        <div className="md:w-1/2">
          <DiagramPreview xml={xml} />
        </div>
      </div>

      {response?.recommendations?.length ? (
        <div className="mt-4">
          <h2 className="text-xl font-semibold mb-2">Recommendations</h2>
          <ul className="space-y-2">
            {response.recommendations.map((r, idx) => (
              <li key={idx} className="border rounded p-2 text-sm">
                <div className="flex justify-between items-center">
                  <span className="font-semibold">{r.title}</span>
                  <span className="text-xs uppercase tracking-wide">{r.severity}</span>
                </div>
                <p className="text-xs mt-1">{r.description}</p>
                {r.tags?.length ? (
                  <div className="mt-1 flex flex-wrap gap-1">
                    {r.tags.map((tag) => (
                      <span
                        key={tag}
                        className="text-[10px] px-2 py-0.5 border rounded-full"
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
}
