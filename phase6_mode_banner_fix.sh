#!/usr/bin/env bash
set -euo pipefail

echo "==[ Phase 6 – Fix Cloud Intelligence Mode Banner wiring ]=="

FRONTEND_DIR="$HOME/cloudreadyai/frontend"
cd "$FRONTEND_DIR"

DIAGRAM_PAGE="src/pages/DiagramsPage.tsx"

if [[ ! -f "$DIAGRAM_PAGE" ]]; then
  echo "ERROR: $DIAGRAM_PAGE not found."
  exit 1
fi

echo "Using diagrams page: $DIAGRAM_PAGE"

########################################
# 1) Ensure useEffect is imported
########################################
if grep -q 'import React, { useState } from "react";' "$DIAGRAM_PAGE"; then
  echo "Updating React import to include useEffect..."
  sed -i 's/import React, { useState } from "react";/import React, { useState, useEffect } from "react";/' "$DIAGRAM_PAGE"
else
  echo "React import line not in expected format; leaving as-is."
fi

########################################
# 2) Add CloudIntelligenceModeBanner import
########################################
if grep -q 'CloudIntelligenceModeBanner' "$DIAGRAM_PAGE"; then
  echo "CloudIntelligenceModeBanner import already present. Skipping."
else
  echo "Inserting CloudIntelligenceModeBanner import..."
  sed -i '/import React.*from "react";/a import { CloudIntelligenceModeBanner } from "../components/CloudIntelligenceModeBanner";' "$DIAGRAM_PAGE"
fi

########################################
# 3) Inject JSX into the component return
########################################
if grep -q 'CloudIntelligenceModeBanner' "$DIAGRAM_PAGE" && grep -q 'CloudIntelligenceModeBanner' "$DIAGRAM_PAGE" && grep -q 'CloudIntelligenceModeBanner' "$DIAGRAM_PAGE"; then
  : # no-op, just here to keep structure tidy
fi

if grep -q 'CloudIntelligenceModeBanner' "$DIAGRAM_PAGE" && grep -q '<CloudIntelligenceModeBanner' "$DIAGRAM_PAGE"; then
  echo "CloudIntelligenceModeBanner JSX already present. Skipping."
else
  echo "Injecting <CloudIntelligenceModeBanner /> into JSX..."
  # Insert after the first 'return (' only
  sed -i '0,/return (/s//return (\n    <CloudIntelligenceModeBanner \\/>/' "$DIAGRAM_PAGE"
fi

echo "Phase 6 mode banner fix completed."
