import React, { useState } from "react";

type CloudProvider = "aws";
type DiagramType = "app_topology";
type DiagramViewMode = "full" | "source" | "target" | "source_and_target";

interface GenerateResponse {
  filename: string;
  xml_base64: string;
}

export default function DiagramsPage() {
  const [runId, setRunId] = useState("TEST");
  const [cloud, setCloud] = useState<CloudProvider>("aws");
  const [diagramType, setDiagramType] = useState<DiagramType>("app_topology");
  const [viewMode, setViewMode] = useState<DiagramViewMode>("full");

  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);
  const [lastGeneratedFile, setLastGeneratedFile] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  function buildPayload() {
    return {
      run_id: runId || "TEST",
      cloud,
      diagram_type: diagramType,
      view_mode: viewMode,
    };
  }

  async function callGenerateEndpoint(): Promise<GenerateResponse> {
    const payload = buildPayload();

    const res = await fetch("/v1/diagrams/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      // Try to grab plain text (502 HTML, validation error, etc.)
      const text = await res.text();
      throw new Error(`Backend returned ${res.status}: ${text}`);
    }

    const json = (await res.json()) as GenerateResponse;
    if (!json.filename || !json.xml_base64) {
      throw new Error("Backend response missing filename or xml_base64");
    }

    return json;
  }

  async function handleGeneratePreview() {
    setIsLoading(true);
    setStatusMessage(null);
    setStatusError(null);

    try {
      const resp = await callGenerateEndpoint();
      setLastGeneratedFile(resp.filename);
      setStatusMessage(
        `Successfully generated diagram: ${resp.filename}. Open the .drawio file in draw.io / diagrams.net to preview the AWS architecture diagram.`
      );
    } catch (err: any) {
      console.error(err);
      setStatusError(String(err?.message || err));
    } finally {
      setIsLoading(false);
    }
  }

  async function handleDownloadDrawio() {
    setIsLoading(true);
    setStatusMessage(null);
    setStatusError(null);

    try {
      const resp = await callGenerateEndpoint();
      setLastGeneratedFile(resp.filename);

      const xmlBytes = Uint8Array.from(atob(resp.xml_base64), (c) =>
        c.charCodeAt(0)
      );
      const blob = new Blob([xmlBytes], { type: "application/xml" });

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = resp.filename || "cloudreadyai_diagram.drawio";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      setStatusMessage(
        `Downloaded draw.io file: ${resp.filename}. Open it in draw.io / diagrams.net to view the full AWS architecture diagram.`
      );
    } catch (err: any) {
      console.error(err);
      setStatusError(String(err?.message || err));
    } finally {
      setIsLoading(false);
    }
  }

  function handleDownloadPdf() {
    // Not wired yet to the new backend path.
    // Keeping the button visible but explaining the limitation.
    setStatusError(
      "PDF export is not wired to the new /v1/diagrams/generate endpoint yet. Download the .drawio file and export to PDF from draw.io / diagrams.net."
    );
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-semibold mb-2">Diagrams</h1>
      <p className="text-sm text-gray-600 mb-6">
        Generate architect-grade AWS diagrams from your CloudReadyAI runs.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Form */}
        <div className="border rounded-xl shadow-sm bg-white p-6 space-y-4">
          <h2 className="text-lg font-semibold mb-2">Diagram Settings</h2>

          {/* Run ID */}
          <div className="space-y-1">
            <label className="text-sm font-medium">Run ID</label>
            <input
              className="w-full border rounded-md px-3 py-2 text-sm"
              value={runId}
              onChange={(e) => setRunId(e.target.value)}
              placeholder="TEST"
            />
          </div>

          {/* Cloud */}
          <div className="space-y-1">
            <label className="text-sm font-medium">Cloud</label>
            <select
              className="w-full border rounded-md px-3 py-2 text-sm"
              value={cloud}
              onChange={(e) => setCloud(e.target.value as CloudProvider)}
            >
              <option value="aws">AWS</option>
            </select>
          </div>

          {/* Diagram Type */}
          <div className="space-y-1">
            <label className="text-sm font-medium">Diagram Type</label>
            <select
              className="w-full border rounded-md px-3 py-2 text-sm"
              value={diagramType}
              onChange={(e) =>
                setDiagramType(e.target.value as DiagramType)
              }
            >
              <option value="app_topology">Application Topology</option>
            </select>
          </div>

          {/* View Mode */}
          <div className="space-y-1">
            <label className="text-sm font-medium">
              View Mode{" "}
              <span className="text-xs text-gray-500">
                (for AWS app topology, &quot;Full Application Topology&quot; is
                recommended)
              </span>
            </label>
            <select
              className="w-full border rounded-md px-3 py-2 text-sm"
              value={viewMode}
              onChange={(e) =>
                setViewMode(e.target.value as DiagramViewMode)
              }
            >
              <option value="full">
                Full Application Topology (Recommended)
              </option>
              <option value="source">Current / Source Only</option>
              <option value="target">Target AWS Only</option>
              <option value="source_and_target">
                Side-by-side Source &amp; Target
              </option>
            </select>
          </div>

          {/* Buttons */}
          <div className="flex flex-wrap gap-3 pt-2">
            <button
              type="button"
              onClick={handleGeneratePreview}
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-md disabled:opacity-60"
            >
              {isLoading ? "Working..." : "Generate Preview"}
            </button>

            <button
              type="button"
              onClick={handleDownloadDrawio}
              disabled={isLoading}
              className="border border-gray-300 text-sm font-medium px-4 py-2 rounded-md bg-white hover:bg-gray-50 disabled:opacity-60"
            >
              Download Draw.io
            </button>

            <button
              type="button"
              onClick={handleDownloadPdf}
              disabled={isLoading}
              className="border border-gray-300 text-sm font-medium px-4 py-2 rounded-md bg-white hover:bg-gray-50 disabled:opacity-60"
            >
              Download PDF
            </button>
          </div>
        </div>

        {/* Right: Status */}
        <div className="border rounded-xl shadow-sm bg-white p-6 space-y-4">
          <h2 className="text-lg font-semibold mb-2">Status</h2>

          {statusError && (
            <div className="text-xs bg-red-50 border border-red-200 text-red-700 rounded-md p-3 whitespace-pre-wrap max-h-72 overflow-auto">
              {statusError}
            </div>
          )}

          {statusMessage && !statusError && (
            <div className="text-sm bg-green-50 border border-green-200 text-green-700 rounded-md p-3">
              {statusMessage}
            </div>
          )}

          {!statusMessage && !statusError && (
            <p className="text-sm text-gray-500">
              No diagram generated yet. Click{" "}
              <span className="font-medium">Generate Preview</span> or{" "}
              <span className="font-medium">Download Draw.io</span> to generate
              an AWS architecture diagram.
            </p>
          )}

          <div className="pt-4 border-t mt-4">
            <h3 className="text-sm font-semibold mb-1">Last generated file:</h3>
            {lastGeneratedFile ? (
              <p className="text-sm">{lastGeneratedFile}</p>
            ) : (
              <p className="text-sm text-gray-500">
                No diagram generated yet.
              </p>
            )}
            <p className="text-xs text-gray-500 mt-2">
              After generating, open the <code>.drawio</code> file in{" "}
              <span className="font-mono">draw.io</span> /{" "}
              <span className="font-mono">diagrams.net</span> to see the full
              AWS architecture diagram.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
