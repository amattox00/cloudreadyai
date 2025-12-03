#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/generate_diagrams.sh TEST
#
# This will:
#   - Call /v1/diagrams/generate for AWS/Azure/GCP
#   - For multiple diagram types + view modes
#   - Decode xml_base64 into .drawio files under diagrams_out/

RUN_ID="${1:-}"
if [[ -z "$RUN_ID" ]]; then
  echo "Usage: $0 <RUN_ID>"
  exit 1
fi

OUT_DIR="diagrams_out/${RUN_ID}"
mkdir -p "${OUT_DIR}"

BASE_URL="http://localhost:8000/v1/diagrams/generate"

# You can trim this list if it feels like too much.
CLOUDS=("aws" "azure" "gcp")
DIAGRAM_TYPES=("app_topology" "network_security" "data_db")
VIEW_MODES=("source_and_target" "source_only" "target_only")

echo "Generating diagrams for RUN_ID=${RUN_ID}"
echo "Output dir: ${OUT_DIR}"
echo

for cloud in "${CLOUDS[@]}"; do
  for dtype in "${DIAGRAM_TYPES[@]}"; do
    for vmode in "${VIEW_MODES[@]}"; do
      echo ">>> ${cloud} | ${dtype} | ${vmode}"

      # JSON path
      json_file="${OUT_DIR}/${RUN_ID}_${cloud}_${dtype}_${vmode}.json"

      # Call API
      curl -sS -X POST "${BASE_URL}" \
        -H "Content-Type: application/json" \
        -d "{
          \"run_id\": \"${RUN_ID}\",
          \"cloud\": \"${cloud}\",
          \"diagram_type\": \"${dtype}\",
          \"view_mode\": \"${vmode}\"
        }" > "${json_file}"

      # Decode base64 into .drawio using python3
      python3 - << PY
import json, base64, os, sys

json_path = "${json_file}"
out_dir = os.path.dirname(json_path)

with open(json_path, "r") as f:
    try:
        data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[WARN] Failed to parse JSON in {json_path}: {e}", file=sys.stderr)
        sys.exit(0)

xml_b64 = data.get("xml_base64")
if not xml_b64:
    print(f"[WARN] No xml_base64 in {json_path}", file=sys.stderr)
    sys.exit(0)

filename = data.get("filename")
if not filename:
    # Fallback predictable name
    filename = os.path.basename(json_path).replace(".json", ".drawio")

out_path = os.path.join(out_dir, filename)

xml_bytes = base64.b64decode(xml_b64)
with open(out_path, "wb") as out:
    out.write(xml_bytes)

print(f"[OK] Wrote {out_path}")
PY

      echo
    done
  done
done

echo "All done. Files are under: ${OUT_DIR}"
