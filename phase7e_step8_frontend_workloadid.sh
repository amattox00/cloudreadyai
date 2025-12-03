#!/usr/bin/env bash
set -euo pipefail

echo "==[ Step 8: Add Workload ID input to Diagrams UI and pass to /diagram/generate_v2 ]=="

cd ~/cloudreadyai/frontend

# 0) Locate the diagrams page
if [[ -f "src/pages/DiagramsPage.tsx" ]]; then
  DIAGRAM_PAGE="src/pages/DiagramsPage.tsx"
elif [[ -f "src/pages/diagrams.tsx" ]]; then
  DIAGRAM_PAGE="src/pages/diagrams.tsx"
else
  echo "ERROR: Could not find diagrams page (src/pages/DiagramsPage.tsx or src/pages/diagrams.tsx)."
  exit 1
fi

echo "Using diagrams page: $DIAGRAM_PAGE"

# 1) Add workloadId state if not present
if ! grep -q "workloadId" "$DIAGRAM_PAGE"; then
  echo "Adding workloadId state to $DIAGRAM_PAGE"
  perl -0pi -e 's/(const \[environment, setEnvironment\][^;]*;\s*\n)/$1  const [workloadId, setWorkloadId] = useState<string>("");\n/' "$DIAGRAM_PAGE"
else
  echo "workloadId state already present. Skipping state insertion."
fi

# 2) Update handleGenerateDiagramV2 body to include workload_id: workloadId || null
if grep -q 'body: JSON.stringify({' "$DIAGRAM_PAGE"; then
  echo "Updating handleGenerateDiagramV2 body payload to use workloadId."
  perl -0pi -e 's/body: JSON.stringify\(\{\s*workload_id: null,\s*detail_level: "detailed",\s*\}\),/body: JSON.stringify({\n          workload_id: workloadId || null,\n          detail_level: "detailed",\n        }),/g' "$DIAGRAM_PAGE"
else
  echo "WARNING: Could not find existing body: JSON.stringify({ workload_id: null, ... }). You may need to adjust manually."
fi

# 3) Add a Workload ID input in the Diagram Generator 2.0 block
if ! grep -q "Workload ID" "$DIAGRAM_PAGE"; then
  echo "Adding Workload ID input to Diagram Generator 2.0 block."
  perl -0pi -e 's/(<div style=\{\{ marginTop: "2rem" \}\}>\s*\n\s*<h2>Diagram Generator 2\.0<\/h2>)/$1\n        <div style={{ marginTop: "0.5rem", marginBottom: "0.5rem" }}>\n          <label htmlFor="workload-id-input" style={{ marginRight: "0.5rem" }}>\n            Workload ID (optional):\n          </label>\n          <input\n            id="workload-id-input"\n            type="text"\n            value={workloadId}\n            onChange={(e) => setWorkloadId(e.target.value)}\n            placeholder="e.g. wl-sample-3tier-001"\n            style={{ padding: "0.25rem 0.5rem", minWidth: "260px" }}\n          />\n        </div>/;' "$DIAGRAM_PAGE"
else
  echo "Workload ID input already present. Skipping input insertion."
fi

echo "✅ Step 8 updates applied to $DIAGRAM_PAGE"

