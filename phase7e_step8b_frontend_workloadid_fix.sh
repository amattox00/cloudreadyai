#!/usr/bin/env bash
set -euo pipefail

echo "==[ Step 8b: Auto-insert Workload ID input into Diagrams UI ]=="

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

python3 - << 'PY'
from pathlib import Path

path = Path("src/pages/DiagramsPage.tsx")
text = path.read_text()

marker = '  <h2>Diagram Generator 2.0</h2>'
insert_block = '''  <h2>Diagram Generator 2.0</h2>
  <div style={{ marginTop: "0.5rem", marginBottom: "0.5rem" }}>
    <label htmlFor="workload-id-input" style={{ marginRight: "0.5rem" }}>
      Workload ID (optional):
    </label>
    <input
      id="workload-id-input"
      type="text"
      value={workloadId}
      onChange={(e) => setWorkloadId(e.target.value)}
      placeholder="e.g. wl-sample-3tier-001"
      style={{ padding: "0.25rem 0.5rem", minWidth: "260px" }}
    />
  </div>'''

if 'workload-id-input' in text:
    print("Workload ID input already present; no changes made.")
else:
    if marker not in text:
        raise SystemExit("ERROR: Could not find Diagram Generator 2.0 <h2> marker in file.")
    text = text.replace(marker, insert_block)
    path.write_text(text)
    print("Inserted Workload ID input under Diagram Generator 2.0 heading.")
PY

echo "✅ Step 8b completed."
