#!/usr/bin/env bash
set -euo pipefail

echo "==[ Step 6: Hook frontend Diagrams UI to /v1/diagram/generate_v2 ]=="

cd ~/cloudreadyai/frontend

# 0) Optional: show where DiagramsPage.tsx lives
if [[ -f "src/pages/DiagramsPage.tsx" ]]; then
  DIAGRAM_PAGE="src/pages/DiagramsPage.tsx"
elif [[ -f "src/pages/diagrams.tsx" ]]; then
  DIAGRAM_PAGE="src/pages/diagrams.tsx"
else
  echo "ERROR: Could not find Diagrams page (src/pages/DiagramsPage.tsx or src/pages/diagrams.tsx)."
  exit 1
fi

echo "Using diagrams page: $DIAGRAM_PAGE"

# 1) Ensure we have a placeholder for storing XML or status
if ! grep -q "const \\[diagramXml" "$DIAGRAM_PAGE"; then
  echo "Adding diagramXml state to $DIAGRAM_PAGE"
  # Insert diagramXml state after the existing React useState declarations
  perl -0pi -e 's/(useState<DiagramType>\("landing_zone"\);\s*\n\s*const \[orgName.*?;\n)/$1  const [diagramXml, setDiagramXml] = useState<string | null>(null);\n  const [isGeneratingV2, setIsGeneratingV2] = useState(false);\n\n/' "$DIAGRAM_PAGE"
else
  echo "diagramXml state already present (or similar). Skipping insertion."
fi

# 2) Add a handler function to call the new backend endpoint
if ! grep -q "handleGenerateDiagramV2" "$DIAGRAM_PAGE"; then
  echo "Adding handleGenerateDiagramV2 to $DIAGRAM_PAGE"
  cat >> "$DIAGRAM_PAGE" << 'TSAPPEND'

  async function handleGenerateDiagramV2() {
    try {
      setIsGeneratingV2(true);
      setDiagramXml(null);

      const resp = await fetch("/v1/diagram/generate_v2", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          workload_id: null,
          detail_level: "detailed",
        }),
      });

      if (!resp.ok) {
        const text = await resp.text();
        console.error("Diagram v2 error:", resp.status, text);
        alert("Diagram v2 generation failed: " + resp.status);
        return;
      }

      const data = await resp.json();
      if (data && data.xml) {
        setDiagramXml(data.xml);
      } else {
        alert("Diagram v2 generation succeeded but response was missing XML.");
      }
    } catch (err) {
      console.error("Diagram v2 error:", err);
      alert("Diagram v2 generation error (see console).");
    } finally {
      setIsGeneratingV2(false);
    }
  }
TSAPPEND
else
  echo "handleGenerateDiagramV2 already present. Skipping insertion."
fi

# 3) Add a button to trigger the new handler, and a simple debug preview
if ! grep -q "Generate Diagram v2" "$DIAGRAM_PAGE"; then
  echo "Adding 'Generate Diagram v2' button and XML preview block."

  # This is a bit heuristic: append a small UI block near bottom of component JSX.
  # We'll just append at end of file inside the main component's JSX container comment.
  cat >> "$DIAGRAM_PAGE" << 'JSAPPEND'

      {/* Diagram Generator 2.0 (backend /v1/diagram/generate_v2) */}
      <div style={{ marginTop: "2rem" }}>
        <h2>Diagram Generator 2.0</h2>
        <button
          onClick={handleGenerateDiagramV2}
          disabled={isGeneratingV2}
          style={{ padding: "0.5rem 1rem", marginRight: "1rem" }}
        >
          {isGeneratingV2 ? "Generating..." : "Generate Diagram v2"}
        </button>

        {diagramXml && (
          <details style={{ marginTop: "1rem" }}>
            <summary>Show raw draw.io XML (debug)</summary>
            <textarea
              readOnly
              style={{ width: "100%", height: "200px", marginTop: "0.5rem" }}
              value={diagramXml}
            />
          </details>
        )}
      </div>
JSAPPEND
else
  echo "'Generate Diagram v2' block already present. Skipping insertion."
fi

echo "✅ Step 6 updates applied to $DIAGRAM_PAGE"

